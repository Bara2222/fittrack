import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime, timedelta
import webbrowser
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict, Counter

# Use secrets if available, otherwise default to localhost
try:
    API_BASE = st.secrets.get('api_base', 'http://localhost:5000/api')
except:
    API_BASE = 'http://localhost:5000/api'

# Initialize session
if 'session' not in st.session_state:
    st.session_state['session'] = requests.Session()

session = st.session_state['session']


# --------------------------------------------------
# Global CSS & UI helpers (visual improvements)
# --------------------------------------------------
_GLOBAL_CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
html, body, [class*='css'] { font-family: 'Poppins', sans-serif; color:#1a1a1a; background:var(--bg) !important }

/* Theme variables - Black & Yellow */
:root{
    --bg: #000000;           /* pure black background */
    --surface: #1c1c1c;      /* dark surface with slight lift */
    --primary: #ffd700;      /* vibrant gold/yellow */
    --secondary: #ffffff;    /* white for text */
    --accent: #ffed4e;       /* lighter yellow accent */
    --muted: #b8b8b8;        /* lighter gray for better readability */
    --success: #4ade80;
    --danger: #ef4444;
    --border: #ffd700;       /* yellow borders */
    --text-primary: #ffffff; /* primary white text */
    --text-secondary: #000000; /* black text for yellow backgrounds */
}

/* Container */
.block-container{
    max-width:1200px; 
    margin:0 auto; 
    padding:2rem 1.5rem; 
    background:var(--bg);
    position: relative;
}
.block-container::before{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        repeating-linear-gradient(90deg, transparent, transparent 50px, rgba(255,215,0,0.03) 50px, rgba(255,215,0,0.03) 51px),
        repeating-linear-gradient(0deg, transparent, transparent 50px, rgba(255,215,0,0.03) 50px, rgba(255,215,0,0.03) 51px);
    pointer-events: none;
    z-index: -1;
}

/* Main header */
.main-header{
    font-size:36px; 
    font-weight:800; 
    color:var(--text-secondary); 
    background: linear-gradient(135deg, var(--primary), var(--accent)); 
    padding:24px 32px; 
    border-radius:20px; 
    box-shadow:0 8px 32px rgba(255,215,0,0.5), 0 0 60px rgba(255,215,0,0.2); 
    margin-bottom:32px; 
    display:flex; 
    align-items:center; 
    gap:16px;
    border: 3px solid var(--primary);
    position: relative;
    overflow: hidden;
}
.main-header::before{
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
    transform: rotate(45deg);
    animation: shine 3s infinite;
}
@keyframes shine {
    0% { transform: translateX(-100%) rotate(45deg); }
    100% { transform: translateX(100%) rotate(45deg); }
}
.main-sub{font-size:14px; color:var(--text-secondary); margin-left:8px; font-weight:500; opacity:0.9}

/* Sidebar */
[data-testid="stSidebar"]{
    background: linear-gradient(180deg, #1c1c1c, #0a0a0a);
    padding:24px 16px; 
    box-shadow: 0 0 30px rgba(255,215,0,0.3); 
    border-right: 2px solid var(--primary);
}
[data-testid="stSidebar"] h1{
    color: var(--primary) !important;
    text-shadow: 0 0 20px rgba(255,215,0,0.8);
}

/* Buttons */
.stButton>button{
    border-radius:12px; 
    padding:12px 24px; 
    transition: all .3s ease; 
    font-weight:600;
    font-size:15px;
    border:none;
    background: var(--primary) !important;
    color: #000000 !important;
    box-shadow: 0 2px 8px rgba(255,215,0,0.4);
}
.stButton>button:hover{
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(255,215,0,0.6);
    background: var(--accent) !important;
}
.stButton>button:disabled{opacity:0.5}

/* Secondary buttons */
.stButton>button.secondary{
    background: transparent;
    border: 2px solid var(--primary);
    color: var(--primary);
    box-shadow: none;
}
.stButton>button.secondary:hover{
    background: var(--primary);
    color: white;
}

/* Messages */
.stAlert{
    border-radius:12px;
    padding:16px;
    border-left: 4px solid var(--primary);
}
.stAlert--success{
    background: rgba(72,187,120,0.1);
    border-left-color: var(--success);
    color: var(--secondary);
}
.stAlert--error{
    background: rgba(245,101,101,0.1);
    border-left-color: var(--danger);
    color: var(--secondary);
}
.stAlert--info{
    background: rgba(255,215,0,0.1);
    border-left-color: var(--primary);
    color: var(--secondary);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{
    gap:12px;
    background: rgba(255,215,0,0.05);
    padding:12px;
    border-radius:16px;
    border: 2px solid rgba(255,215,0,0.2);
}
.stTabs [data-baseweb="tab"]{
    border-radius:12px;
    padding:14px 28px;
    font-weight:700;
    color: var(--muted);
    border: 2px solid transparent;
    transition: all .3s ease;
}
.stTabs [data-baseweb="tab"]:hover{
    background: rgba(255,215,0,0.1);
    border-color: rgba(255,215,0,0.3);
    color: var(--primary);
}
.stTabs [aria-selected="true"]{
    background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
    color: var(--text-secondary) !important;
    border-color: var(--primary) !important;
    box-shadow: 0 4px 12px rgba(255,215,0,0.4);
    font-weight: 800;
}

/* Cards */
.card{
    background: linear-gradient(145deg, #1c1c1c, #141414); 
    border-radius:20px; 
    padding:28px; 
    box-shadow:0 4px 20px rgba(255,215,0,0.2), inset 0 1px 0 rgba(255,215,0,0.1);
    border: 2px solid rgba(255,215,0,0.3);
    transition: all .4s ease;
    position: relative;
}
.card::before{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 20px;
    padding: 2px;
    background: linear-gradient(135deg, var(--primary), transparent, var(--accent));
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    opacity: 0;
    transition: opacity .4s ease;
}
.card:hover{
    box-shadow:0 8px 32px rgba(255,215,0,0.4), 0 0 60px rgba(255,215,0,0.2);
    transform: translateY(-4px) scale(1.02);
    border-color: var(--primary);
}
.card:hover::before{
    opacity: 1;
}

/* Override Streamlit defaults */
.stApp{background:var(--bg) !important}
.main{background:var(--bg) !important}
.block-container{background:var(--bg) !important}

/* Markdown/text */
.stMarkdown, .stText, .stHtml, .stMarkdown div, .stCaption{
    color: var(--text-primary) !important;
    background: transparent !important;
    line-height: 1.6;
}
.stMarkdown h1{
    color: var(--primary) !important;
    font-weight: 800;
    font-size: 2.5rem;
    text-shadow: 0 0 30px rgba(255,215,0,0.6);
    margin-bottom: 1rem;
}
.stMarkdown h2{
    color: var(--accent) !important;
    font-weight: 700;
    font-size: 2rem;
    text-shadow: 0 0 20px rgba(255,237,78,0.5);
    margin-bottom: 0.8rem;
}
.stMarkdown h3{
    color: var(--text-primary) !important;
    font-weight: 600;
    font-size: 1.5rem;
    border-left: 4px solid var(--primary);
    padding-left: 12px;
    margin-bottom: 0.6rem;
}
.stMarkdown p{
    color: var(--muted) !important;
    font-size: 1rem;
}
.stMarkdown a{
    color: var(--primary) !important;
    text-decoration: none;
    font-weight:600;
    border-bottom: 2px solid transparent;
    transition: all .3s ease;
}
.stMarkdown a:hover{
    border-bottom-color: var(--primary);
    text-shadow: 0 0 10px rgba(255,215,0,0.6);
}

/* Form inputs */
.stTextInput>div>div>input, 
.stTextArea>div>div>textarea,
.stSelectbox>div>div>div,
.stNumberInput>div>div>input{
    background: linear-gradient(145deg, #2a2a2a, #1c1c1c) !important;
    border: 2px solid rgba(255,215,0,0.3) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    padding:14px 16px !important;
    font-size:16px !important;
    transition: all .3s ease;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus{
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 4px rgba(255,215,0,0.3), inset 0 2px 4px rgba(0,0,0,0.3) !important;
    background: linear-gradient(145deg, #303030, #202020) !important;
}

/* Labels */
.stTextInput>label, .stTextArea>label, .stSelectbox>label, .stNumberInput>label{
    color: var(--primary) !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    margin-bottom: 10px !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Sidebar elements */
[data-testid="stSidebar"] .stButton>button{
    width:100%;
    text-align:left;
    justify-content:flex-start;
    background: transparent !important;
    color: var(--text-primary) !important;
    box-shadow:none;
    border: 2px solid rgba(255,215,0,0.2) !important;
    border-radius: 12px;
}
[data-testid="stSidebar"] .stButton>button:hover{
    background: rgba(255,215,0,0.15) !important;
    border-color: var(--primary) !important;
    transform: translateX(6px);
    box-shadow: 0 0 20px rgba(255,215,0,0.3) !important;
    color: var(--primary) !important;
}

/* Stat boxes */
.stat-box{
    background: linear-gradient(135deg, #ffd700, #ffed4e);
    color: #000000;
    padding:32px;
    border-radius:20px;
    text-align:center;
    box-shadow:0 8px 32px rgba(255,215,0,0.5), inset 0 -2px 0 rgba(0,0,0,0.1);
    border: 3px solid #000000;
    position: relative;
    overflow: hidden;
}
.stat-box::before{
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(255,255,255,0.3), transparent);
    transform: rotate(45deg);
    animation: shine 3s infinite;
}
.stat-number{
    font-size:56px;
    font-weight:900;
    margin-bottom:12px;
    text-shadow: 2px 2px 0 rgba(0,0,0,0.2);
    position: relative;
}
.stat-label{
    font-size:16px;
    font-weight:700;
    opacity:0.9;
    text-transform:uppercase;
    letter-spacing:2px;
    position: relative;
}

/* Expander */
.streamlit-expanderHeader{
    background: var(--surface);
    border-radius:12px;
    padding:16px;
    border: 1px solid var(--border);
    font-weight:600;
    color: var(--secondary);
}
.streamlit-expanderHeader:hover{
    border-color: var(--primary);
    background: rgba(255,215,0,0.05);
}

</style>
"""

st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)


def _password_strength(pw: str):
    """Return (score 0-5, color, label, width%)"""
    if not pw:
        return 0, '#eee', 'Very weak', 6
    score = 0
    if len(pw) >= 8:
        score += 1
    if len(pw) >= 12:
        score += 1
    if any(c.isdigit() for c in pw):
        score += 1
    if any(not c.isalnum() for c in pw):
        score += 1
    if any(c.isupper() for c in pw) and any(c.islower() for c in pw):
        score += 1

    if score <= 1:
        return score, '#ef4444', 'Weak', 20 + score*10
    if score <= 3:
        return score, '#f97316', 'Fair', 40 + score*12
    return score, '#10b981', 'Strong', 80 + (score-4)*4


def render_app_header():
    # Version from secrets if available
    try:
        ver = st.secrets.get('app_version', 'v2.0')
    except Exception:
        ver = 'v2.0'
    st.markdown(f"<div class='main-header'>💪 FitTrack <span class='main-sub'>{ver} — Tréninkový deník</span></div>", unsafe_allow_html=True)



def _safe_json(resp, default=None):
    """Return parsed JSON or a fallback dict with 'error' or default."""
    try:
        return resp.json()
    except Exception:
        try:
            text = resp.text
            if text:
                return {'error': text}
        except Exception:
            pass
    return default if default is not None else {}


def _display_api_error(resp):
    """Centralized display for API errors: prefer server message and request id if provided."""
    try:
        payload = resp.json()
    except Exception:
        payload = None

    if payload and isinstance(payload, dict):
        msg = payload.get('error') or payload.get('message')
        rid = payload.get('request_id') or resp.headers.get('X-Request-ID')
        if msg:
            if rid:
                st.error(f"{msg} (ID: {rid})")
                # provide copy button for the request id (JS fallback for Streamlit)
                btn = st.button('Kopírovat ID chyby', key=f'copy_err_{rid}')
                if btn:
                    # Use clipboard via JS
                    js = f"navigator.clipboard.writeText('{rid}').then(()=>alert('ID zkopírováno do schránky'))"
                    st.write(f"<script>{js}</script>", unsafe_allow_html=True)
            else:
                st.error(msg)
            return

    # Fallback to raw text
    text = ''
    try:
        text = resp.text
    except Exception:
        pass
    if text:
        st.error(text)
    else:
        st.error('Neznámá chyba serveru')

# Initialize login state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'
if 'show_login_form' not in st.session_state:
    st.session_state['show_login_form'] = False

# Check for Google OAuth callback
try:
    query_params = st.query_params
except AttributeError:
    # Fallback for very old streamlit versions
    query_params = {}

if 'auth' in query_params:
    # query_params values are lists when returned by Streamlit
    auth_val = query_params.get('auth')
    if isinstance(auth_val, list):
        auth_val = auth_val[0] if auth_val else None

    if auth_val == 'success':
        st.session_state['logged_in'] = True
        st.success('Přihlášení přes Google úspěšné!')
        # Clear query params
        try:
            st.query_params.clear()
        except Exception:
            pass
    elif auth_val == 'error':
        msg = query_params.get('msg')
        if isinstance(msg, list):
            msg = msg[0] if msg else 'Unknown error'
        st.error(f"Chyba při přihlášení: {msg}")
        try:
            st.query_params.clear()
        except Exception:
            pass
    

def check_login():
    """Check if user is logged in by calling /api/me"""
    try:
        r = session.get(f"{API_BASE}/me", timeout=2)
        if r.ok:
            st.session_state['logged_in'] = True
            st.session_state['user'] = _safe_json(r).get('user')
            return True
    except Exception:
        pass
    st.session_state['logged_in'] = False
    st.session_state['user'] = None
    return False



def profile_form():
    """Render a one-time profile form (age, height_cm, weight_kg) shown only if profile isn't completed."""
    st.markdown("<div class='main-header'>📝 Doplnit profil</div>", unsafe_allow_html=True)
    st.info('Prosím doplňte svůj věk, výšku (v cm) a váhu (v kg). Zobrazí se pouze jednou po prvním přihlášení.')
    with st.form('profile_form'):
        age = st.number_input('Věk', min_value=1, max_value=120, value=25)
        height = st.number_input('Výška (cm)', min_value=50, max_value=250, value=175)
        weight = st.number_input('Váha (kg)', min_value=20.0, max_value=300.0, value=75.0, step=0.5)
        submitted = st.form_submit_button('Uložit profil')
        if submitted:
            payload = {'age': int(age), 'height_cm': float(height), 'weight_kg': float(weight)}
            try:
                r = session.post(f"{API_BASE}/profile", json=payload, timeout=5)
                if r.ok:
                    st.success('Profil uložen.')
                    # update local user state
                    if 'user' not in st.session_state:
                        st.session_state['user'] = {}
                    st.session_state['user'].update({'age': payload['age'], 'height_cm': payload['height_cm'], 'weight_kg': payload['weight_kg'], 'profile_completed': True})
                    st.rerun()
                else:
                    err = _safe_json(r).get('error')
                    st.error(err or 'Chyba při ukládání profilu')
            except Exception:
                st.error('Nepodařilo se kontaktovat API')
    st.stop()


def landing_page():
    """Landing page with intro and login button."""
    # Check if we should show login form instead
    if st.session_state.get('show_login_form', False):
        login_page()
        return

    # Hero section
    st.markdown("""
    <div style="text-align: center; padding: 4rem 0;">
        <h1 style="font-size: 3.5rem; font-weight: 800; margin-bottom: 1rem; background: linear-gradient(90deg, #5cc8ff, #ff9f6b); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            FitTrack
        </h1>
        <p style="font-size: 1.25rem; color: #9aa4b2; max-width: 600px; margin: 0 auto 2rem;">
            Váš osobní tréninkový deník. Sledujte své pokroky, plánujte cvičení a dosahujte svých cílů efektivněji.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Features grid
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="card" style="text-align: center; height: 100%;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">📊</div>
            <h3 style="color: #e6eef7;">Statistiky</h3>
            <p style="color: #9aa4b2;">Přehledné grafy a analýzy vašich výkonů.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card" style="text-align: center; height: 100%;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">💪</div>
            <h3 style="color: #e6eef7;">Tréninky</h3>
            <p style="color: #9aa4b2;">Databáze cviků a možnost tvorby vlastních plánů.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="card" style="text-align: center; height: 100%;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">📱</div>
            <h3 style="color: #e6eef7;">Mobilní</h3>
            <p style="color: #9aa4b2;">Přístupné odkudkoliv, optimalizované pro telefon.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 4rem;'></div>", unsafe_allow_html=True)

    # Call to action
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🚀 Začít cvičit (Přihlásit se)", use_container_width=True):
            st.session_state['show_login_form'] = True
            st.rerun()


def login_page():
    st.markdown('<div class="main-header">💪 FitTrack</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Přihlášení", "Registrace"])
    
    with tab1:
        st.subheader("Přihlásit se")
        with st.form("login_form"):
            username = st.text_input("Uživatelské jméno")
            password = st.text_input("Heslo", type="password")
            submit = st.form_submit_button("Přihlásit")
            
            if submit:
                if not username or not password:
                    st.error("Vyplňte všechna pole")
                else:
                    # Basic client-side validation
                    if len(username) < 3 or len(username) > 30:
                        st.error('Uživatelské jméno musí mít 3–30 znaků')
                    elif not username.isalnum():
                        st.error('Uživatelské jméno smí obsahovat pouze písmena a čísla')
                    else:
                        r = session.post(f"{API_BASE}/login", json={'username': username, 'password': password}, timeout=5)
                        if r.ok:
                            data = _safe_json(r)
                            st.session_state['logged_in'] = True
                            st.session_state['user'] = {'username': username, 'is_admin': data.get('is_admin', False)}
                            st.success("Přihlášení úspěšné!")
                            st.rerun()
                        else:
                            _display_api_error(r)
        
        st.markdown("---")
        st.subheader("Nebo se přihlaste přes Google")
        if st.button("🔐 Přihlásit se přes Google", use_container_width=True):
            r = session.get(f"{API_BASE}/google/login", timeout=5)
            if r.ok:
                auth_url = _safe_json(r).get('auth_url')
                # Replace meta-refresh with JS redirect and provide fallback link
                if auth_url:
                    st.markdown(f"<script>window.location.href='{auth_url}';</script>", unsafe_allow_html=True)
                    st.info(f"Přesměrování na Google... Pokud se nic nestane, [klikněte sem]({auth_url})")
                else:
                    st.error('Chyba při získávání adresy pro Google přihlášení')
            else:
                st.error("Chyba při inicializaci Google přihlášení")
    
    with tab2:
        st.subheader("Registrace")
        with st.form("register_form"):
            new_username = st.text_input("Uživatelské jméno", key="reg_user")
            new_password = st.text_input("Heslo (min. 8 znaků)", type="password", key="reg_pass")
            confirm_password = st.text_input("Potvrdit heslo", type="password", key="reg_confirm")
            submit_reg = st.form_submit_button("Registrovat")
            
            if submit_reg:
                if not new_username or not new_password:
                    st.error("Vyplňte všechna pole")
                elif new_password != confirm_password:
                    st.error("Hesla se neshodují")
                else:
                    # Client-side validation for username/password
                    import re
                    if not (3 <= len(new_username) <= 30):
                        st.error('Uživatelské jméno musí mít 3–30 znaků')
                    elif not re.match(r'^[A-Za-z0-9._-]+$', new_username):
                        st.error('Uživatelské jméno smí obsahovat písmena, čísla, tečky, podtržítka a pomlčky')
                    elif len(new_password) < 8:
                        st.error('Heslo musí mít minimálně 8 znaků')
                    else:
                        # Check username availability before attempting registration
                        proceed = True
                        try:
                            cu = requests.get(f"{API_BASE}/check_username", params={'username': new_username}, timeout=3)
                            if cu.ok:
                                info = _safe_json(cu)
                                if not info.get('available', True):
                                    st.error('Uživatelské jméno již existuje')
                                    proceed = False
                            else:
                                # don't block registration on check failure; show warning
                                st.warning('Kontrola uživatelského jména selhala, pokračuji v registraci')
                        except Exception:
                            st.warning('Kontrola uživatelského jména selhala, pokračuji v registraci')

                        if proceed:
                            r = session.post(f"{API_BASE}/register", json={'username': new_username, 'password': new_password}, timeout=5)
                            if r.ok:
                                st.success("✅ Registrace úspěšná! Nyní se můžete přihlásit.")
                                st.balloons()
                            else:
                                _display_api_error(r)

def dashboard_page():
    st.markdown('<div class="main-header">📊 Dashboard</div>', unsafe_allow_html=True)
    # Stats
    r = session.get(f"{API_BASE}/stats", timeout=5)
    if r.ok:
        stats = _safe_json(r).get('stats', {})
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{stats.get('total_workouts', 0)}</div>
                <div class="stat-label">Celkem tréninků</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{stats.get('recent_exercises', 0)}</div>
                <div class="stat-label">Cviků v posledních 5</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("⚡ Rychlý start")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🟢 Začátečník", use_container_width=True):
            r = session.post(f"{API_BASE}/quickstart/zacatecnik", timeout=5)
            if r.ok:
                st.success("Trénink vytvořen!")
                st.session_state['page'] = 'workouts'
                st.rerun()
    
    with col2:
        if st.button("🟡 Pokročilý", use_container_width=True):
            r = session.post(f"{API_BASE}/quickstart/pokracily", timeout=5)
            if r.ok:
                st.success("Trénink vytvořen!")
                st.session_state['page'] = 'workouts'
                st.rerun()
    
    with col3:
        if st.button("🔴 Expert", use_container_width=True):
            r = session.post(f"{API_BASE}/quickstart/expert", timeout=5)
            if r.ok:
                st.success("Trénink vytvořen!")
                st.session_state['page'] = 'workouts'
                st.rerun()
    
    st.markdown("---")
    
    # Recent workouts
    st.subheader("📅 Poslední tréninky")
    r = session.get(f"{API_BASE}/workouts", timeout=5)
    if r.ok:
        workouts = _safe_json(r).get('workouts', [])[:5]
        if workouts:
            for w in workouts:
                with st.expander(f"📌 {w['date']} — {w['exercise_count']} cviků"):
                    st.write(f"**Poznámka:** {w.get('note', 'Bez poznámky')}")
                    if st.button("Zobrazit detail", key=f"detail_{w['id']}"):
                        st.session_state['selected_workout'] = w['id']
                        st.session_state['page'] = 'workout_detail'
                        st.rerun()
        else:
            st.info("Zatím nemáte žádné tréninky. Začněte rychlým startem nebo vytvořte nový trénink!")


def stats_page():
    """Advanced statistics page with interactive Plotly charts."""
    st.markdown('<div class="main-header">📈 Pokročilé statistiky & analýzy</div>', unsafe_allow_html=True)

    r = session.get(f"{API_BASE}/workouts", timeout=5)
    if not r.ok:
        st.error('Nepodařilo se načíst tréninky pro statistiky')
        return

    workouts = _safe_json(r).get('workouts', [])
    if not workouts:
        st.info('🏋️ Zatím není dost dat pro statistiky. Začněte vytvářením tréninků!')
        return

    # Collect all exercise data with details
    ex_rows = []
    for w in workouts:
        try:
            wr = session.get(f"{API_BASE}/workouts/{w['id']}", timeout=5)
            if not wr.ok:
                continue
            detail = _safe_json(wr).get('workout', {})
            wdate = detail.get('date')
            for e in detail.get('exercises', []):
                ex_rows.append({
                    'date': wdate,
                    'name': e.get('name'),
                    'sets': e.get('sets', 0),
                    'reps': e.get('reps', 0),
                    'weight': e.get('weight', 0) or 0,
                    'volume': (e.get('sets', 0) * e.get('reps', 0) * (e.get('weight', 0) or 0))
                })
        except Exception:
            continue

    if not ex_rows:
        st.info('Žádné cviky k analýze')
        return

    df = pd.DataFrame(ex_rows)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # === KEY METRICS ===
    st.markdown("## 📊 Klíčové metriky")
    col1, col2, col3, col4 = st.columns(4)
    
    total_workouts = len(workouts)
    total_exercises = len(df)
    total_volume = df['volume'].sum()
    unique_exercises = df['name'].nunique()
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{total_workouts}</div>
            <div class="stat-label">Celkem tréninků</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{total_exercises}</div>
            <div class="stat-label">Provedených cviků</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{int(total_volume):,}</div>
            <div class="stat-label">Celkový objem (kg)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{unique_exercises}</div>
            <div class="stat-label">Různých cviků</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # === WORKOUT FREQUENCY CHART ===
    st.markdown("## 📅 Frekvence tréninků v čase")
    
    workout_dates = pd.to_datetime([w['date'] for w in workouts])
    workout_freq = workout_dates.value_counts().sort_index().reset_index()
    workout_freq.columns = ['Datum', 'Počet']
    
    fig_freq = px.line(workout_freq, x='Datum', y='Počet', 
                       title='Tréninky v čase',
                       labels={'Datum': 'Datum', 'Počet': 'Počet tréninků'},
                       template='plotly_dark',
                       line_shape='spline')
    fig_freq.update_traces(line_color='#FFD700', line_width=3, fill='tozeroy', fillcolor='rgba(255,215,0,0.2)')
    fig_freq.update_layout(
        plot_bgcolor='#1c1c1c',
        paper_bgcolor='#000000',
        font_color='#ffffff',
        title_font_size=20,
        hovermode='x unified'
    )
    st.plotly_chart(fig_freq, use_container_width=True)

    st.markdown("---")

    # === TOP EXERCISES BY COUNT ===
    st.markdown("## 🏆 Nejčastější cviky")
    
    exercise_counts = df['name'].value_counts().head(10).reset_index()
    exercise_counts.columns = ['Cvik', 'Počet']
    
    fig_top = px.bar(exercise_counts, x='Počet', y='Cvik', 
                     orientation='h',
                     title='Top 10 nejčastějších cviků',
                     template='plotly_dark',
                     color='Počet',
                     color_continuous_scale=['#FFD700', '#FFED4E'])
    fig_top.update_layout(
        plot_bgcolor='#1c1c1c',
        paper_bgcolor='#000000',
        font_color='#ffffff',
        title_font_size=20,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    st.plotly_chart(fig_top, use_container_width=True)

    st.markdown("---")

    # === VOLUME PROGRESS ===
    st.markdown("## 💪 Progres objemu (celkové kg)")
    
    daily_volume = df.groupby('date')['volume'].sum().reset_index()
    daily_volume.columns = ['Datum', 'Objem (kg)']
    
    fig_volume = px.area(daily_volume, x='Datum', y='Objem (kg)',
                         title='Celkový tréninkový objem v čase',
                         template='plotly_dark')
    fig_volume.update_traces(line_color='#FFD700', fillcolor='rgba(255,215,0,0.3)')
    fig_volume.update_layout(
        plot_bgcolor='#1c1c1c',
        paper_bgcolor='#000000',
        font_color='#ffffff',
        title_font_size=20,
        hovermode='x unified'
    )
    st.plotly_chart(fig_volume, use_container_width=True)

    st.markdown("---")

    # === EXERCISE DISTRIBUTION ===
    st.markdown("## 📦 Rozdělení cviků podle typu")
    
    # Group similar exercises (simple categorization)
    def categorize_exercise(name):
        name_lower = name.lower()
        if any(x in name_lower for x in ['bench', 'tlak', 'press']):
            return 'Tlaky'
        elif any(x in name_lower for x in ['squat', 'dřep']):
            return 'Dřepy'
        elif any(x in name_lower for x in ['deadlift', 'mrtvý']):
            return 'Mrtvé tahy'
        elif any(x in name_lower for x in ['pull', 'tah', 'row']):
            return 'Tahy'
        elif any(x in name_lower for x in ['curl', 'bicep']):
            return 'Biceps'
        elif any(x in name_lower for x in ['tricep', 'extension']):
            return 'Triceps'
        elif any(x in name_lower for x in ['shoulder', 'rameno']):
            return 'Ramena'
        else:
            return 'Ostatní'
    
    df['category'] = df['name'].apply(categorize_exercise)
    category_counts = df['category'].value_counts().reset_index()
    category_counts.columns = ['Kategorie', 'Počet']
    
    fig_pie = px.pie(category_counts, values='Počet', names='Kategorie',
                     title='Rozdělení cviků podle kategorie',
                     template='plotly_dark',
                     color_discrete_sequence=['#FFD700', '#FFED4E', '#FFA500', '#FF8C00', '#FF6347', '#FF4500', '#DC143C', '#8B0000'])
    fig_pie.update_layout(
        paper_bgcolor='#000000',
        font_color='#ffffff',
        title_font_size=20
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # === SETS & REPS ANALYSIS ===
    st.markdown("## 🔢 Analýza sérií a opakování")
    
    col1, col2 = st.columns(2)
    
    with col1:
        avg_sets = df.groupby('name')['sets'].mean().sort_values(ascending=False).head(10).reset_index()
        avg_sets.columns = ['Cvik', 'Průměr sérií']
        avg_sets['Průměr sérií'] = avg_sets['Průměr sérií'].round(1)
        
        fig_sets = px.bar(avg_sets, x='Cvik', y='Průměr sérií',
                         title='Průměrný počet sérií (Top 10)',
                         template='plotly_dark',
                         color='Průměr sérií',
                         color_continuous_scale=['#FFD700', '#FFED4E'])
        fig_sets.update_layout(
            plot_bgcolor='#1c1c1c',
            paper_bgcolor='#000000',
            font_color='#ffffff',
            xaxis_tickangle=-45,
            showlegend=False
        )
        st.plotly_chart(fig_sets, use_container_width=True)
    
    with col2:
        avg_reps = df.groupby('name')['reps'].mean().sort_values(ascending=False).head(10).reset_index()
        avg_reps.columns = ['Cvik', 'Průměr opakování']
        avg_reps['Průměr opakování'] = avg_reps['Průměr opakování'].round(1)
        
        fig_reps = px.bar(avg_reps, x='Cvik', y='Průměr opakování',
                         title='Průměrný počet opakování (Top 10)',
                         template='plotly_dark',
                         color='Průměr opakování',
                         color_continuous_scale=['#FFD700', '#FFED4E'])
        fig_reps.update_layout(
            plot_bgcolor='#1c1c1c',
            paper_bgcolor='#000000',
            font_color='#ffffff',
            xaxis_tickangle=-45,
            showlegend=False
        )
        st.plotly_chart(fig_reps, use_container_width=True)

    st.markdown("---")

    # === PROGRESS TRACKER FOR SPECIFIC EXERCISE ===
    st.markdown("## 📈 Sledování pokroku jednotlivých cviků")
    
    available_exercises = sorted(df['name'].unique())
    selected_exercise = st.selectbox('Vyberte cvik pro detailní analýzu:', available_exercises)
    
    if selected_exercise:
        ex_data = df[df['name'] == selected_exercise].copy()
        ex_data = ex_data.sort_values('date')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Weight progress
            if ex_data['weight'].sum() > 0:
                fig_weight = px.line(ex_data, x='date', y='weight',
                                    title=f'Progres váhy: {selected_exercise}',
                                    template='plotly_dark',
                                    markers=True)
                fig_weight.update_traces(line_color='#FFD700', marker_size=10)
                fig_weight.update_layout(
                    plot_bgcolor='#1c1c1c',
                    paper_bgcolor='#000000',
                    font_color='#ffffff',
                    xaxis_title='Datum',
                    yaxis_title='Váha (kg)'
                )
                st.plotly_chart(fig_weight, use_container_width=True)
            else:
                st.info('Žádná data o váze pro tento cvik')
        
        with col2:
            # Volume progress
            if ex_data['volume'].sum() > 0:
                fig_vol = px.line(ex_data, x='date', y='volume',
                                 title=f'Progres objemu: {selected_exercise}',
                                 template='plotly_dark',
                                 markers=True)
                fig_vol.update_traces(line_color='#FFED4E', marker_size=10)
                fig_vol.update_layout(
                    plot_bgcolor='#1c1c1c',
                    paper_bgcolor='#000000',
                    font_color='#ffffff',
                    xaxis_title='Datum',
                    yaxis_title='Objem (kg)'
                )
                st.plotly_chart(fig_vol, use_container_width=True)
            else:
                st.info('Žádná data o objemu pro tento cvik')

    st.markdown("---")

    # === WEEKLY HEATMAP ===
    st.markdown("## 🗓️ Týdenní aktivita (heatmap)")
    
    df_workouts = pd.DataFrame({'date': workout_dates})
    df_workouts['weekday'] = df_workouts['date'].dt.day_name()
    df_workouts['week'] = df_workouts['date'].dt.isocalendar().week
    
    weekday_counts = df_workouts['weekday'].value_counts().reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ], fill_value=0).reset_index()
    weekday_counts.columns = ['Den', 'Počet']
    weekday_map = {
        'Monday': 'Pondělí', 'Tuesday': 'Úterý', 'Wednesday': 'Středa',
        'Thursday': 'Čtvrtek', 'Friday': 'Pátek', 'Saturday': 'Sobota', 'Sunday': 'Neděle'
    }
    weekday_counts['Den'] = weekday_counts['Den'].map(weekday_map)
    
    fig_heatmap = px.bar(weekday_counts, x='Den', y='Počet',
                        title='Aktivita podle dne v týdnu',
                        template='plotly_dark',
                        color='Počet',
                        color_continuous_scale=['#1c1c1c', '#FFD700'])
    fig_heatmap.update_layout(
        plot_bgcolor='#1c1c1c',
        paper_bgcolor='#000000',
        font_color='#ffffff',
        title_font_size=20,
        showlegend=False
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.markdown("---")

    # === DATA EXPORT ===
    st.markdown("## 💾 Export dat")
    with st.expander('📥 Stáhnout surová data (CSV)'):
        try:
            csv_blob = df.to_csv(index=False)
            st.download_button('⬇️ Stáhnout CSV', 
                             data=csv_blob, 
                             file_name=f'fittrack_stats_{date.today().isoformat()}.csv', 
                             mime='text/csv',
                             use_container_width=True)
        except Exception:
            st.error('Export selhal')

def workouts_page():
    st.markdown('<div class="main-header">💪 Moje tréninky</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Nový trénink", use_container_width=True):
            st.session_state['page'] = 'new_workout'
            st.rerun()
    
    st.markdown("---")
    
    r = session.get(f"{API_BASE}/workouts", timeout=5)
    if not r.ok:
        st.error("Nepodařilo se načíst tréninky")
        return
    
    workouts = r.json().get('workouts', [])
    
    if not workouts:
        st.info("Zatím nemáte žádné tréninky")
        return
    
    # Create DataFrame for display
    df_data = []
    for w in workouts:
        df_data.append({
            'Datum': w['date'],
            'Poznámka': w.get('note', '')[:50] + ('...' if len(w.get('note', '')) > 50 else ''),
            'Počet cviků': w['exercise_count'],
            'ID': w['id']
        })
    
    df = pd.DataFrame(df_data)
    
    # Display workouts
    for idx, row in df.iterrows():
        col1, col2, col3, col4 = st.columns([2, 4, 2, 2])
        with col1:
            st.write(f"**{row['Datum']}**")
        with col2:
            st.write(row['Poznámka'])
        with col3:
            st.write(f"🏋️ {row['Počet cviků']} cviků")
        with col4:
            if st.button("Detail", key=f"view_{row['ID']}"):
                st.session_state['selected_workout'] = row['ID']
                st.session_state['page'] = 'workout_detail'
                st.rerun()
        st.markdown("---")

def workout_detail_page():
    if 'selected_workout' not in st.session_state:
        st.error("Žádný trénink nebyl vybrán")
        return
    
    wid = st.session_state['selected_workout']
    r = session.get(f"{API_BASE}/workouts/{wid}", timeout=5)
    
    if not r.ok:
        st.error("Trénink nenalezen")
        return
    
    workout = _safe_json(r).get('workout')
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f'<div class="main-header">🏋️ Trénink z {workout["date"]}</div>', unsafe_allow_html=True)
    with col2:
        if st.button("🗑️ Smazat trénink", use_container_width=True):
            r = session.delete(f"{API_BASE}/workouts/{wid}", timeout=5)
            if r.ok:
                st.success("Trénink smazán!")
                st.session_state['page'] = 'workouts'
                st.rerun()
    
    st.write(f"**Poznámka:** {workout.get('note', 'Bez poznámky')}")
    st.markdown("---")
    
    # Exercises
    st.subheader("📋 Cviky")
    exercises = workout.get('exercises', [])
    
    if exercises:
        for ex in exercises:
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            with col1:
                st.write(f"**{ex['name']}**")
            with col2:
                st.write(f"{ex['sets']}x")
            with col3:
                st.write(f"{ex['reps']} opak.")
            with col4:
                st.write(f"{ex.get('weight', '-')} kg")
            with col5:
                if st.button("❌", key=f"del_ex_{ex['id']}"):
                    r = session.delete(f"{API_BASE}/exercises/{ex['id']}", timeout=5)
                    if r.ok:
                        st.success("Cvik smazán!")
                        st.rerun()
            st.markdown("---")
    else:
        st.info("Žádné cviky zatím nebyly přidány")
    
    # Add exercise form
    st.subheader("➕ Přidat cvik")
    with st.form(f"add_exercise_{wid}"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            ex_name = st.text_input("Název cviku")
        with col2:
            ex_sets = st.number_input("Série", value=3, min_value=1)
        with col3:
            ex_reps = st.number_input("Opakování", value=10, min_value=1)
        with col4:
            ex_weight = st.number_input("Váha (kg)", value=0.0, step=2.5)
        
        submitted = st.form_submit_button("Přidat cvik")
        if submitted:
            if not ex_name:
                st.error("Vyplňte název cviku")
            else:
                payload = {
                    'name': ex_name,
                    'sets': ex_sets,
                    'reps': ex_reps,
                    'weight': ex_weight if ex_weight > 0 else None
                }
                r = session.post(f"{API_BASE}/exercises/{wid}/add", json=payload, timeout=5)
                if r.ok:
                    st.success("Cvik přidán!")
                    st.rerun()
                else:
                    st.error("Chyba při přidávání cviku")

def new_workout_page():
    st.markdown('<div class="main-header">➕ Nový trénink</div>', unsafe_allow_html=True)
    
    with st.form("new_workout_form"):
        workout_date = st.date_input("Datum", value=date.today())
        note = st.text_area("Poznámka")
        
        st.subheader("Cviky")
        st.write("Přidejte cviky do tréninku:")
        
        num_exercises = st.number_input("Počet cviků", min_value=1, max_value=20, value=1)
        
        exercises = []
        for i in range(num_exercises):
            st.markdown(f"**Cvik {i+1}**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                ex_name = st.text_input(f"Název", key=f"name_{i}")
            with col2:
                ex_sets = st.number_input(f"Série", value=3, min_value=1, key=f"sets_{i}")
            with col3:
                ex_reps = st.number_input(f"Opakování", value=10, min_value=1, key=f"reps_{i}")
            with col4:
                ex_weight = st.number_input(f"Váha (kg)", value=0.0, step=2.5, key=f"weight_{i}")
            
            if ex_name:
                exercises.append({
                    'name': ex_name,
                    'sets': ex_sets,
                    'reps': ex_reps,
                    'weight': ex_weight if ex_weight > 0 else None
                })
        
        submitted = st.form_submit_button("Vytvořit trénink")
        
        if submitted:
            if not exercises:
                st.error("Přidejte alespoň jeden cvik")
            else:
                payload = {
                    'date': workout_date.isoformat(),
                    'note': note,
                    'exercises': exercises
                }
                r = session.post(f"{API_BASE}/workouts", json=payload, timeout=5)
                if r.status_code == 201:
                    st.success("Trénink vytvořen!")
                    st.session_state['page'] = 'workouts'
                    st.rerun()
                else:
                    st.error("Chyba při vytváření tréninku")

def catalog_page():
    st.markdown('<div class="main-header">📚 Katalog cviků</div>', unsafe_allow_html=True)
    
    r = session.get(f"{API_BASE}/catalog", timeout=5)
    if not r.ok:
        st.error("Nepodařilo se načíst katalog")
        return
    
    catalog = _safe_json(r).get('exercises', [])
    
    st.write("Základní cviky pro inspiraci:")
    # Load user's workouts so they can choose where to add exercises
    wr = session.get(f"{API_BASE}/workouts", timeout=5)
    workouts = []
    workout_map = {}
    if wr.ok:
        workouts = _safe_json(wr).get('workouts', [])
    for w in workouts:
        note = (w.get('note') or 'Bez poznámky')
        short = note if len(note) <= 30 else note[:27] + '...'
        label = f"{w['date']} — {short} ({w['exercise_count']} cviků)"
        workout_map[label] = w['id']

    # Option to create a new workout
    create_new_label = '🔹 Vytvořit nový trénink (dnešek)'

    target_options = [create_new_label] + list(workout_map.keys())
    selected_target = st.selectbox('Vyberte trénink, do kterého přidat cviky:', target_options)

    # Multi-select for catalog
    chosen = st.multiselect('Vyberte cviky (můžete vybrat více):', catalog)

    col1, col2 = st.columns([1, 1])
    with col1:
        default_sets = st.number_input('Série (pro vybrané)', min_value=1, max_value=10, value=3)
    with col2:
        default_reps = st.number_input('Opakování (pro vybrané)', min_value=1, max_value=100, value=10)

    if st.button('Přidat vybrané do tréninku'):
        if not chosen:
            st.error('Vyberte alespoň jeden cvik')
        else:
            # Determine workout id (create if requested)
            if selected_target == create_new_label:
                payload = {'date': date.today().isoformat(), 'note': f'Přidáno z katalogu: {", ".join(chosen)}', 'exercises': []}
                cr = session.post(f"{API_BASE}/workouts", json=payload, timeout=5)
                if cr.ok:
                    wid = _safe_json(cr).get('id')
                else:
                    st.error('Nepodařilo se vytvořit nový trénink')
                    wid = None
            else:
                wid = workout_map.get(selected_target)

            if wid:
                errors = []
                for ex in chosen:
                    ex_payload = {'name': ex, 'sets': int(default_sets), 'reps': int(default_reps)}
                    ae = session.post(f"{API_BASE}/exercises/{wid}/add", json=ex_payload, timeout=5)
                    if not ae.ok:
                        try:
                            errors.append(_safe_json(ae).get('error', f'Chyba při přidávání {ex}'))
                        except Exception:
                            errors.append(f'Chyba při přidávání {ex}')

                if not errors:
                    st.success(f"{len(chosen)} cviků bylo přidáno do tréninku (ID {wid}).")
                    st.session_state['selected_workout'] = wid
                    st.session_state['page'] = 'workout_detail'
                    st.rerun()
                else:
                    for e in errors:
                        st.error(e)

def export_page():
    st.markdown('<div class="main-header">📥 Export dat</div>', unsafe_allow_html=True)

    st.write("Vyberte formát exportu a stáhněte si svá data.")

    fmt = st.selectbox('Formát exportu', ['CSV', 'PDF', 'JSON'])

    if fmt == 'CSV':
        if st.button("📊 Stáhnout CSV", use_container_width=True):
            r = session.get(f"{API_BASE}/export/csv", timeout=5)
            if r.ok:
                csv_data = r.json().get('csv')
                st.download_button(
                    label="💾 Uložit CSV soubor",
                    data=csv_data,
                    file_name=f"fittrack_export_{date.today().isoformat()}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.success("CSV připraveno ke stažení!")
            else:
                st.error("Chyba při exportu CSV")

    elif fmt == 'PDF':
        if st.button("📄 Stáhnout PDF", use_container_width=True):
            # PDF endpoint is served at /export/pdf
            try:
                r = session.get(f"{API_BASE.replace('/api','', timeout=5)}/export/pdf")
                if r.ok:
                    pdf_data = r.content
                    st.download_button(
                        label="💾 Uložit PDF",
                        data=pdf_data,
                        file_name=f"fittrack_export_{date.today().isoformat()}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success("PDF připraveno ke stažení!")
                else:
                    st.error("Chyba při exportu PDF")
            except Exception:
                st.error('Nepodařilo se kontaktovat server pro PDF export')

    elif fmt == 'JSON':
        if st.button("🗂️ Stáhnout JSON", use_container_width=True):
            # Build JSON from API
            r = session.get(f"{API_BASE}/workouts", timeout=5)
            if r.ok:
                summaries = _safe_json(r).get('workouts', [])
                translated = []
                for w in summaries:
                    # fetch detailed workout to include exercises
                    wr = session.get(f"{API_BASE}/workouts/{w['id']}", timeout=5)
                    if not wr.ok:
                        continue
                    detail = wr.json().get('workout', {})
                    # Lokalizované klíče a formát data
                    try:
                        dt = datetime.fromisoformat(detail.get('date')).strftime('%d.%m.%Y') if detail.get('date') else ''
                    except Exception:
                        dt = detail.get('date', '')
                    item = {
                        'ID': detail.get('id'),
                        'Datum': dt,
                        'Poznámka': detail.get('note', '')
                    }
                    exs = []
                    for e in detail.get('exercises', []):
                        exs.append({
                            'Cvik': e.get('name'),
                            'Série': e.get('sets'),
                            'Opakování': e.get('reps'),
                            'Váha (kg)': e.get('weight') if e.get('weight') is not None else ''
                        })
                    item['Cviky'] = exs
                    translated.append(item)

                import json as _json
                blob = _json.dumps(translated, ensure_ascii=False, indent=2)
                st.download_button(
                    label="💾 Uložit JSON",
                    data=blob,
                    file_name=f"fittrack_export_{date.today().isoformat()}.json",
                    mime="application/json",
                    use_container_width=True
                )
                st.success("JSON připraven ke stažení!")
            else:
                st.error('Chyba při získávání dat pro JSON export')

def admin_page():
    if not st.session_state.get('user', {}).get('is_admin'):
        st.error("Nemáte oprávnění")
        return
    
    st.markdown('<div class="main-header">⚙️ Admin panel</div>', unsafe_allow_html=True)
    
    r = session.get(f"{API_BASE}/admin/users", timeout=5)
    if not r.ok:
        st.error("Chyba při načítání uživatelů")
        return
    
    users = _safe_json(r).get('users', [])
    
    st.subheader(f"👥 Celkem uživatelů: {len(users)}")
    
    df_data = []
    for u in users:
        df_data.append({
            'ID': u['id'],
            'Uživatel': u['username'],
            'Email': u.get('email', ''),
            'OAuth': u.get('oauth_provider', '-'),
            'Tréninky': u['workout_count'],
            'Vytvořen': u.get('created_at', '')[:10] if u.get('created_at') else '-'
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True)

# Main app
if not st.session_state['logged_in']:
    # Try to check if already logged in
    if not check_login():
        landing_page()
        st.stop()

# If logged in but profile not completed, show profile form once
if st.session_state.get('logged_in') and st.session_state.get('user') and not st.session_state['user'].get('profile_completed'):
    profile_form()

# Sidebar navigation
render_app_header()
with st.sidebar:
    st.title("💪 FitTrack")
    user_info = st.session_state.get('user', {})
    st.write(f"👤 **{user_info.get('username', 'User')}**")
    
    # Profile expander: show profile data and allow editing
    with st.expander("Můj profil", expanded=False):
        u = st.session_state.get('user', {}) or {}
        
        # Display profile photo if exists
        if u.get('photo_url'):
            st.image(u.get('photo_url'), width=150)
        else:
            st.write("📷 Žádná profilová fotka")
        
        # Show profile info only if not completed (first login) or in edit mode
        if not u.get('profile_completed') or st.session_state.get('edit_profile'):
            profile_display = {
                'Uživatelské jméno': u.get('username', ''),
                'Věk': u.get('age') if u.get('age') is not None else '-',
                'Výška (cm)': u.get('height_cm') if u.get('height_cm') is not None else '-',
                'Váha (kg)': u.get('weight_kg') if u.get('weight_kg') is not None else '-',
            }
            try:
                import pandas as _pd
                rows = [[k, '' if v is None else str(v)] for k, v in profile_display.items()]
                st.table(_pd.DataFrame(rows, columns=['Pole', 'Hodnota']))
            except Exception:
                for k, v in profile_display.items():
                    st.write(f"**{k}:** {v}")

        if st.button("Upravit profil", key='sidebar_edit_profile'):
            st.session_state['edit_profile'] = True

        # Editing is done on the main page; sidebar only shows the button to switch there
        # (If edit_profile is True the main area will render the editor.)
    st.markdown("---")
    
    pages = {
        'dashboard': '📊 Dashboard',
    'stats': '📈 Statistiky',
        'workouts': '💪 Moje tréninky',
        'new_workout': '➕ Nový trénink',
        'catalog': '📚 Katalog cviků',
        'export': '📥 Export',
    }
    
    if user_info.get('is_admin'):
        pages['admin'] = '⚙️ Admin'
    
    for key, label in pages.items():
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            # leave edit mode when navigating to other pages
            st.session_state['edit_profile'] = False
            st.session_state['page'] = key
            st.rerun()
    
    st.markdown("---")
    
    if st.button("🚪 Odhlásit se", use_container_width=True):
        r = session.post(f"{API_BASE}/logout", timeout=5)
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.session_state['page'] = 'dashboard'
        st.session_state['edit_profile'] = False
        session.cookies.clear()
        st.rerun()

# Render current page
page = st.session_state.get('page', 'dashboard')

# If the user clicked "Upravit profil" in the sidebar, render the editor here on the main page
def profile_editor_main():
    st.markdown("<div class='main-header'>✏️ Upravit profil</div>", unsafe_allow_html=True)
    u = st.session_state.get('user', {}) or {}
    
    # Photo upload section (outside form)
    st.subheader("📷 Profilová fotka")
    uploaded_file = st.file_uploader("Nahrát novou fotku", type=['png', 'jpg', 'jpeg'], key='photo_upload')
    if uploaded_file is not None:
        import base64
        from io import BytesIO
        from PIL import Image
        
        # Display preview
        image = Image.open(uploaded_file)
        st.image(image, width=200, caption="Náhled")
        
        # Convert to base64 for storage
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        if st.button("💾 Uložit fotku"):
            # Store in session state (in real app, upload to server)
            st.session_state['user']['photo_url'] = f"data:image/png;base64,{img_str}"
            st.success("✅ Fotka uložena!")
            st.rerun()
    
    st.markdown("---")
    st.subheader("📝 Údaje profilu")
    
    with st.form('main_profile_editor'):
        age_val = st.number_input('Věk', min_value=1, max_value=120, value=int(u.get('age') or 25))
        height_val = st.number_input('Výška (cm)', min_value=50.0, max_value=250.0, value=float(u.get('height_cm') or 175.0))
        weight_val = st.number_input('Váha (kg)', min_value=20.0, max_value=300.0, value=float(u.get('weight_kg') or 75.0), step=0.5)
        submitted = st.form_submit_button('Uložit profil')
        cancel = st.form_submit_button('Zrušit')
        if submitted:
            payload = {'age': int(age_val), 'height_cm': float(height_val), 'weight_kg': float(weight_val)}
            try:
                r = session.post(f"{API_BASE}/profile", json=payload, timeout=5)
                if r.ok:
                    st.success('Profil uložen.')
                    st.session_state['user'].update({'age': payload['age'], 'height_cm': payload['height_cm'], 'weight_kg': payload['weight_kg'], 'profile_completed': True})
                    st.session_state['edit_profile'] = False
                    # after saving, show dashboard with updated values
                    st.session_state['page'] = 'dashboard'
                    st.rerun()
                else:
                    try:
                        st.error(_safe_json(r).get('error', 'Chyba při ukládání profilu'))
                    except Exception:
                        st.error('Chyba při ukládání profilu')
            except Exception:
                st.error('Nepodařilo se kontaktovat API')
        if cancel:
            st.session_state['edit_profile'] = False
            st.session_state['page'] = 'dashboard'
            st.rerun()

if st.session_state.get('edit_profile'):
    profile_editor_main()
    st.stop()

if page == 'dashboard':
    dashboard_page()
elif page == 'stats':
    stats_page()
elif page == 'workouts':
    workouts_page()
elif page == 'workout_detail':
    workout_detail_page()
elif page == 'new_workout':
    new_workout_page()
elif page == 'catalog':
    catalog_page()
elif page == 'export':
    export_page()
elif page == 'admin':
    admin_page()
