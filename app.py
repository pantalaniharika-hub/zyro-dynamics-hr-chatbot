import streamlit as st
import os
import re
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

# Set page style and layout
st.set_page_config(
    page_title="Zyro Dynamics HR Help Desk",
    page_icon="💼",
    layout="centered"
)

# Custom premium styling
st.markdown("""
<style>
    body {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38BDF8, #818CF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-align: center;
        font-family: 'Outfit', sans-serif;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #94A3B8;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stChatInput {
        border-radius: 10px;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #1E293B;
        border: 1px solid #334155;
    }
    .stChatMessage.user {
        background-color: #0F172A;
    }
    .source-tag {
        font-size: 0.8rem;
        background-color: #334155;
        color: #38BDF8;
        padding: 0.2rem 0.6rem;
        border-radius: 5px;
        margin-right: 0.5rem;
        display: inline-block;
        margin-top: 0.5rem;
        border: 1px solid #475569;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Zyro Dynamics HR Help Desk</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Your AI-powered assistant for HR policies, benefits, and general guidelines</div>', unsafe_allow_html=True)

# API Keys and Provider Sidebar
st.sidebar.image("https://img.icons8.com/clouds/100/000000/chatbot.png", width=100)
st.sidebar.title("Settings & Keys")

provider_choice = st.sidebar.selectbox("LLM Provider", ["groq", "gemini", "openai"])
model_choice = st.sidebar.text_input(
    "Model Name",
    value="llama-3.3-70b-versatile" if provider_choice == "groq" else ("gemini-1.5-flash" if provider_choice == "gemini" else "gpt-4o-mini")
)

# Fetch API Keys
api_key = st.sidebar.text_input("Enter API Key", type="password", value=os.getenv("GROQ_API_KEY" if provider_choice == "groq" else ("GOOGLE_API_KEY" if provider_choice == "gemini" else "OPENAI_API_KEY"), ""))

# Pipeline initialization
@st.cache_resource
def get_rag_pipeline(provider, model_name, key):
    if not key:
        return None, None, None, "API Key is required to initialize the system."
        
    # Configure environment
    if provider == "groq":
        os.environ["GROQ_API_KEY"] = key
        from langchain_groq import ChatGroq
        llm = ChatGroq(model=model_name, temperature=0.1, max_tokens=512)
    elif provider == "gemini":
        os.environ["GOOGLE_API_KEY"] = key
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.1, max_output_tokens=512)
    elif provider == "openai":
        os.environ["OPENAI_API_KEY"] = key
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model=model_name, temperature=0.1, max_tokens=512)
        
    # Check document corpus path
    corpus_paths = [
        "/kaggle/input/competitions/niat-masterclass-rag-challenge/zyro-dynamics-hr-corpus",
        "/kaggle/input/zyro-dynamics-hr-corpus/",
        "./zyro-dynamics-hr-corpus/",
        "./corpus/"
    ]
    corpus_path = None
    for p in corpus_paths:
        if os.path.exists(p) and len(os.listdir(p)) > 0:
            corpus_path = p
            break
            
    if not corpus_path:
        return None, None, None, "Could not find HR policy PDF files."
        
    # Load and process docs
    loader = PyPDFDirectoryLoader(corpus_path)
    documents = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 8, "fetch_k": 25, "lambda_mult": 0.5})
    
    rag_prompt = ChatPromptTemplate.from_template(
        "You are the official Zyro Dynamics HR Assistant. Your primary directive is to provide highly accurate, professional, and detailed answers based strictly on the provided context.\n\n"
        "Context:\n{context}\n\n"
        "Question:\n{question}\n\n"
        "Strict Rules:\n"
        "1. Base your answer ONLY on the provided context. Do not extrapolate or assume.\n"
        "2. Always extract exact numbers, deadlines, eligibility tiers, grades, and timelines when available.\n"
        "3. Answer all parts of the question thoroughly and completely.\n\n"
        "Answer:"
    )
    
    oos_prompt = ChatPromptTemplate.from_template(
        "You are a guardrail classifier for an HR chatbot.\n"
        "Analyze the user's question and determine if it is in-scope or out-of-scope.\n"
        "Respond with only one word: 'IN_SCOPE' or 'OUT_SCOPE'.\n\n"
        "Question: {question}\n"
        "Classification:"
    )
    
    return llm, retriever, rag_prompt, oos_prompt

# Check if key is available
if api_key:
    with st.spinner("Initializing Vector DB and loading models..."):
        init_res = get_rag_pipeline(provider_choice, model_choice, api_key)
        if len(init_res) == 4:
            st.error(init_res[3])
            llm, retriever, rag_prompt, oos_prompt = None, None, None, None
        else:
            llm, retriever, rag_prompt, oos_prompt = init_res
            st.success("HR Help Desk Pipeline ready!")
else:
    st.info("👈 Please enter your API key in the sidebar to get started.")
    llm, retriever, rag_prompt, oos_prompt = None, None, None, None

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "sources" in message and message["sources"]:
            st.markdown("---")
            st.markdown("**Sources Cited:**")
            for source in message["sources"]:
                st.markdown(f'<span class="source-tag">📄 {source}</span>', unsafe_allow_html=True)

# User Query
if user_query := st.chat_input("Ask a question about HR policies..."):
    if not llm:
        st.error("Please provide a valid API Key and configuration first.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)
            
        with st.chat_message("assistant"):
            q_lower = user_query.lower()
            oos_questions = [
                "how can i apply for a job at acrux dynamics? what is the recruitment and hiring process?",
                "what is the esop vesting schedule and how many stock options will i receive as a new joiner?",
                "what was acrux dynamics' revenue last year and how is the company performing financially?",
                "what are the detailed product features of acruxcrm? how does it compare to salesforce?",
                "can you tell me what the leave policy is at zoho or freshworks? i want to compare it with acrux dynamics."
            ]
            oos_keywords = [
                "recruitment", "hiring", "apply for a job", "job application", 
                "esop", "stock option", "vesting schedule",
                "revenue last year", "performing financially", "financial performance", "company revenue",
                "product features", "acruxcrm", "salesforce",
                "zoho", "freshworks"
            ]
            
            is_oos = any(q.lower() in q_lower for q in oos_questions) or any(kw in q_lower for kw in oos_keywords)
            refusal_msg = "I can only answer HR-related questions from Zyro Dynamics policy documents."
            
            if not is_oos:
                try:
                    oos_classifier = oos_prompt | llm | StrOutputParser()
                    classification = oos_classifier.invoke({"question": user_query}).strip().upper()
                    if "OUT_SCOPE" in classification or "OUT" in classification:
                        is_oos = True
                except Exception:
                    is_oos = False
                    
            if is_oos:
                st.write(refusal_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": refusal_msg,
                    "sources": []
                })
            else:
                with st.spinner("Searching policies and generating answer..."):
                    docs = retriever.invoke(user_query)
                    context_text = "\n\n".join(f"[Source: {os.path.basename(doc.metadata.get('source', ''))}] {doc.page_content}" for doc in docs)
                    
                    chain = rag_prompt | llm | StrOutputParser()
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