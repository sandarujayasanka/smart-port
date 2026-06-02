"""
login_page.py  —  Smart Port Login UI (Sign In only)
Run:  streamlit run login_page.py
"""

import streamlit as st
import re
from db import login_user

st.set_page_config(
    page_title="Smart Port | Sign In",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.stApp { background: #07080f; color: #e2e8f0; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { max-width: 460px !important; padding-top: 80px !important; padding-bottom: 40px !important; }
.brand-block { text-align: center; margin-bottom: 40px; }
.brand-icon { font-size: 52px; line-height: 1; margin-bottom: 12px; }
.brand-title { font-size: 24px; font-weight: 700; color: #38bdf8; letter-spacing: -0.3px; }
.brand-sub { font-size: 11px; font-family: 'JetBrains Mono', monospace; color: #334155; letter-spacing: 2px; text-transform: uppercase; margin-top: 6px; }
.card-title { font-size: 20px; font-weight: 600; color: #f1f5f9; margin-bottom: 4px; }
.card-sub { font-size: 13px; color: #475569; margin-bottom: 28px; }
.stTextInput label { font-size: 11px !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 1.2px !important; color: #64748b !important; font-family: 'JetBrains Mono', monospace !important; }
.stTextInput input { background: #0f172a !important; border: 1px solid #1e3a5f !important; border-radius: 8px !important; color: #e2e8f0 !important; font-family: 'JetBrains Mono', monospace !important; font-size: 14px !important; padding: 10px 14px !important; }
.stTextInput input:focus { border-color: #38bdf8 !important; box-shadow: 0 0 0 2px rgba(56,189,248,0.15) !important; }
.stButton > button { width: 100%; background: linear-gradient(135deg, #0369a1, #0284c7) !important; color: #fff !important; border: none !important; border-radius: 8px !important; font-family: 'Sora', sans-serif !important; font-weight: 600 !important; font-size: 15px !important; padding: 13px !important; letter-spacing: 0.3px; margin-top: 8px; }
.stButton > button:hover { background: linear-gradient(135deg, #0284c7, #38bdf8) !important; }
.error-msg { background: #1c0505; border: 1px solid #7f1d1d; border-left: 4px solid #ef4444; border-radius: 8px; padding: 12px 16px; color: #fca5a5; font-size: 13px; font-family: 'JetBrains Mono', monospace; margin: 12px 0; }
.info-divider { text-align: center; font-size: 11px; color: #1e3a5f; font-family: 'JetBrains Mono', monospace; margin: 20px 0 0; letter-spacing: 0.5px; }
</style>
""", unsafe_allow_html=True)

def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$", email))

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "token" not in st.session_state:
    st.session_state.token = None

st.markdown("""
<div class="brand-block">
    <div class="brand-icon">🚢</div>
    <div class="brand-title">Smart Port</div>
    <div class="brand-sub">Container Yard Management System</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="card-title">Welcome back</div>', unsafe_allow_html=True)
st.markdown('<div class="card-sub">Sign in to access the port management dashboard</div>', unsafe_allow_html=True)

login_msg = st.empty()

login_email = st.text_input("Email Address", placeholder="admin@smartport.lk", key="login_email")
login_password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")

if st.button("Sign In →", key="btn_login"):
    if not login_email or not login_password:
        login_msg.markdown('<div class="error-msg">⚠️ &nbsp;Please fill in both fields.</div>', unsafe_allow_html=True)
    elif not is_valid_email(login_email):
        login_msg.markdown('<div class="error-msg">⚠️ &nbsp;Please enter a valid email address.</div>', unsafe_allow_html=True)
    else:
        with st.spinner("Authenticating..."):
            result = login_user(login_email, login_password)
        if result["ok"]:
            st.session_state.logged_in = True
            st.session_state.user = result["user"]
            st.session_state.token = result["token"]
            st.switch_page("pages/app.py")
        else:
            login_msg.markdown(f'<div class="error-msg">❌ &nbsp;{result["error"]}</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-divider">
    Contact your administrator to get access
</div>
""", unsafe_allow_html=True)