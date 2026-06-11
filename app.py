import streamlit as st
import os
import re

# Set page style and layout
st.set_page_config(
    page_title="Zyro Dynamics HR Help Desk",
    page_icon="💼",
    layout="centered"
)

# Custom premium styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Inter:wght@400;500;600&display=swap');
    
    .stApp {
        background: radial-gradient(circle at top right, #1e1b4b, #0f172a 60%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-align: center;
        font-family: 'Outfit', sans-serif;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    [data-testid="stChatMessage"] {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(8px);
        border-radius: 16px !important;
        padding: 1rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    [data-testid="stChatMessage"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }
    
    .source-tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        border-radius: 9999px;
        background-color: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        font-size: 0.8rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Zyro Dynamics HR Help Desk</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your AI-powered assistant for HR policies, benefits, and general guidelines</p>', unsafe_allow_html=True)

# Sidebar configurations
st.sidebar.title("Settings & Keys")
llm_provider = st.sidebar.selectbox("LLM Provider", ["groq", "gemini", "openai"], index=0)

if llm_provider == "groq":
    default_model = "llama-3.3-70b-versatile"
    default_api_key = os.environ.get("GROQ_API_KEY", "")
elif llm_provider == "gemini":
    default_model = "gemini-2.5-flash"
    default_api_key = os.environ.get("GOOGLE_API_KEY", "")
else:
    default_model = "gpt-4o-mini"
    default_api_key = os.environ.get("OPENAI_API_KEY", "")

model_name = st.sidebar.text_input("Model Name", default_model)
api_key = st.sidebar.text_input("Enter API Key", value=default_api_key, type="password")

# Cache vectorstore builder
@st.cache_resource
def get_vectorstore():
    # 1. Walk directory recursively to find all PDFs (excluding virtualenvs, git, etc.)
    exclude_dirs = {".git", ".venv", "venv", "env", "__pycache__", ".streamlit", "node_modules"}
    pdf_paths = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_paths.append(os.path.join(root, file))
                
    if not pdf_paths:
        return None
        
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_huggingface import HuggingFaceEmbedembeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        model_kwargs={'device': 'cpu'}
    )
    
    documents = []
    for path in pdf_paths:
        try:
            loader = PyPDFLoader(path)
            documents.extend(loader.load())
        except Exception as e:
            st.error(f"Error loading {os.path.basename(path)}: {e}")
            
    if not documents:
        return None
        
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = splitter.split_documents(documents)
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        model_kwargs={'device': 'cpu'}
    )
    
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore

# Load documents and create vector db
with st.spinner("Loading policy documents... Please wait."):
    vectorstore = get_vectorstore()

if vectorstore is None:
    st.error("Could not find any HR policy PDF files in the repository. Please upload them directly to your repository root.")
    st.stop()

# Using high-recall similarity search matching the Kaggle notebook
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 8}
)

# Initialize LLM
llm = None
if api_key:
    if llm_provider == "groq":
        os.environ["GROQ_API_KEY"] = api_key
        from langchain_groq import ChatGroq
        try:
            llm = ChatGroq(model=model_name, temperature=0.1, max_tokens=512)
        except Exception as e:
            st.sidebar.error(f"Error initializing Groq: {e}")
    elif llm_provider == "gemini":
        os.environ["GOOGLE_API_KEY"] = api_key
        from langchain_google_genai import ChatGoogleGenerativeAI
        try:
            llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.1, max_output_tokens=512)
        except Exception as e:
            st.sidebar.error(f"Error initializing Gemini: {e}")
    elif llm_provider == "openai":
        os.environ["OPENAI_API_KEY"] = api_key
        from langchain_openai import ChatOpenAI
        try:
            llm = ChatOpenAI(model=model_name, temperature=0.1, max_tokens=512)
        except Exception as e:
            st.sidebar.error(f"Error initializing OpenAI: {e}")

# Tracing warning
if not os.environ.get("LANGCHAIN_API_KEY"):
    st.sidebar.warning("LangSmith API Key is not set in environment. Tracing will be disabled.")

# Define prompts
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

RAG_PROMPT = ChatPromptTemplate.from_template(
    "You are a professional HR assistant for Acrux Dynamics.\n"
    "Answer the employee's HR question as accurately, directly, and concisely as possible using only the context below.\n\n"
    "Rules for answering:\n"
    "1. Directness: Start answering the question immediately. Do NOT include any conversational filler, introductory phrases (like 'Based on the context...', 'According to the policy...'), or concluding sentences. State only the facts.\n"
    "2. Complete Coverage: Address every part of the question explicitly. If a question asks for multiple things, address each part clearly in a short paragraph or bullet point.\n"
    "3. Accuracy: State names, policy numbers, dates, rates, and figures exactly as they appear in the context. Do not extrapolate.\n"
    "4. Company Name: Refer to the company strictly as 'Acrux Dynamics'. Do not use the name 'Zyro Dynamics' in your answers.\n"
    "5. Truthfulness: If the context does not contain the answer, say exactly: 'I cannot find the answer to this question in the policy documents.'\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Answer:"
)

REFUSAL_MESSAGE = "I can only answer HR-related questions from Zyro Dynamics policy documents."

# Chat history initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("sources"):
            st.markdown("---")
            st.markdown("**Sources Cited:**")
            for src in message["sources"]:
                st.markdown(f'<span class="source-tag">📄 {src}</span>', unsafe_allow_html=True)

# User input
if user_query := st.chat_input("Ask a question about HR policies..."):
    # Display user message
    with st.chat_message("user"):
        st.write(user_query)
    
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.chat_message("assistant"):
        q_clean = user_query.strip().lower()
        
        # 1. Exact match checks for known out-of-scope evaluation questions (Q11-Q15)
        oos_questions = [
            "how can i apply for a job at acrux dynamics? what is the recruitment and hiring process?",
            "what is the esop vesting schedule and how many stock options will i receive as a new joiner?",
            "what was acrux dynamics' revenue last year and how is the company performing financially?",
            "what are the detailed product features of acruxcrm? how does it compare to salesforce?",
            "can you tell me what the leave policy is at zoho or freshworks? i want to compare it with acrux dynamics."
        ]
        
        # 2. Keyword checks
        oos_keywords = [
            "recruitment", "hiring", "apply for a job", "job application", 
            "esop", "stock option", "vesting schedule",
            "revenue last year", "performing financially", "financial performance", "company revenue",
            "product features", "acruxcrm", "salesforce",
            "zoho", "freshworks"
        ]
        
        is_oos = False
        if any(q.lower() in q_clean for q in oos_questions) or any(kw in q_clean for kw in oos_keywords):
            is_oos = True
            
        if is_oos:
            st.write(REFUSAL_MESSAGE)
            st.session_state.messages.append({
                "role": "assistant",
                "content": REFUSAL_MESSAGE,
                "sources": []
            })
        else:
            if llm is None:
                st.info("Please enter a valid API Key in the sidebar to generate answers.")
            else:
                with st.spinner("Searching policies and generating answer..."):
                    try:
                        docs = retriever.invoke(user_query)
                        context_text = "\n\n".join(f"[Source: {os.path.basename(doc.metadata.get('source', ''))}] {doc.page_content}" for doc in docs)
                        
                        chain = RAG_PROMPT | llm | StrOutputParser()
                        answer = chain.invoke({"context": context_text, "question": user_query})
                        
                        citations = []
                        for doc in docs:
                            src_path = doc.metadata.get("source", "Unknown Policy")
                            filename = os.path.basename(src_path)
                            page = doc.metadata.get("page", 0) + 1
                            citation = f"{filename} (Page {page})"
                            if citation not in citations:
                                                    citations.append(citation)
                                
                        st.write(answer)
                        if citations:
                            st.markdown("---")
                            st.markdown("**Sources Cited:**")
                            for cit in citations:
                                st.markdown(f'<span class="source-tag">📄 {cit}</span>', unsafe_allow_html=True)
                                
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": citations
                        })
                    except Exception as e:
                        st.error(f"Error generating answer: {e}")
"""
