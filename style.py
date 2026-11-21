import streamlit as st

def inject_css():
    st.markdown("""
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 3rem;}
    [data-testid="stMetric"] {
        background: #1A1F2B; border: 1px solid #2A3142;
        padding: 14px 16px; border-radius: 12px;
    }
    .stTabs [data-baseweb="tab-list"] {gap: 8px;}
    .stTabs [data-baseweb="tab"] {padding: 8px 16px; border-radius: 8px;}
    .hero {
        background: linear-gradient(135deg, #0F766E 0%, #1E3A8A 100%);
        padding: 32px 36px; border-radius: 16px; margin-bottom: 24px;
    }
    .hero h1 {margin: 0; font-size: 2.4rem; color: white;}
    .hero p {margin: 8px 0 0 0; color: #E2E8F0; font-size: 1.05rem;}
    .card {
        background: #1A1F2B; border: 1px solid #2A3142;
        border-radius: 12px; padding: 18px 20px; height: 100%;
    }
    .card h4 {margin: 0 0 8px 0;}
    .card p {margin: 0; color: #CBD5E1; font-size: 0.95rem;}
    </style>
    """, unsafe_allow_html=True)