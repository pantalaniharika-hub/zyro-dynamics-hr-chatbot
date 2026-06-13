import streamlit as st
import os
import re
import time
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Zyro Dynamics - Executive HR Help Desk",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling (CSS injection)
st.markdown("""
<style>
    /* Google Fonts import */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Apply styles globally */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main app container dark background styling */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #101524 0%, #070a13 90%);
        color: #e2e8f0;
    }
    
    /* Header styling with gradient */
    .header-title {
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.1rem;
        letter-spacing: -0.06rem;
        font-family: 'Outfit', sans-serif;
    }
    
    .header-subtitle {
        color: #94a3b8;
        font-size: 1.2rem;
        margin-bottom: 2.5rem;
        font-weight: 300;
        letter-spacing: 0.02rem;
    }
    
    /* Sidebar premium dark style */
    section[data-testid="stSidebar"] {
        background-color: #080c16 !important;
        border-right: 1px solid #1e293b;
    }
    
    /* Glassmorphic cards for highlights */
    .glass-card {
        background: rgba(17, 24, 39, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(96, 165, 250, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(96, 165, 250, 0.1);
    }
    
    .card-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.15rem;
        font-weight: 600;
        color: #60a5fa;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-text {
        font-size: 0.9rem;
        color: #cbd5e1;
        line-height: 1.5;
    }
    
    /* Input field customization */
    .stTextInput>div>div>input {
        background-color: #0f172a !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
    }
    .stTextInput>div>div>input:focus {
        border-color: #60a5fa !important;
        box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.2) !important;
    }
    
    /* Premium button styles */
    div.stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4) !important;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    }
    
    /* Pill button styling for suggested questions */
    .suggested-pill {
        display: inline-block;
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid #334155;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        font-size: 0.85rem;
        color: #94a3b8;
        cursor: pointer;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
        text-align: left;
    }
    .suggested-pill:hover {
        background: rgba(96, 165, 250, 0.1);
        border-color: #60a5fa;
        color: #60a5fa;
        transform: scale(1.02);
    }
    
    /* Doc citation tags */
    .doc-pill {
        display: inline-flex;
        align-items: center;
        background: rgba(167, 139, 250, 0.12);
        color: #c084fc;
        border: 1px solid rgba(167, 139, 250, 0.3);
        border-radius: 30px;
        padding: 0.25rem 0.75rem;
        font-size: 0.8rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
        margin-right: 6px;
        box-shadow: 0 0 8px #10b981;
    }
</style>
""", unsafe_allow_html=True)

# Main title display
st.markdown('<div class="header-title">Zyro Dynamics</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Executive HR Intelligence Portal & Policy Chatbot</div>', unsafe_allow_html=True)

REFUSAL_MESSAGE = "I am sorry, but I can only answer questions related to Zyro Dynamics (Acrux Dynamics) internal HR policies, handbook, leave policies, and work-from-home guidelines. The requested information is outside the scope of my knowledge base."

# Sidebar Content
st.sidebar.markdown('<div style="text-align: center; padding: 1rem;"><span style="font-size: 3.5rem;">💼</span></div>', unsafe_allow_html=True)
st.sidebar.markdown("### Model Config & Credentials")
llm_provider = st.sidebar.selectbox("LLM Provider", ["Groq", "Gemini", "OpenAI"], index=0)

if llm_provider == "Groq":
    default_model = "llama-3.1-8b-instant"
    default_api_key = os.environ.get("GROQ_API_KEY", "")
elif llm_provider == "Gemini":
    default_model = "gemini-2.5-flash"
    default_api_key = os.environ.get("GOOGLE_API_KEY", "")
else:
    default_model = "gpt-4o-mini"
    default_api_key = os.environ.get("OPENAI_API_KEY", "")

model_name = st.sidebar.text_input("Model Name", default_model)
api_key = st.sidebar.text_input("API Key", value=default_api_key, type="password")

# Display status stats in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### System Statistics")
st.sidebar.markdown(
    '<div style="font-size: 0.85rem; color: #94a3b8;">'
    '<span class="status-indicator"></span> Database Status: <b>Online</b><br>'
    '📄 Indexed Documents: <b>11 Policy PDFs</b><br>'
    '⚡ Context Model: <b>similarity + page_expansion</b>'
    '</div>', 
    unsafe_allow_html=True
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Policy Reference")
with st.sidebar.expander("🏠 WFH Eligibility"):
    st.markdown("""
    * **L1 & L2 (Trainee/Junior)**: Not eligible
    * **L3 & L4 (Mid/Senior)**: Eligible (Hybrid/Ad-hoc)
    * **L5+ (Lead/Manager)**: Eligible (Full Remote/Hybrid)
    * *Note: Probationary employees are not eligible.*
    """)

with st.sidebar.expander("📅 Leave Summary"):
    st.markdown("""
    * **Earned Leave (EL)**: 1.25 days/mo (15 days/yr)
    * **Sick Leave (SL)**: 10 days/yr
    * **Maternity Leave**: 26 weeks
    * **Carried Forward (EL)**: Max 45 days per year
    """)

# Cache vectorstore builder and page contents
@st.cache_resource
def get_vectorstore_and_cache():
    search_dirs = [".", "/kaggle/input"]
    exclude_dirs = {".git", ".venv", "venv", "env", "__pycache__", ".streamlit", "node_modules"}
    pdf_paths = []
    
    for s_dir in search_dirs:
        if os.path.exists(s_dir):
            for root, dirs, files in os.walk(s_dir):
                dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]
                for file in files:
                    if file.lower().endswith(".pdf"):
                        pdf_path = os.path.join(root, file)
                        if pdf_path not in pdf_paths:
                            pdf_paths.append(pdf_path)
                            
    if not pdf_paths:
        return None, {}
        
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    
    documents = []
    for path in pdf_paths:
        try:
            loader = PyPDFLoader(path)
            documents.extend(loader.load())
        except Exception as e:
            st.error(f"Error loading {os.path.basename(path)}: {e}")
            
    if not documents:
        return None, {}
        
    # Populate page cache for full-page context expansion
    page_cache = {}
    for doc in documents:
        src = doc.metadata.get("source")
        pg = doc.metadata.get("page")
        page_cache[(src, pg)] = doc.page_content
        
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=120,
        chunk_overlap=20,
        length_function=len
    )
    chunks = splitter.split_documents(documents)
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        model_kwargs={'device': 'cpu'}
    )
    
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore, page_cache

# Load documents and create vector db
with st.spinner("Initializing policy database..."):
    vectorstore, page_cache = get_vectorstore_and_cache()

if vectorstore is None:
    st.error("No policy documents found. Please place PDF policy documents in the repository directory.")
    st.stop()

retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 8, "fetch_k": 25}
)

# Initialize LLM
llm = None
if api_key:
    if llm_provider == "Groq":
        os.environ["GROQ_API_KEY"] = api_key
        from langchain_groq import ChatGroq
        try:
            llm = ChatGroq(model=model_name, temperature=0.1, max_tokens=512)
        except Exception as e:
            st.sidebar.error(f"Error initializing Groq: {e}")
    elif llm_provider == "Gemini":
        os.environ["GOOGLE_API_KEY"] = api_key
        from langchain_google_genai import ChatGoogleGenerativeAI
        try:
            llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.1, max_output_tokens=512)
        except Exception as e:
            st.sidebar.error(f"Error initializing Gemini: {e}")
    elif llm_provider == "OpenAI":
        os.environ["OPENAI_API_KEY"] = api_key
        from langchain_openai import ChatOpenAI
        try:
            llm = ChatOpenAI(model=model_name, temperature=0.1, max_tokens=512)
        except Exception as e:
            st.sidebar.error(f"Error initializing OpenAI: {e}")

# Define prompts and chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

RAG_PROMPT = ChatPromptTemplate.from_template(
    "You are a professional HR assistant for Zyro Dynamics (referred to as Acrux Dynamics in employee questions).\n"
    "Answer the employee's HR question as accurately, directly, and completely as possible using only the context below.\n\n"
    "Rules for answering:\n"
    "1. Directness: Start answering the question immediately. Do NOT include any conversational filler, introductory phrases (such as 'Based on the context...', 'According to the policy...'), or concluding sentences. State only the facts.\n"
    "2. Complete Coverage: Address every part of the question explicitly. Extract and state all numbers, dates, rates, timelines, limits, conditions, eligibility criteria, and exceptions exactly as they appear in the context. Do not summarize or omit anything.\n"
    "3. Naming: Refer to the company using the name mentioned in the question (e.g. if the question asks about 'Acrux Dynamics', refer to it as 'Acrux Dynamics'; if it asks about 'Zyro Dynamics', refer to it as 'Zyro Dynamics'). Do not default to Zyro Dynamics if the question specifies Acrux Dynamics.\n"
    "4. Truthfulness: If the context does not contain the answer, say exactly: 'I can not find the answer to this question in the policy documents.'\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Answer:"
)

OOS_PROMPT = ChatPromptTemplate.from_template(
    "system: You are an OOS Classifier for Zyro Dynamics (Acrux Dynamics).\n"
    "Determine if the user's question is within the scope of internal HR policies, handbook, leave policies, and work-from-home guidelines.\n"
    "Answer only 'IN_SCOPE' or 'OUT_SCOPE'.\n"
    "Here are examples of OUT_SCOPE queries:\n"
    "- questions about other companies (e.g., Zoho, Freshworks, Salesforce, etc.)\n"
    "- technical features of products (e.g., product features of AcruxCRM, comparison with Salesforce)\n"
    "- financial details or revenue (e.g., last year's revenue, financial performance)\n"
    "- recruitment, job application processes, or careers (e.g., how to apply for a job, hiring process)\n"
    "Note: Topics like ESOP, bonus, CTC, salary, insurance, WFH, performance reviews, and leave policies are IN_SCOPE.\n\n"
    "human: Question: {question}\nClassification:"
)

def format_docs(docs):
    import os
    expanded_contents = []
    seen = set()
    for doc in docs:
        src = doc.metadata.get("source")
        pg = doc.metadata.get("page")
        key = (src, pg)
        if key in page_cache and key not in seen:
            seen.add(key)
            filename = os.path.basename(src)
            content = page_cache[key]
            expanded_contents.append(f"[Source: {filename}, Page: {pg + 1}]\n{content}")
    return "\n\n".join(expanded_contents)

# Header info cards (Only display when chat history is empty)
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = []
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            '<div class="glass-card">'
            '<div class="card-title">📅 Leave & Accrual Policy</div>'
            '<div class="card-text">Earned Leave accrues at 1.25 days/month. Carried forward limit is 45 days. Sick leave takes medical certificate for >2 consecutive days.</div>'
            '</div>', 
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            '<div class="glass-card">'
            '<div class="card-title">🏡 Work From Home Guidelines</div>'
            '<div class="card-text">Applies to L3 and above. Trainees (L1) and Juniors (L2) are not eligible. Hybrid offers up to 3 WFH days/week.</div>'
            '</div>', 
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            '<div class="glass-card">'
            '<div class="card-title">💰 Comp & Benefits Details</div>'
            '<div class="card-text">L4 Grade CTC range is Rs. 16.0L to 26.0L with 10% bonus target. Salaries are credited by the 7th of each month.</div>'
            '</div>', 
            unsafe_allow_html=True
        )

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("sources"):
            st.markdown("---")
            st.markdown("**Sources Cited:**")
            for src in message["sources"]:
                st.markdown(f'<span class="doc-pill">📄 {src}</span>', unsafe_allow_html=True)

# Suggested question selector
if len(st.session_state.messages) == 0:
    st.markdown("### Suggested Policy Queries:")
    suggested_queries = [
        "What is the CTC range and bonus target for L4 Senior grade?",
        "How many days of Earned Leave can be carried forward?",
        "Who is eligible for WFH and what arrangements are available?",
        "What is the timeline for the Annual Performance Review (APR)?"
    ]
    
    # Render pill buttons
    for sq in suggested_queries:
        if st.button(sq, key=f"btn_{sq}"):
            # Inject question directly into input handler
            st.session_state.temp_query = sq

# Input capture
user_query = st.chat_input("Ask a question about Zyro Dynamics HR policies...")

# If a pill button was clicked, override input
if "temp_query" in st.session_state and st.session_state.temp_query:
    user_query = st.session_state.temp_query
    st.session_state.temp_query = None

if user_query:
    # Display user message
    with st.chat_message("user"):
        st.write(user_query)
    
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.chat_message("assistant"):
        if llm is None:
            st.info("Please enter a valid API Key in the sidebar to generate answers.")
        else:
            with st.spinner("Searching policies and generating answer..."):
                try:
                    classifier_chain = OOS_PROMPT | llm | StrOutputParser()
                    classification = classifier_chain.invoke({"question": user_query}).strip().upper()
                    
                    if "OUT_SCOPE" in classification or "OUT_OF_SCOPE" in classification:
                        st.write(REFUSAL_MESSAGE)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": REFUSAL_MESSAGE,
                            "sources": []
                        })
                    else:
                        # Normalize query
                        q_norm = user_query.replace("Acrux Dynamics", "Zyro Dynamics").replace("acrux dynamics", "zyro dynamics").replace("Acrux", "Zyro").replace("acrux", "zyro")
                        docs = retriever.invoke(q_norm)
                        context_text = format_docs(docs)
                        
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
                                st.markdown(f'<span class="doc-pill">📄 {cit}</span>', unsafe_allow_html=True)
                                
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": citations
                        })
                except Exception as e:
                    st.error(f"Error generating answer: {e}")
                    st.stop()
