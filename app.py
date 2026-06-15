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
        color
