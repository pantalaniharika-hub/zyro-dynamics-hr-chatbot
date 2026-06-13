import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# Page config  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Zyro Dynamics HR Help Desk",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Overall background */
    .stApp { background: #f0f4f8; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(160deg, #0f2940 0%, #1a4875 100%);
        color: #e0eaf5;
    }
    section[data-testid="stSidebar"] * { color: #e0eaf5 !important; }
    section[data-testid="stSidebar"] .stTextInput input {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        border-radius: 8px;
    }

    /* Chat message cards */
    .user-bubble {
        background: #1a4875;
        color: #ffffff;
        border-radius: 18px 18px 4px 18px;
        padding: 14px 18px;
        margin: 6px 0 6px 60px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        font-size: 0.95rem;
        line-height: 1.55;
    }
    .bot-bubble {
        background: #ffffff;
        color: #1e2a3a;
        border-radius: 18px 18px 18px 4px;
        padding: 14px 18px;
        margin: 6px 60px 6px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.10);
        font-size: 0.95rem;
        line-height: 1.6;
        border-left: 4px solid #1a4875;
    }
    .refusal-bubble {
        background: #fff8e1;
        color: #7a5800;
        border-radius: 18px 18px 18px 4px;
        padding: 14px 18px;
        margin: 6px 60px 6px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        font-size: 0.95rem;
        border-left: 4px solid #f0a500;
    }

    /* Source citation pills */
    .source-pill {
        display: inline-block;
        background: #e8f0fe;
        color: #1a4875;
        border-radius: 999px;
        padding: 3px 12px;
        font-size: 0.76rem;
        margin: 3px 4px 3px 0;
        border: 1px solid #b8d0f0;
        font-weight: 500;
    }
    .sources-label {
        font-size: 0.78rem;
        color: #6b7a8d;
        margin-top: 8px;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    /* Header bar */
    .header-bar {
        background: linear-gradient(90deg, #0f2940 0%, #1a4875 100%);
        color: white;
        padding: 20px 32px;
        border-radius: 12px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 18px;
        box-shadow: 0 4px 16px rgba(26,72,117,0.25);
    }
    .header-title { font-size: 1.6rem; font-weight: 700; margin: 0; }
    .header-sub   { font-size: 0.9rem; opacity: 0.75; margin: 2px 0 0; }

    /* Spinner override */
    .stSpinner > div { border-color: #1a4875 transparent transparent !important; }

    /* Chat input */
    .stChatInput textarea {
        background: #ffffff !important;
        border: 1.5px solid #c5d9f0 !important;
        border-radius: 12px !important;
        font-size: 0.95rem !important;
    }

    /* Hide Streamlit default header */
    header[data-testid="stHeader"] { display: none; }

    /* Quick question button */
    .stButton button {
        background: #e8f0fe;
        color: #1a4875;
        border: 1px solid #b8d0f0;
        border-radius: 8px;
        font-size: 0.82rem;
        padding: 5px 12px;
        width: 100%;
        text-align: left;
        transition: background 0.15s;
    }
    .stButton button:hover {
        background: #1a4875;
        color: #ffffff;
        border-color: #1a4875;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Imports (cached heavy work)
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def build_pipeline(api_key: str, provider: str = "groq"):
    """Load docs → chunk → embed → FAISS → LLM → chain. Cached."""
    import os, sys
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnableParallel, RunnablePassthrough

    # Set key
    os.environ["GROQ_API_KEY"]   = api_key
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"]    = "zyro-rag-challenge"

    # ── Load PDFs ────────────────────────────────────────────
    CORPUS = "/kaggle/input/zyro-dynamics-hr-corpus/"
    if not os.path.exists(CORPUS):
        CORPUS = "./hr_docs/"   # local fallback for dev

    docs = []
    if os.path.exists(CORPUS):
        for root, _, files in os.walk(CORPUS):
            for f in sorted(files):
                if f.lower().endswith(".pdf"):
                    try:
                        docs.extend(PyPDFLoader(os.path.join(root, f)).load())
                    except Exception:
                        pass

    if not docs:
        return None, None, None, "No HR policy documents found. Please check the corpus path."

    # ── Chunk ─────────────────────────────────────────────────
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    # ── Embed ─────────────────────────────────────────────────
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    # ── Vector store ──────────────────────────────────────────
    vs = FAISS.from_documents(chunks, embeddings)
    retriever = vs.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 10, "fetch_k": 40, "lambda_mult": 0.6},
    )

    # ── LLM ───────────────────────────────────────────────────
    from langchain_groq import ChatGroq
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.05, max_tokens=1024)

    # ── Prompts ───────────────────────────────────────────────
    RAG_PROMPT = ChatPromptTemplate.from_template(
        """You are the official HR policy assistant for Zyro Dynamics (also called Acrux Dynamics by employees).
Answer HR policy questions using ONLY the context below.

RULES:
1. Answer DIRECTLY — no preamble like "Based on the context...".
2. Include EVERY number, date, %, rate, limit, eligibility condition verbatim.
3. Use bullet points or numbered lists for multi-part answers.
4. Mirror the company name used in the question (Zyro Dynamics or Acrux Dynamics).
5. If the answer is not in context, say: "I cannot find the answer to this question in the policy documents."

Context:
{context}

Question: {question}

Answer:"""
    )

    OOS_PROMPT = ChatPromptTemplate.from_template(
        """Classify whether this question is IN_SCOPE or OUT_OF_SCOPE for an internal HR policy chatbot.

IN_SCOPE: leave policies, payroll, salary grades, benefits, insurance, performance reviews, 
          WFH/remote work, onboarding, separation, code of conduct, travel expenses, POSH, PIP, probation.
OUT_OF_SCOPE: external recruitment/job applications, company financials/revenue, product info, 
              software tools (CRM/Salesforce/Zoho), ESOPs, or anything unrelated to internal HR.

Question: {question}

Reply with exactly one word: IN_SCOPE or OUT_OF_SCOPE"""
    )

    def normalize(text):
        for a, b in [("Acrux Dynamics","Zyro Dynamics"),("acrux dynamics","zyro dynamics"),("Acrux","Zyro"),("acrux","zyro")]:
            text = text.replace(a, b)
        return text

    def fmt_docs(docs):
        parts = []
        for d in docs:
            src = os.path.basename(d.metadata.get("source",""))
            pg  = d.metadata.get("page", 0) + 1
            parts.append(f"[{src} | p.{pg}]\n{d.page_content}")
        return "\n\n---\n\n".join(parts)

    chain_info = {
        "retriever": retriever,
        "llm": llm,
        "RAG_PROMPT": RAG_PROMPT,
        "OOS_PROMPT": OOS_PROMPT,
        "fmt_docs": fmt_docs,
        "normalize": normalize,
    }

    return chain_info, retriever, llm, None


REFUSAL = "I can only answer HR-related questions from Zyro Dynamics policy documents."

def ask(question: str, chain_info: dict) -> tuple[str, list[str], bool]:
    """Returns (answer, citations, is_refusal)."""
    retriever   = chain_info["retriever"]
    llm         = chain_info["llm"]
    RAG_PROMPT  = chain_info["RAG_PROMPT"]
    OOS_PROMPT  = chain_info["OOS_PROMPT"]
    fmt_docs    = chain_info["fmt_docs"]
    normalize   = chain_info["normalize"]
    from langchain_core.output_parsers import StrOutputParser

    # 1. Out-of-scope check
    try:
        oos_chain  = OOS_PROMPT | llm | StrOutputParser()
        label      = oos_chain.invoke({"question": question}).strip().upper()
        if "OUT_OF_SCOPE" in label or "OUT" in label:
            return REFUSAL, [], True
    except Exception:
        pass

    # 2. Retrieve + generate
    q_norm = normalize(question)
    docs   = retriever.invoke(q_norm)
    ctx    = fmt_docs(docs)

    rag_chain = RAG_PROMPT | llm | StrOutputParser()
    answer    = rag_chain.invoke({"context": ctx, "question": question})

    # 3. Build citation list
    citations = []
    for d in docs:
        src = os.path.basename(d.metadata.get("source", "Unknown"))
        pg  = d.metadata.get("page", 0) + 1
        cit = f"{src}  (p. {pg})"
        if cit not in citations:
            citations.append(cit)

    return answer, citations, False


# ─────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pipeline" not in st.session_state:
    st.session_state.pipeline = None
if "ready" not in st.session_state:
    st.session_state.ready = False

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏢 HR Help Desk")
    st.markdown("**Zyro Dynamics Pvt. Ltd.**")
    st.divider()

    st.markdown("### ⚙️ Configuration")
    api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Get a free key at console.groq.com",
    )

    if st.button("🚀 Initialize Chatbot", use_container_width=True):
        if not api_key.strip():
            st.error("Please enter a valid Groq API key.")
        else:
            with st.spinner("Loading HR policy documents and building index…"):
                chain_info, _, _, err = build_pipeline(api_key.strip())
                if err:
                    st.error(err)
                else:
                    st.session_state.pipeline = chain_info
                    st.session_state.ready    = True
                    st.success("✅ HR chatbot ready!")

    st.divider()

    # Quick question examples
    st.markdown("### 💡 Sample Questions")
    examples = [
        "At what rate does Earned Leave accrue per month?",
        "What is the maximum EL that can be carried forward?",
        "What is the maternity leave entitlement?",
        "When is salary credited each month?",
        "What is the WFH policy for L3 employees?",
        "Explain the APR timeline.",
        "What is the PIP process?",
        "What does Group Medical Insurance cover?",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex[:20]}"):
            st.session_state._quick_q = ex

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("""
    <div style='font-size:0.75rem; opacity:0.65; margin-top:20px;'>
    ℹ️ This chatbot answers questions from Zyro Dynamics internal HR policy documents only.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Main area — header
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-bar">
  <span style="font-size:2.2rem;">🏢</span>
  <div>
    <p class="header-title">Zyro Dynamics HR Help Desk</p>
    <p class="header-sub">AI-powered • Retrieval-Augmented Generation • Policy-grounded answers</p>
  </div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.ready:
    st.info("👈 Enter your **Groq API key** in the sidebar and click **Initialize Chatbot** to get started.")
    st.markdown("""
    **What this chatbot can help with:**
    - 🌴 Leave policies (Earned Leave, Sick Leave, Maternity/Paternity)
    - 💰 Salary, CTC grades, and bonus structure
    - 🏠 Work-from-home and remote work eligibility
    - 🏥 Health insurance and benefits coverage
    - 📊 Performance reviews (APR, PIP, ratings)
    - 📋 Code of conduct, POSH, onboarding & separation
    - ✈️ Travel and expense reimbursement
    """)
    st.stop()

# ─────────────────────────────────────────────
# Render chat history
# ─────────────────────────────────────────────
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-bubble">👤 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            bubble_cls = "refusal-bubble" if msg.get("refusal") else "bot-bubble"
            icon = "⚠️" if msg.get("refusal") else "🤖"
            st.markdown(f'<div class="{bubble_cls}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("sources"):
                pills = "".join(f'<span class="source-pill">📄 {s}</span>' for s in msg["sources"])
                st.markdown(
                    f'<div class="sources-label">Sources</div><div>{pills}</div>',
                    unsafe_allow_html=True,
                )

# ─────────────────────────────────────────────
# Handle quick-question button
# ─────────────────────────────────────────────
if hasattr(st.session_state, "_quick_q") and st.session_state._quick_q:
    user_query = st.session_state._quick_q
    del st.session_state._quick_q
else:
    user_query = None

# ─────────────────────────────────────────────
# Chat input
# ─────────────────────────────────────────────
typed = st.chat_input("Ask a question about Zyro Dynamics HR policies…")
if typed:
    user_query = typed

if user_query:
    # Show user message
    st.markdown(f'<div class="user-bubble">👤 {user_query}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_query})

    with st.spinner("Searching policy documents…"):
        try:
            answer, citations, is_refusal = ask(user_query, st.session_state.pipeline)
        except Exception as e:
            answer, citations, is_refusal = f"⚠️ Error: {e}", [], False

    bubble_cls = "refusal-bubble" if is_refusal else "bot-bubble"
    icon       = "⚠️" if is_refusal else "🤖"
    st.markdown(f'<div class="{bubble_cls}">{icon} {answer}</div>', unsafe_allow_html=True)

    if citations and not is_refusal:
        pills = "".join(f'<span class="source-pill">📄 {s}</span>' for s in citations)
        st.markdown(
            f'<div class="sources-label">Sources</div><div>{pills}</div>',
            unsafe_allow_html=True,
        )

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": citations,
        "refusal": is_refusal,
    })
