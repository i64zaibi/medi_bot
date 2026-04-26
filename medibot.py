import os
import streamlit as st
from model import load_vectorstore, get_answer
from dotenv import load_dotenv, find_dotenv
try:
    load_dotenv(find_dotenv())
except:
    pass

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediBot — AI Medical Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
    --bg:      #080f1a;
    --surface: #0d1b2e;
    --card:    #112240;
    --border:  #1e3a5f;
    --accent:  #00d4ff;
    --green:   #00e5a0;
    --text:    #e8f4fd;
    --muted:   #7a9bbf;
    --danger:  #ff4d6d;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

.main .block-container { padding: 0 !important; max-width: 100% !important; }

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 2rem 1.5rem !important; }

.hero-banner {
    background: linear-gradient(135deg, #0d1b2e 0%, #0a2040 40%, #0d1b2e 100%);
    border-bottom: 1px solid var(--border);
    padding: 1.8rem 2.5rem 1.4rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(0,212,255,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-banner::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 30%;
    width: 300px; height: 100px;
    background: radial-gradient(ellipse, rgba(0,229,160,0.06) 0%, transparent 70%);
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin: 0;
    line-height: 1.1;
    background: linear-gradient(90deg, #00d4ff, #00e5a0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 0.9rem;
    color: var(--muted);
    margin-top: 0.3rem;
    font-weight: 300;
    letter-spacing: 0.03em;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0,229,160,0.1);
    border: 1px solid rgba(0,229,160,0.3);
    color: var(--green);
    font-size: 0.72rem;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 20px;
    margin-top: 0.7rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.hero-badge::before {
    content: '';
    width: 6px; height: 6px;
    background: var(--green);
    border-radius: 50%;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(1.3); }
}

[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.3rem 0 !important;
}

[data-testid="stChatInput"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 0.8rem 1.2rem !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stChatInputContainer"] {
    background: var(--surface) !important;
    border-top: 1px solid var(--border) !important;
    padding: 1.2rem 2.5rem !important;
    position: sticky !important;
    bottom: 0 !important;
}

.stat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 0.8rem;
    margin: 1.5rem 0;
}
.stat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
    transition: border-color 0.2s, transform 0.2s;
}
.stat-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}
.stat-label {
    font-size: 0.72rem;
    color: var(--muted);
    margin-top: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.sidebar-logo {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00d4ff, #00e5a0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
}
.sidebar-tagline {
    font-size: 0.75rem;
    color: var(--muted);
    margin-bottom: 1.5rem;
    font-style: italic;
}

.section-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin: 1.2rem 0 0.6rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
}

.stButton > button {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
    font-size: 0.8rem !important;
    font-family: 'DM Sans', sans-serif !important;
    text-align: left !important;
    width: 100% !important;
    padding: 0.6rem 0.9rem !important;
    transition: all 0.2s !important;
    margin-bottom: 0.3rem !important;
}
.stButton > button:hover {
    border-color: var(--accent) !important;
    background: rgba(0,212,255,0.08) !important;
    color: var(--accent) !important;
    transform: translateX(3px) !important;
}

.info-box {
    background: rgba(0,212,255,0.06);
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 10px;
    padding: 0.9rem 1rem;
    font-size: 0.8rem;
    color: var(--muted);
    line-height: 1.5;
    margin-top: 1rem;
}
.info-box strong { color: var(--accent); }

.welcome-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 2.5rem;
    text-align: center;
    margin: 2rem auto;
    max-width: 560px;
}
.welcome-icon { font-size: 3.5rem; margin-bottom: 1rem; display: block; }
.welcome-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 0.6rem;
}
.welcome-text {
    color: var(--muted);
    font-size: 0.9rem;
    line-height: 1.6;
    margin-bottom: 1.5rem;
}
.feature-pills { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; }
.pill {
    background: rgba(0,212,255,0.08);
    border: 1px solid rgba(0,212,255,0.2);
    color: var(--accent);
    font-size: 0.75rem;
    padding: 4px 12px;
    border-radius: 20px;
}

.stSpinner > div { border-top-color: var(--accent) !important; }

.stAlert {
    background: rgba(255,77,109,0.1) !important;
    border: 1px solid rgba(255,77,109,0.3) !important;
    border-radius: 10px !important;
    color: #ff8fa3 !important;
}

hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
QUICK_QUESTIONS = [
    "💊 What are common drug interactions?",
    "🩺 Symptoms of Type 2 Diabetes?",
    "❤️ How to lower blood pressure naturally?",
    "🧠 What causes migraines?",
    "🦠 How do antibiotics work?",
]

# ── Cache vectorstore ─────────────────────────────────────────────────────────
@st.cache_resource
def get_vectorstore():
    return load_vectorstore()

# ── Session state ─────────────────────────────────────────────────────────────
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'quick_q' not in st.session_state:
    st.session_state.quick_q = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🩺 MediBot</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">AI-Powered Medical Encyclopedia</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="stat-grid">'
        '<div class="stat-card"><div class="stat-num">1M+</div><div class="stat-label">Med Pages</div></div>'
        '<div class="stat-card"><div class="stat-num">24/7</div><div class="stat-label">Available</div></div>'
        '<div class="stat-card"><div class="stat-num">RAG</div><div class="stat-label">Powered</div></div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-label">Quick Questions</div>', unsafe_allow_html=True)
    for i, q in enumerate(QUICK_QUESTIONS):
        if st.button(q, key=f"quick_btn_{i}"):
            st.session_state.quick_q = q.split(" ", 1)[1]

    st.markdown("""
    <div class="info-box">
        <strong>⚠️ Disclaimer</strong><br>
        MediBot provides information from the Gale Encyclopedia of Medicine.
        Always consult a qualified healthcare professional for medical advice.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Actions</div>', unsafe_allow_html=True)
    if st.button("🗑️ Clear Conversation", key="clear_chat_btn"):
        st.session_state.messages = []
        st.rerun()

# ── Hero Banner ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">Medical AI Assistant</div>
    <div class="hero-sub">Powered by Gale Encyclopedia of Medicine · Llama 3.1 · FAISS Vector Search</div>
    <div class="hero-badge">Live · Ready to Answer</div>
</div>
""", unsafe_allow_html=True)

# ── Chat Display ──────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <span class="welcome-icon">🩺</span>
        <div class="welcome-title">How can I help you today?</div>
        <div class="welcome-text">
            Ask me anything about medical conditions, symptoms, treatments,
            medications, or general health topics. I'll search through
            the medical encyclopedia to find accurate answers.
        </div>
        <div class="feature-pills">
            <span class="pill">🔍 Encyclopedia Search</span>
            <span class="pill">💡 Evidence-Based</span>
            <span class="pill">⚡ Instant Answers</span>
            <span class="pill">📚 Source Cited</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message['role'],
                             avatar="👤" if message['role'] == 'user' else "🩺"):
            if message['role'] == 'assistant' and '|||SOURCES|||' in message['content']:
                answer, sources = message['content'].split('|||SOURCES|||', 1)
                st.markdown(answer)
                with st.expander("📄 View Source Documents", expanded=False):
                    st.caption(sources)
            else:
                st.markdown(message['content'])

# ── Quick Question Injection ──────────────────────────────────────────────────
injected_prompt = None
if st.session_state.quick_q:
    injected_prompt = st.session_state.quick_q
    st.session_state.quick_q = None

# ── Chat Input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask a medical question…", key="main_chat_input")
prompt = injected_prompt or user_input

if prompt:
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({'role': 'user', 'content': prompt})

    with st.chat_message("assistant", avatar="🩺"):
        with st.spinner("Searching the medical encyclopedia…"):
            try:
                vectorstore = get_vectorstore()

                # ── Chat history banana ───────────────────────────────────────
                history_text = ""
                for msg in st.session_state.messages[:-1]:
                    role = "User" if msg['role'] == 'user' else "MediBot"
                    content = msg['content'].split('|||SOURCES|||')[0]
                    history_text += f"{role}: {content}\n"

                # ── model.py se answer lo ─────────────────────────────────────
                result, source_docs = get_answer(vectorstore, prompt, history_text)

                # ── Sources format karo ───────────────────────────────────────
                source_text = ""
                for i, doc in enumerate(source_docs, 1):
                    page = doc.metadata.get('page', 'N/A')
                    source_text += f"**Source {i}** (Page {page}):\n{doc.page_content[:300]}…\n\n"

                st.markdown(result)
                with st.expander("📄 View Source Documents", expanded=False):
                    st.markdown(source_text)

                combined = f"{result}|||SOURCES|||{source_text}"
                st.session_state.messages.append({'role': 'assistant', 'content': combined})

            except Exception as e:
                st.error(f"⚠️ {str(e)}")