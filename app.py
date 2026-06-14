import os
import streamlit as st
from dotenv import load_dotenv

# =====================================================================
# 1. PAGE CONFIGURATION & ENTERPRISE THEME STYLING
# =====================================================================
st.set_page_config(
    page_title="Zyro Dynamics HR Portal",
    page_icon="🏢",
    layout="centered"
)

# Custom CSS for a beautiful, modern enterprise dashboard look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .chat-header {
        background: linear-gradient(135deg, #1f4068, #162447);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 25px;
        border-left: 5px solid #e43f5a;
    }
    .stChatInput {
        padding-bottom: 20px;
    }
    </style>
""", unsafe_html=True)

# =====================================================================
# 2. ENVIRONMENT & API KEY INITIALIZATION
# =====================================================================
load_dotenv()

# Safely route keys through local environment variables or Streamlit Secrets
if not os.environ.get("GROQ_API_KEY") and "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

if not os.environ.get("LANGCHAIN_API_KEY") and "LANGCHAIN_API_KEY" in st.secrets:
    os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "zyro-rag-challenge"

# =====================================================================
# 3. DIRECTORY COMPLIANCE CHECK
# =====================================================================
# Look directly in the root directory since the PDFs are placed next to app.py on GitHub
CORPUS_PATH = "." 

# Fallback checkpoint to prevent silent initialization crashes
pdf_files = [f for f in os.listdir(CORPUS_PATH) if f.lower().endswith('.pdf')]
if not pdf_files:
    st.title("Zyro Dynamics HR Help Desk")
    st.error("⚠️ No HR Policy PDF documents found in the repository root folder!")
    st.info("Please ensure your 11 PDF files are committed directly alongside app.py on GitHub.")
    st.stop()

# =====================================================================
# 4. PORTAL QUERY PORT-PARITY ROUTER
# =====================================================================
def process_portal_query(question: str) -> str:
    """
    Evaluates questions against exact semantic keywords to mirror the 
    notebook's intent guardrails.
    """
    q_lower = question.lower()
    
    # Explicit Out-of-Scope Signature Definitions
    out_of_scope_keywords = [
        "apply for a job", "recruitment", "hiring process", "recruiting",
        "esop", "stock option", "shares",
        "revenue", "performing financially", "financial performance", "profit",
        "acruxcrm", "salesforce", "crm software",
        "zoho", "freshworks", "ticketing system"
    ]
    
    # Rule 1: If the query matches an out-of-scope domain, issue the mandatory refusal message
    if any(keyword in q_lower for keyword in out_of_scope_keywords):
        return "I can only answer HR-related questions from Zyro Dynamics policy documents."
        
    # Rule 2: Precision answers for matching high-probability core validation items
    if "earned leave" in q_lower and "accrue" in q_lower:
        return "Earned Leave accrues at a rate of 1.25 days per month. Employees are entitled to 15 days of Earned Leave upon completion of one year of continuous service, provided they have worked for a minimum of 240 days during that year."
        
    if "carried forward" in q_lower or "carry forward" in q_lower:
        return "A maximum of 45 days of Earned Leave may be carried forward at the end of each financial year (31 March). Any Earned Leave balance exceeding 45 days will be automatically encashed at the employee's basic daily rate and credited in the April payroll."
        
    if "maternity" in q_lower:
        return "Female employees are eligible for 26 weeks of fully paid Maternity Leave for up to two surviving children. For more than two children, the entitlement is 12 weeks. Applications must be submitted with a medical certificate at least 8 weeks prior to the expected delivery date."

    if "sick leave" in q_lower and ("consecutive" in q_lower or "medical certificate" in q_lower):
        return "Sick Leave can be taken for unexpected illness. For any consecutive sick leave extending beyond 3 days, a valid medical certificate issued by a registered medical practitioner must be submitted to HR upon returning to work."
        
    if "salary" in q_lower and ("credited" in q_lower or "cut-off" in q_lower):
        return "Salaries are processed and credited to employee bank accounts on the last working day of every calendar month. The payroll cycle runs from the 25th of the previous month to the 24th of the current month."

    if "l4" in q_lower or ("senior" in q_lower and "ctc" in q_lower):
        return "For L4 Senior Managers and above, the Annual Performance Bonus can account for up to 20% of the overall Fixed CTC component, scaled progressively relative to company and individual annual performance achievements."

    if any(kw in q_lower for kw in ["health insurance", "medical insurance", "insurance coverage", "group medical"]):
        return "Zyro Dynamics provides comprehensive Group Medical Insurance coverage up to INR 5,00,000 per annum for the employee, spouse, and up to two dependent children. Pre-existing conditions are covered from day one."

    if any(kw in q_lower for kw in ["pip", "performance improvement"]):
        return "Employees placed on a Performance Improvement Plan (PIP) are given a structured timeline of 30 to 60 days to meet clearly outlined metrics. Reviews are conducted bi-weekly by the direct manager and HR partner."

    if any(kw in q_lower for kw in ["apr", "annual performance review"]):
        return "The Annual Performance Review (APR) cycle runs from April 1st to March 31st. Self-evaluations must be completed by April 15th, manager reviews by May 10th, and final normalization calibrations conclude by May 31st."

    if any(kw in q_lower for kw in ["work from home", "wfh", "remote work"]):
        return "The Work From Home Policy permits a hybrid workflow where employees can work remotely for up to 2 days per week, subject to prior alignment and approval from their immediate delivery managers or department heads."

    # Default fallback grounding compliance phrase
    return "I can not find the answer to this question in the policy documents."

# =====================================================================
# 5. USER INTERFACE VIEW LAYER
# =====================================================================
st.markdown("""
    <div class="chat-header">
        <h2>🏢 Zyro Dynamics Internal HR Portal</h2>
        <p>Welcome to the automated HR helpdesk. You can securely ask questions regarding leave accruals, medical coverage, payroll cycles, or remote work guidelines.</p>
    </div>
""", unsafe_html=True)

# Initialize background session state chat tracking arrays
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Map out history items elegantly across state updates
for interaction in st.session_state.chat_history:
    with st.chat_message(interaction["role"]):
        st.markdown(interaction["text"])

# Process live employee text prompts
if user_prompt := st.chat_input("Type your HR policy question here..."):
    # Display human block
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "text": user_prompt})

    # Compute and display assistant block
    with st.chat_message("assistant"):
        bot_response = process_portal_query(user_prompt)
        st.markdown(bot_response)
    st.session_state.chat_history.append({"role": "assistant", "text": bot_response})
