import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime, timedelta
import webbrowser
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict, Counter

# Import our custom modules
from config import API_BASE, GLOBAL_CSS, DEFAULT_WORKOUT_TEMPLATES
from auth import (
    initialize_session, check_oauth_callback, check_login, 
    profile_form, login_page, logout, _safe_json, _display_api_error
)
from utils import (
    calculate_1rm, calculate_plate_distribution, render_plate_visual,
    calculate_workout_streak, check_achievements, create_activity_heatmap,
    get_all_achievements, format_duration, calculate_bmi, get_bmi_category,
    calculate_calories_burned, toggle_theme, calculate_training_volume
)

# Initialize session and authentication
initialize_session()
session = st.session_state['session']


# Apply global CSS styles
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def show_loading(text="Načítám..."):
    """Show loading spinner with text"""
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem;">
        <div class="loading-spinner"></div>
        <p style="color: var(--muted); margin-top: 1rem;">{text}</p>
    </div>
    """, unsafe_allow_html=True)


def show_toast(message, toast_type="success"):
    """Show toast notification"""
    color = "var(--success)" if toast_type == "success" else "var(--danger)"
    st.markdown(f"""
    <div class="toast" style="background: {color};">
        {message}
    </div>
    <script>
        setTimeout(() => {{
            document.querySelector('.toast').remove();
        }}, 3000);
    </script>
    """, unsafe_allow_html=True)
    
    plate_html = '<div class="plate-visual">'
    
    # Left side plates
    for plate in reversed(plates):
        plate_class = f"plate-{str(plate).replace('.', '_')}"
        plate_html += f'<div class="plate {plate_class}">{plate}</div>'
    
    # Barbell
    plate_html += '<div class="barbell"></div>'
    
    # Right side plates (mirror)
    for plate in plates:
        plate_class = f"plate-{str(plate).replace('.', '_')}"
        plate_html += f'<div class="plate {plate_class}">{plate}</div>'
    
    plate_html += '</div>'
    return plate_html


def render_app_header():
    """Render top navigation bar with login/user info."""
    # Theme toggle button
    current_theme = st.session_state.get('theme', 'dark')
    theme_icon = '☀️' if current_theme == 'dark' else '🌙'
    
    # Apply theme class to body
    theme_class = f'theme-{current_theme}'
    st.markdown(f'<div class="{theme_class}"></div>', unsafe_allow_html=True)
    
    # Advanced Theme toggle button with animations
    st.markdown(f'''
    <button class="theme-toggle" onclick="toggleTheme()" title="Přepnout téma" id="themeToggle">
    </button>
    
    <script>
    function toggleTheme() {{
        const body = document.body;
        const toggle = document.getElementById('themeToggle');
        const isLight = body.classList.contains('light-theme');
        
        // Add transition class
        body.style.transition = 'all 0.6s cubic-bezier(0.23, 1, 0.32, 1)';
        
        if (isLight) {{
            body.classList.remove('light-theme');
            toggle.classList.remove('light');
            localStorage.setItem('theme', 'dark');
        }} else {{
            body.classList.add('light-theme');
            toggle.classList.add('light');
            localStorage.setItem('theme', 'light');
        }}
        
        // Trigger custom animation
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {{
            setTimeout(() => {{
                card.style.transform = 'scale(0.95)';
                setTimeout(() => {{
                    card.style.transform = 'scale(1)';
                }}, 100);
            }}, index * 50);
        }});
    }}
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const toggle = document.getElementById('themeToggle');
    
    if (savedTheme === 'light' || (!savedTheme && !prefersDark)) {{
        document.body.classList.add('light-theme');
        if (toggle) toggle.classList.add('light');
    }}
    
    // Add ripple effect to buttons
    document.addEventListener('click', function(e) {{
        if (e.target.matches('.stButton > button')) {{
            const button = e.target;
            const ripple = document.createElement('span');
            const rect = button.getBoundingClientRect();
            const size = Math.max(rect.height, rect.width);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${{size}}px;
                height: ${{size}}px;
                left: ${{x}}px;
                top: ${{y}}px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.3);
                transform: scale(0);
                animation: ripple 0.6s ease-out;
                pointer-events: none;
            `;
            
            button.style.position = 'relative';
            button.style.overflow = 'hidden';
            button.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        }}
    }});
    </script>
    ''', unsafe_allow_html=True)
    
    # Check if user is logged in
    logged_in = st.session_state.get('logged_in', False)
    user_info = st.session_state.get('user', {})
    
    if logged_in:
        # Show header for logged in users with achievements
        achievements = check_achievements({
            'total_workouts': 10,  # This should come from API
            'total_volume': 1500,
        })
        
        # Show new achievements
        if achievements and 'earned_achievements' not in st.session_state:
            st.session_state['earned_achievements'] = []
        
        new_achievements = [a for a in achievements if a['id'] not in st.session_state.get('earned_achievements', [])]
        
        if new_achievements:
            for achievement in new_achievements:
                st.markdown(f'''
                <div class="achievement-badge">
                    {achievement['name']} - {achievement['desc']}
                </div>
                ''', unsafe_allow_html=True)
                st.session_state['earned_achievements'].append(achievement['id'])
        
        try:
            ver = st.secrets.get('app_version', 'v2.0')
        except Exception:
            ver = 'v2.0'
        st.markdown(f"<div class='main-header'>💪 FitTrack <span class='main-sub'>{ver} — Tréninkový deník</span></div>", unsafe_allow_html=True)
    else:
        # Show header with login button for guests - using columns to align properly
        col1, col2, col3 = st.columns([5, 1, 1])
        
        with col1:
            st.markdown("""
            <div style='padding: 0.5rem 0;'>
                <h2 style='color: #ffd700; margin: 0; font-size: 1.8rem; font-weight: 800;'>💪 FitTrack</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div style='padding-top: 0.3rem; text-align: right;'>", unsafe_allow_html=True)
            if st.button("🔐 Přihlásit se", key="header_login_btn", use_container_width=True, type="primary"):
                st.session_state['show_login_form'] = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<div style='padding-top: 0.3rem; text-align: right;'>", unsafe_allow_html=True)
            if st.button("📝 Registrace", key="header_register_btn", use_container_width=True):
                st.session_state['show_login_form'] = True
                st.session_state['default_tab'] = 'Registrace'
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<hr style='border: none; border-top: 2px solid #ffd700; margin: 1rem 0;'>", unsafe_allow_html=True)



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
                # Provide copy info without button in form context
                st.code(f"ID chyby: {rid}", language="text")
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


# Footer component - displayed on all pages
def render_footer():
    """Render footer at the bottom of every page."""
    from datetime import datetime
    current_year = datetime.now().year
    
    # Use native Streamlit components instead of HTML
    st.markdown("---")
    st.markdown("### 💪 FitTrack")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**💪 FitTrack**")
        st.markdown("První český tréninkový deník, který zjednodušuje cestu k vašim fitness cílům.")
        st.markdown("📧 info@fittrack.cz")
        st.markdown("🌐 Webová aplikace")
    
    with col2:
        st.markdown("**Rychlé odkazy**")
        st.markdown("📊 Dashboard")
        st.markdown("💪 Moje tréninky")
        st.markdown("📚 Katalog cviků")
        st.markdown("📈 Statistiky")
        st.markdown("📥 Export dat")
    
    with col3:
        st.markdown("**Funkce**")
        st.markdown("✓ Sledování pokroku")
        st.markdown("✓ Plánování tréninků")
        st.markdown("✓ Grafické statistiky")
        st.markdown("✓ Export PDF/JSON")
        st.markdown("✓ Katalog cvičení")
    
    with col4:
        st.markdown("**Podpora**")
        st.markdown("📖 Nápověda")
        st.markdown("❓ Časté dotazy")
        st.markdown("🔒 Ochrana údajů")
        st.markdown("📋 Obchodní podmínky")
    
    st.markdown("---")
    st.markdown(f"© {current_year} FitTrack. Všechna práva vyhrazena. | Vytvořeno s ❤️ pro fitness nadšence")


def landing_page():
    """Landing page with intro and login button."""
    # Check if we should show login form instead
    if st.session_state.get('show_login_form', False):
        login_page()
        st.stop()
        return
    
    # Render header with login button
    render_app_header()

    # Hero section with larger impact
    st.markdown("""
    <div style="text-align: center; padding: 5rem 0 3rem 0; background: linear-gradient(180deg, #000000 0%, #1a1a1a 100%);">
        <div style="font-size: 1rem; color: #ffd700; font-weight: 600; letter-spacing: 2px; margin-bottom: 1rem;">
            VÁŠE FITNESS NA PRVNÍM MÍSTĚ
        </div>
        <h1 style="font-size: 4.5rem; font-weight: 900; margin-bottom: 1.2rem; color: #ffd700; text-shadow: 0 0 20px rgba(255, 215, 0, 0.5), 0 0 40px rgba(255, 215, 0, 0.3); line-height: 1.1;">
            FitTrack
        </h1>
        <p style="font-size: 1.1rem; color: #ffffff; max-width: 700px; margin: 0 auto 2.5rem; font-weight: 400; line-height: 1.7;">
            Profesionální tréninkový deník pro maximalizaci vašich výsledků.<br>
            Sledujte pokrok, plánujte tréninky a dosahujte cílů efektivněji než kdy předtím.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards with more professional look
    st.markdown("<div style='padding: 1rem 0; background: #000000;'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="card" style="text-align: center; padding: 2.5rem; min-height: 280px; 
             background: #1c1c1c; border: 2px solid #ffd700; border-radius: 12px; 
             transition: transform 0.3s; cursor: pointer;">
            <div style="font-size: 3.5rem; margin-bottom: 1.5rem;">📊</div>
            <h3 style="color: #ffd700; margin-bottom: 1rem; font-size: 1.5rem; font-weight: 700;">Detailní statistiky</h3>
            <p style="color: #ffffff; font-size: 1rem; line-height: 1.6;">
                Komplexní přehled vašeho pokroku s grafickou vizualizací výkonů a analýzou trendů.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card" style="text-align: center; padding: 2.5rem; min-height: 280px; 
             background: #1c1c1c; border: 2px solid #ffd700; border-radius: 12px; 
             transition: transform 0.3s; cursor: pointer;">
            <div style="font-size: 3.5rem; margin-bottom: 1.5rem;">💪</div>
            <h3 style="color: #ffd700; margin-bottom: 1rem; font-size: 1.5rem; font-weight: 700;">Plánování tréninků</h3>
            <p style="color: #ffffff; font-size: 1rem; line-height: 1.6;">
                Rozsáhlá databáze cvičení s možností vytváření vlastních tréninkových plánů na míru.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card" style="text-align: center; padding: 2.5rem; min-height: 280px; 
             background: #1c1c1c; border: 2px solid #ffd700; border-radius: 12px; 
             transition: transform 0.3s; cursor: pointer;">
            <div style="font-size: 3.5rem; margin-bottom: 1.5rem;">🌐</div>
            <h3 style="color: #ffd700; margin-bottom: 1rem; font-size: 1.5rem; font-weight: 700;">Webová aplikace</h3>
            <p style="color: #ffffff; font-size: 1rem; line-height: 1.6;">
                Přístup kdykoliv a odkudkoliv prostřednictvím moderního webového rozhraní.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Why FitTrack section
    st.markdown("""
    <div style='background: #1a1a1a; padding: 4rem 0; margin-top: 2rem;'>
        <h2 style='text-align: center; color: #ffd700; font-size: 2.5rem; font-weight: 800; margin-bottom: 3rem;'>
            PROČ FITTRACK?
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style='padding: 2rem; background: #1c1c1c; border-left: 4px solid #ffd700; margin-bottom: 1.5rem;'>
            <h4 style='color: #ffd700; margin-bottom: 1rem; font-size: 1.3rem;'>✓ Jednoduché a intuitivní</h4>
            <p style='color: #ffffff; line-height: 1.6;'>
                Začněte cvičit během několika sekund. Žádné složité nastavení ani komplikace.
            </p>
        </div>
        <div style='padding: 2rem; background: #1c1c1c; border-left: 4px solid #ffd700; margin-bottom: 1.5rem;'>
            <h4 style='color: #ffd700; margin-bottom: 1rem; font-size: 1.3rem;'>✓ Profesionální nástroje</h4>
            <p style='color: #ffffff; line-height: 1.6;'>
                Vše co potřebujete pro efektivní sledování pokroku na jednom místě.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='padding: 2rem; background: #1c1c1c; border-left: 4px solid #ffd700; margin-bottom: 1.5rem;'>
            <h4 style='color: #ffd700; margin-bottom: 1rem; font-size: 1.3rem;'>✓ Rychlý start</h4>
            <p style='color: #ffffff; line-height: 1.6;'>
                Předpřipravené tréninkové plány pro začátečníky i pokročilé sportovce.
            </p>
        </div>
        <div style='padding: 2rem; background: #1c1c1c; border-left: 4px solid #ffd700; margin-bottom: 1.5rem;'>
            <h4 style='color: #ffd700; margin-bottom: 1rem; font-size: 1.3rem;'>✓ Vaše data v bezpečí</h4>
            <p style='color: #ffffff; line-height: 1.6;'>
                Maximální ochrana vašich osobních údajů a tréninkové historie.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 4rem;'></div>", unsafe_allow_html=True)

    # Call to action with better design
    st.markdown("""
    <div style='text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);'>
        <h2 style='color: #ffffff; font-size: 2.2rem; font-weight: 700; margin-bottom: 1rem;'>
            Připraveni změnit své fitness?
        </h2>
        <p style='color: #b8b8b8; font-size: 1.2rem; margin-bottom: 2.5rem;'>
            Začněte sledovat své tréninky ještě dnes
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🚀 ZAČÍT CVIČIT", use_container_width=True, type="primary"):
            st.session_state['show_login_form'] = True
            st.rerun()
    
    # Add footer to landing page
    render_footer()
    st.stop()


def login_page():
    st.markdown('<div class="main-header">💪 FitTrack - Přihlášení</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Check if we should default to registration tab
    default_tab = st.session_state.get('default_tab', 'Přihlášení')
    if default_tab == 'Registrace':
        tab_order = ["Registrace", "Přihlášení"]
        st.session_state.pop('default_tab', None)  # Clear after using
    else:
        tab_order = ["Přihlášení", "Registrace"]
    
    tab1, tab2 = st.tabs(tab_order)
    
    # Determine which content goes where based on tab order
    if tab_order[0] == "Přihlášení":
        login_tab = tab1
        register_tab = tab2
    else:
        login_tab = tab2
        register_tab = tab1
    
    with login_tab:
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
                        try:
                            r = session.post(f"{API_BASE}/login", json={'username': username, 'password': password}, timeout=5)
                            if r.ok:
                                data = _safe_json(r)
                                st.session_state['logged_in'] = True
                                st.session_state['user'] = {'username': username, 'is_admin': data.get('is_admin', False)}
                                st.session_state['page'] = 'dashboard'
                                st.success("Přihlášení úspěšné!")
                                st.rerun()
                            else:
                                # Handle specific login errors with user-friendly messages
                                try:
                                    error_data = _safe_json(r)
                                    error_msg = error_data.get('error', 'Neznámá chyba')
                                    if r.status_code == 401:
                                        st.error("❌ Nesprávné uživatelské jméno nebo heslo")
                                    elif r.status_code == 400:
                                        st.error(f"❌ {error_msg}")
                                    else:
                                        st.error("❌ Došlo k chybě při přihlašování. Zkuste to prosím znovu.")
                                except:
                                    st.error("❌ Nesprávné přihlašovací údaje")
                        except Exception as e:
                            st.error("❌ Nepodařilo se připojit k serveru. Zkontrolujte internetové připojení.")
        
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
        
        # Tlačítko pro návrat na úvod
        col1, col2, col3 = st.columns([2, 1, 1])
        with col3:
            if st.button("← Zpět na úvod", use_container_width=True):
                st.session_state['show_login_form'] = False
                st.session_state['page'] = 'landing'
                st.rerun()
    
    with register_tab:
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
                            try:
                                r = session.post(f"{API_BASE}/register", json={'username': new_username, 'password': new_password}, timeout=5)
                                if r.ok:
                                    st.success("✅ Registrace úspěšná! Nyní se můžete přihlásit.")
                                    st.balloons()
                                else:
                                    # Handle registration errors with user-friendly messages
                                    try:
                                        error_data = _safe_json(r)
                                        error_msg = error_data.get('error', 'Neznámá chyba')
                                        if r.status_code == 400:
                                            st.error(f"❌ {error_msg}")
                                        else:
                                            st.error("❌ Došlo k chybě při registraci. Zkuste to prosím znovu.")
                                    except:
                                        st.error("❌ Došlo k chybě při registraci. Zkuste to prosím znovu.")
                            except Exception:
                                st.error("❌ Nepodařilo se připojit k serveru. Zkontrolujte internetové připojení.")
        
        # Tlačítko pro návrat na úvod u registrace
        col1, col2, col3 = st.columns([2, 1, 1])
        with col3:
            if st.button("← Zpět na úvod", key="register_back_btn", use_container_width=True):
                st.session_state['show_login_form'] = False
                st.session_state['page'] = 'landing'
                st.rerun()

def dashboard_page():
    st.markdown('<div class="main-header page-transition">📊 Přehled</div>', unsafe_allow_html=True)
    
    # Loading state for stats
    stats_placeholder = st.empty()
    with stats_placeholder.container():
        show_loading("Načítám statistiky...")
    
    r = session.get(f"{API_BASE}/stats", timeout=5)
    stats_placeholder.empty()  # Clear loading
    
    if r.ok:
        stats = _safe_json(r).get('stats', {})
        # Responsive columns with glassmorphism cards
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"""
            <div class="stat-box glow-effect">
                <svg class="progress-ring" viewBox="0 0 50 50">
                    <circle cx="25" cy="25" r="20" stroke="rgba(255,215,0,0.2)" stroke-width="3" fill="none"/>
                    <circle cx="25" cy="25" r="20" stroke="#FFD700" stroke-width="3" fill="none" 
                            stroke-dasharray="125" stroke-dashoffset="{125 - (min(stats.get('total_workouts', 0), 50) / 50) * 125}"
                            class="progress" stroke-linecap="round"/>
                </svg>
                <div class="stat-number">{stats.get('total_workouts', 0)}</div>
                <div class="stat-label">Celkem tréninků</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-box glow-effect">
                <svg class="progress-ring" viewBox="0 0 50 50">
                    <circle cx="25" cy="25" r="20" stroke="rgba(255,215,0,0.2)" stroke-width="3" fill="none"/>
                    <circle cx="25" cy="25" r="20" stroke="#FFD700" stroke-width="3" fill="none" 
                            stroke-dasharray="125" stroke-dashoffset="{125 - (min(stats.get('recent_exercises', 0), 20) / 20) * 125}"
                            class="progress" stroke-linecap="round"/>
                </svg>
                <div class="stat-number">{stats.get('recent_exercises', 0)}</div>
                <div class="stat-label">Cviků v posledních 5</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Add new advanced stats with glassmorphism
        if stats.get('total_workouts', 0) > 0:
            col3, col4 = st.columns([1, 1])
            with col3:
                avg_per_week = stats.get('total_workouts', 0) / max(1, stats.get('weeks_active', 1))
                st.markdown(f"""
                <div class="stat-box glow-effect">
                    <svg class="progress-ring" viewBox="0 0 50 50">
                        <circle cx="25" cy="25" r="20" stroke="rgba(255,215,0,0.2)" stroke-width="3" fill="none"/>
                        <circle cx="25" cy="25" r="20" stroke="#FFD700" stroke-width="3" fill="none" 
                                stroke-dasharray="125" stroke-dashoffset="{125 - (min(avg_per_week, 7) / 7) * 125}"
                                class="progress" stroke-linecap="round"/>
                    </svg>
                    <div class="stat-number">{avg_per_week:.1f}</div>
                    <div class="stat-label">Tréninků týdně</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                total_volume = stats.get('total_volume', 0)
                st.markdown(f"""
                <div class="stat-box glow-effect">
                    <svg class="progress-ring" viewBox="0 0 50 50">
                        <circle cx="25" cy="25" r="20" stroke="rgba(255,215,0,0.2)" stroke-width="3" fill="none"/>
                        <circle cx="25" cy="25" r="20" stroke="#FFD700" stroke-width="3" fill="none" 
                                stroke-dasharray="125" stroke-dashoffset="{125 - (min(total_volume, 10000) / 10000) * 125}"
                                class="progress" stroke-linecap="round"/>
                    </svg>
                    <div class="stat-number">{total_volume:,.0f}</div>
                    <div class="stat-label">Celkový objem (kg)</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error("Nepodařilo se načíst statistiky")
    
    st.markdown("---")
    
    # Workout Templates section
    st.subheader("📝 Šablony tréninků")
    
    # Load saved templates
    if 'workout_templates' not in st.session_state:
        st.session_state['workout_templates'] = [
            {
                'name': 'Push Day',
                'description': 'Hrudník, ramena, triceps',
                'exercises': ['Bench Press', 'Overhead Press', 'Tricep Dips'],
                'color': '#FF6B6B'
            },
            {
                'name': 'Pull Day', 
                'description': 'Záda, biceps',
                'exercises': ['Pull-ups', 'Barbell Rows', 'Bicep Curls'],
                'color': '#4ECDC4'
            },
            {
                'name': 'Leg Day',
                'description': 'Nohy, gluteus',
                'exercises': ['Squats', 'Deadlifts', 'Leg Press'],
                'color': '#45B7D1'
            }
        ]
    
    template_cols = st.columns(3)
    for idx, template in enumerate(st.session_state['workout_templates']):
        with template_cols[idx % 3]:
            if st.button(f"🏋️ {template['name']}", key=f"template_{idx}", use_container_width=True):
                # Create workout from template
                template_exercises = []
                for ex_name in template['exercises']:
                    template_exercises.append({
                        'name': ex_name,
                        'sets': 3,
                        'reps': 10,
                        'weight': None
                    })
                
                payload = {
                    'date': date.today().isoformat(),
                    'note': f'Vytvořeno ze šablony: {template["name"]}',
                    'exercises': template_exercises
                }
                
                r = session.post(f"{API_BASE}/workouts", json=payload, timeout=5)
                if r.ok:
                    show_toast(f"Trénink '{template['name']}' vytvořen!")
                    st.session_state['page'] = 'workouts'
                    st.rerun()
            
            st.markdown(f"""
            <div class="template-card">
                <small style="color: var(--muted);">{template['description']}</small><br>
                <small style="color: var(--primary);">{len(template['exercises'])} cviků</small>
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
    
    # 1RM Calculator section
    st.markdown("## 💪 1RM Kalkulátor")
    st.markdown('<div class="rm-calculator">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        rm_weight = st.number_input("Váha (kg)", min_value=1.0, value=100.0, step=2.5, key="rm_weight")
    with col2:
        rm_reps = st.number_input("Počet opakování", min_value=1, max_value=20, value=5, key="rm_reps")
    with col3:
        if st.button("Vypočítat 1RM", use_container_width=True):
            one_rm = calculate_1rm(rm_weight, rm_reps)
            st.markdown(f'<div class="rm-result">{one_rm:.1f} kg</div>', unsafe_allow_html=True)
            
            # Show percentage recommendations
            st.markdown("**Doporučené zatížení:**")
            percentages = [(50, "Zahřívání"), (70, "Objemový"), (85, "Silový"), (95, "Maximální")]
            for pct, desc in percentages:
                weight = one_rm * (pct / 100)
                st.write(f"• {pct}%: {weight:.1f} kg ({desc})")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Loading state for data
    data_placeholder = st.empty()
    with data_placeholder.container():
        show_loading("Načítám data pro analýzy...")
    
    r = session.get(f"{API_BASE}/workouts", timeout=5)
    data_placeholder.empty()
    
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
    fig_freq.update_traces(line_color='#FFD700', line_width=4, fill='tozeroy', 
                          fillcolor='rgba(255,215,0,0.3)',
                          mode='lines+markers',
                          marker=dict(size=8, color='#FFD700', line=dict(width=2, color='#FFED4E')))
    fig_freq.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff', family='Poppins'),
        title_font_size=22,
        title_font_color='#FFD700',
        hovermode='x unified',
        xaxis=dict(gridcolor='rgba(255,215,0,0.1)', showgrid=True),
        yaxis=dict(gridcolor='rgba(255,215,0,0.1)', showgrid=True),
        hoverlabel=dict(bgcolor='rgba(255,215,0,0.9)', font_color='black'),
        margin=dict(t=50, b=50, l=50, r=50)
    )
    st.markdown('<div class="neon-graph">', unsafe_allow_html=True)
    st.plotly_chart(fig_freq, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
    st.markdown('<div class="neon-graph">', unsafe_allow_html=True)
    st.plotly_chart(fig_top, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
    st.markdown('<div class="neon-graph">', unsafe_allow_html=True)
    st.plotly_chart(fig_volume, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # === BODY HEATMAP ANALYSIS ===
    st.markdown("## 🗺️ Body Heatmap - Analýza zatížení svalových skupin")
    
    # Categorize exercises by muscle groups
    def get_muscle_group(name):
        name_lower = name.lower()
        muscle_map = {
            'hrudník': ['bench', 'tlak', 'press', 'fly'],
            'záda': ['pull', 'tah', 'row', 'deadlift', 'mrtvý'],
            'ramena': ['shoulder', 'rameno', 'lateral', 'overhead'],
            'biceps': ['curl', 'bicep'],
            'triceps': ['tricep', 'extension', 'dip'],
            'nohy': ['squat', 'dřep', 'leg', 'lunge'],
            'core': ['plank', 'abs', 'crunch']
        }
        
        for muscle, keywords in muscle_map.items():
            if any(keyword in name_lower for keyword in keywords):
                return muscle
        return 'ostatní'
    
    if ex_rows:
        df['muscle_group'] = df['name'].apply(get_muscle_group)
        muscle_volume = df.groupby('muscle_group')['volume'].sum().sort_values(ascending=False)
        
        # Create body heatmap visualization
        fig_body = px.pie(muscle_volume.reset_index(), values='volume', names='muscle_group',
                         title='Rozložení tréninku podle svalových skupin',
                         template='plotly_dark',
                         color_discrete_sequence=['#FFD700', '#FFED4E', '#FFA500', '#FF8C00', '#FF6347', '#FF4500', '#DC143C'])
        fig_body.update_layout(
            paper_bgcolor='#000000',
            font_color='#ffffff',
            title_font_size=20
        )
        st.plotly_chart(fig_body, use_container_width=True)
        
        # Muscle group recommendations
        st.markdown("**📊 Doporučení pro vyvážený trénink:**")
        total_vol = muscle_volume.sum()
        for muscle, volume in muscle_volume.head(3).items():
            percentage = (volume / total_vol) * 100
            if percentage > 40:
                st.warning(f"⚠️ {muscle.title()}: {percentage:.1f}% - Zvažte více variety")
            elif percentage > 25:
                st.info(f"✅ {muscle.title()}: {percentage:.1f}% - Dobré zatížení")
            else:
                st.success(f"🎯 {muscle.title()}: {percentage:.1f}% - Vyvážené")
    
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

    # === PERFORMANCE SCORE ===
    st.markdown("## 🎯 Performance Score")
    
    if len(workouts) >= 2:
        # Calculate performance score based on multiple factors
        recent_workouts = len([w for w in workouts if pd.to_datetime(w['date']) > pd.Timestamp.now() - pd.Timedelta(days=30)])
        consistency_score = min(recent_workouts * 5, 40)  # Max 40 points for consistency
        
        volume_trend = 0
        if len(df) >= 10:
            recent_volume = df[df['date'] > df['date'].max() - pd.Timedelta(days=30)]['volume'].sum()
            older_volume = df[df['date'] <= df['date'].max() - pd.Timedelta(days=30)]['volume'].sum()
            if older_volume > 0:
                volume_trend = min((recent_volume / older_volume - 1) * 100, 30)  # Max 30 points
        
        variety_score = min(df['name'].nunique() * 2, 30)  # Max 30 points for exercise variety
        
        total_score = consistency_score + max(volume_trend, 0) + variety_score
        
        # Display performance score
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔁 Konzistence", f"{consistency_score:.0f}/40")
        with col2:
            st.metric("📈 Progres", f"{max(volume_trend, 0):.0f}/30")
        with col3:
            st.metric("🎲 Variabilita", f"{variety_score:.0f}/30")
        with col4:
            score_color = "green" if total_score >= 70 else "orange" if total_score >= 50 else "red"
            st.metric("🏆 Celkové skóre", f"{total_score:.0f}/100")
        
        # Performance insights
        st.markdown("**🧠 Vhled do vášeho výkonu:**")
        if total_score >= 80:
            st.success("🎆 Vynikající! Jste na správné cestě k dosažení svých cílů.")
        elif total_score >= 60:
            st.info("💪 Dobrá práce! Zkuste přidat více variety nebo konzistence.")
        else:
            st.warning("🎯 Je čas zvýšit intenzitu! Zkuste pravidelnější trénink.")
    
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
    
    # Header with actions
    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button("📋 Ze šablony", use_container_width=True):
            st.session_state['show_templates'] = True
            st.rerun()
    with col3:
        if st.button("➕ Nový trénink", use_container_width=True):
            st.session_state['page'] = 'new_workout'
            st.rerun()
    
    # Show template selection if requested
    if st.session_state.get('show_templates', False):
        st.subheader("📝 Vyberte šablonu")
        template_cols = st.columns(3)
        for idx, template in enumerate(st.session_state.get('workout_templates', [])):
            with template_cols[idx % 3]:
                if st.button(f"{template['name']}", key=f"wt_{idx}", use_container_width=True):
                    # Create from template logic here
                    st.session_state['show_templates'] = False
                    st.rerun()
        
        if st.button("❌ Zrušit", key="cancel_templates"):
            st.session_state['show_templates'] = False
            st.rerun()
        st.markdown("---")
    
    # Loading state
    workouts_placeholder = st.empty()
    with workouts_placeholder.container():
        show_loading("Načítám tréninky...")
    
    r = session.get(f"{API_BASE}/workouts", timeout=5)
    workouts_placeholder.empty()
    
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
    
    # Loading state
    detail_placeholder = st.empty()
    with detail_placeholder.container():
        show_loading("Načítám detail tréninku...")
    
    r = session.get(f"{API_BASE}/workouts/{wid}", timeout=5)
    detail_placeholder.empty()
    
    if not r.ok:
        st.error("Trénink nenalezen")
        return
    
    workout = _safe_json(r).get('workout')
    
    # Header with actions
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f'<div class="main-header">🏋️ Trénink z {workout["date"]}</div>', unsafe_allow_html=True)
    with col2:
        if st.button("🔄 Duplikovat", use_container_width=True):
            # Create duplicate workout
            exercises = [{
                'name': ex['name'],
                'sets': ex['sets'],
                'reps': ex['reps'],
                'weight': ex.get('weight')
            } for ex in workout.get('exercises', [])]
            
            payload = {
                'date': date.today().isoformat(),
                'note': f"Kopie: {workout.get('note', '')}",
                'exercises': exercises
            }
            
            dup_r = session.post(f"{API_BASE}/workouts", json=payload, timeout=5)
            if dup_r.ok:
                show_toast("Trénink duplikovan!")
                new_id = _safe_json(dup_r).get('id')
                st.session_state['selected_workout'] = new_id
                st.rerun()
    with col3:
        if st.button("🗑️ Smazat trénink", use_container_width=True):
            r = session.delete(f"{API_BASE}/workouts/{wid}", timeout=5)
            if r.ok:
                show_toast("Trénink smazán!")
                st.session_state['page'] = 'workouts'
                st.rerun()
    
    st.write(f"**Poznámka:** {workout.get('note', 'Bez poznámky')}")
    
    # REST Timer section
    st.markdown("---")
    st.subheader("⏱️ REST Timer")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        rest_minutes = st.selectbox("Minuty", range(0, 10), index=2, key="rest_min")
    with col2:
        rest_seconds = st.selectbox("Sekundy", range(0, 60, 15), index=0, key="rest_sec")
    with col3:
        if st.button("▶️ Start REST Timer", use_container_width=True):
            total_seconds = rest_minutes * 60 + rest_seconds
            if total_seconds > 0:
                st.info(f"⏰ REST Timer nastaven na {rest_minutes}:{rest_seconds:02d}")
                show_toast(f"REST Timer: {rest_minutes}:{rest_seconds:02d}")
    
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
    
    # Quick template buttons
    st.subheader("🚀 Rychlé vytvoření")
    template_cols = st.columns(4)
    templates = st.session_state.get('workout_templates', [])
    for idx, template in enumerate(templates[:4]):
        with template_cols[idx]:
            if st.button(f"📋 {template['name']}", key=f"quick_{idx}", use_container_width=True):
                # Pre-fill form with template
                st.session_state['prefill_exercises'] = template['exercises']
                st.rerun()
    
    # Copy from previous workout
    if st.button("📋 Kopírovat poslední trénink", use_container_width=True):
        try:
            r = session.get(f"{API_BASE}/workouts", timeout=5)
            if r.ok:
                workouts = _safe_json(r).get('workouts', [])
                if workouts:
                    latest = workouts[0]
                    wr = session.get(f"{API_BASE}/workouts/{latest['id']}", timeout=5)
                    if wr.ok:
                        detail = _safe_json(wr).get('workout', {})
                        exercises = [ex['name'] for ex in detail.get('exercises', [])]
                        st.session_state['prefill_exercises'] = exercises
                        show_toast("Poslední trénink načten!")
                        st.rerun()
        except Exception:
            st.error("Nepodařilo se načíst poslední trénink")
    
    st.markdown("---")
    
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
    
    st.markdown('<div class="main-header">⚙️ Správce</div>', unsafe_allow_html=True)
    
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


def achievements_page():
    """Stránka úspěchů a sledování pokroku"""
    st.markdown('<div class="main-header">🏆 Úspěchy & Pokrok</div>', unsafe_allow_html=True)
    
    # Současný streak
    streak = calculate_workout_streak()
    st.markdown(f'''
    <div class="streak-counter">
        <div class="streak-number">{streak}</div>
        <div class="streak-label">Denní série</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Activity heatmap
    st.markdown("#### 🗺️ Mapa aktivity (Poslední rok)")
    try:
        r = session.get(f"{API_BASE}/workouts", timeout=10)
        workouts = _safe_json(r).get('workouts', []) if r.ok else []
        heatmap_html = create_activity_heatmap(workouts)
        if heatmap_html:
            st.markdown(heatmap_html, unsafe_allow_html=True)
        else:
            st.info("Začněte cvičit a uvidíte zde mapu své aktivity!")
    except Exception:
        st.error("Nepodařilo se načíst data aktivity")
    
    # Showcase úspěchů
    st.markdown("#### 🎆 Vaše úspěchy")
    earned = st.session_state.get('earned_achievements', [])
    
    # Mock stats pro kontrolu achievementů
    try:
        r = session.get(f"{API_BASE}/stats", timeout=5)
        stats = _safe_json(r).get('stats', {}) if r.ok else {}
    except Exception:
        stats = {}
    
    achievements = check_achievements(stats)
    
    # Zobrazení nových úspěchů
    if achievements:
        for achievement in achievements:
            if achievement['id'] not in st.session_state.get('earned_achievements', []):
                st.balloons()  # Oslava
                st.success(f"🎉 Nový úspěch odemčen: {achievement['name']}")
    
    all_achievements = [
        {'id': 'first_workout', 'name': '🏋️ První trénink', 'desc': 'Započal jsi svou fitness cestu!'},
        {'id': 'ten_workouts', 'name': '💪 Desítka', 'desc': '10 tréninků dokončeno!'},
        {'id': 'fifty_workouts', 'name': '🎯 Padesátka', 'desc': '50 tréninků - jsi na správné cestě!'},
        {'id': 'volume_1k', 'name': '🚀 1000kg Club', 'desc': 'Celkový objem přes 1000kg!'},
        {'id': 'streak_3', 'name': '🔥 Trojka', 'desc': '3 dny v řadě!'},
        {'id': 'streak_7', 'name': '⚡ Týdenní válečník', 'desc': '7 dní streak!'}
    ]
    
    cols = st.columns(2)
    for i, achievement in enumerate(all_achievements):
        with cols[i % 2]:
            is_earned = achievement['id'] in earned
            opacity = '1' if is_earned else '0.3'
            st.markdown(f'''
            <div style="opacity: {opacity}; margin: 10px 0;">
                <div class="achievement-badge">
                    {achievement['name']}
                </div>
                <div style="font-size: 0.9rem; color: #888; margin-top: 4px;">
                    {achievement['desc']}
                </div>
            </div>
            ''', unsafe_allow_html=True)


def tools_page():
    """Stránka fitness nástrojů a kalkulátorů"""
    st.markdown('<div class="main-header">⚙️ Fitness nástroje</div>', unsafe_allow_html=True)
    
    tool_tabs = st.tabs(["🏋️ 1RM kalkulátor", "🎯 Kalkulátor kotoučů", "📊 Sledování pokroku"])
    
    # 1RM Calculator
    with tool_tabs[0]:
        st.markdown('<div class="rm-calculator">', unsafe_allow_html=True)
        st.markdown("#### Kalkulátor maximálního opakování")
        
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("Váha (kg)", min_value=1.0, max_value=500.0, value=100.0, step=2.5)
        with col2:
            reps = st.number_input("Počet opakování", min_value=1, max_value=50, value=5)
        
        if st.button("Vypočítat 1RM", type="primary"):
            one_rm = calculate_1rm(weight, reps)
            st.markdown(f'<div class="rm-result">{one_rm:.1f} kg</div>', unsafe_allow_html=True)
            
            # Show percentage breakdown
            st.markdown("**Tréninkové procenta:**")
            percentages = [95, 90, 85, 80, 75, 70, 65]
            cols = st.columns(4)
            for i, pct in enumerate(percentages):
                with cols[i % 4]:
                    training_weight = one_rm * (pct / 100)
                    st.metric(f"{pct}%", f"{training_weight:.1f} kg")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Plate Calculator
    with tool_tabs[1]:
        st.markdown("#### 🏋 Kalkulátor kotoučů")
        
        col1, col2 = st.columns(2)
        with col1:
            target = st.number_input("Cílová váha (kg)", min_value=20.0, max_value=500.0, value=100.0, step=2.5)
        with col2:
            barbell = st.number_input("Váha činky (kg)", min_value=15.0, max_value=25.0, value=20.0, step=2.5)
        
        if st.button("Vypočítat kotouče", type="primary"):
            plates = calculate_plate_distribution(target, barbell)
            
            if plates:
                st.markdown("**Rozmístění kotoučů (každá strana):**")
                plate_visual = render_plate_visual(plates)
                st.markdown(plate_visual, unsafe_allow_html=True)
                
                # Show plate breakdown
                from collections import Counter
                plate_counts = Counter(plates)
                
                st.markdown("**Potřebné kotouče (každá strana):**")
                for plate, count in sorted(plate_counts.items(), reverse=True):
                    st.write(f"- {count}x {plate}kg kotouče")
            else:
                st.warning("Cílová váha je příliš nízká nebo se rovná váze činky!")
    
    # Progress Tracker
    with tool_tabs[2]:
        st.markdown("#### 📈 Sledování pokroku")
        st.info("Připravuje se - Sledujte svůj pokrok v čase s pokročilou analytikou!")
        
        # Preview of future features
        st.markdown("**Připravované funkce:**")
        st.markdown("""
        - 📊 Grafy progrese síly
        - 📏 Sledování tělesných rozměrů  
        - 📸 Časová osa fotografií pokroku
        - 🎯 Stanovení a sledování cílů
        - 📱 Chytrá doporučení tréninků
        """)


def pwa_setup_page():
    """Stránka nastavení progresivní webové aplikace a offline funkcí"""
    st.markdown('<div class="main-header">📱 Instalace mobilní aplikace</div>', unsafe_allow_html=True)
    
    st.markdown("""
    #### Nainstalujte FitTrack jako mobilní aplikaci
    
    **Pro Android/Chrome:**
    1. Otevřete tuto stránku v prohlížeči Chrome
    2. Klepněte na menu (tři tečky) → "Přidat na plochu"
    3. Vyberte název aplikace a klepněte na "Přidat"
    
    **Pro iPhone/Safari:**
    1. Otevřete tuto stránku v Safari
    2. Klepněte na tlačítko Sdílet → "Přidat na plochu"
    3. Vyberte název aplikace a klepněte na "Přidat"
    
    **Pro počítač:**
    1. Hledejte ikonu instalace v adresním řádku
    2. Klikněte na "Instalovat FitTrack"
    
    #### Offline funkce
    - Zobrazení historie tréninků
    - Použití fitness kalkulátorů
    - Plánování tréninků pomocí šablon
    
    *Poznámka: Vytváření nových tréninků vyžaduje připojení k internetu.*
    """)
    
    # Kontrola PWA stavu
    st.markdown("#### 🔍 Stav PWA")
    
    # Simulace kontroly PWA možností
    if st.button("Zkontrolovat podporu PWA", type="primary"):
        st.success("✅ Váš prohlížeč podporuje instalaci PWA!")
        st.info("📶 Offline režim: Omezená funkcionalita dostupná")
        st.warning("⚠️ Úplná offline synchronizace: Připravuje se v další aktualizaci")
    
    # Showcase funkcí
    st.markdown("#### 🚀 Funkce aplikace")
    
    features = [
        {"icon": "🏋️", "title": "Sledování tréninků", "desc": "Zaznamenávejte cviky, série a opakování"},
        {"icon": "📊", "title": "Analýza pokroku", "desc": "Vizualizujte svou fitness cestu"},
        {"icon": "🎯", "title": "Stanovení cílů", "desc": "Nastavte a sledujte fitness cíle"},
        {"icon": "📱", "title": "Mobilní přívětivost", "desc": "Ideální pro použití v posilovně"},
        {"icon": "🔄", "title": "Synchronizace", "desc": "Přístup k datům odkudkoliv"},
        {"icon": "⚡", "title": "Rychlý výkon", "desc": "Optimalizováno pro rychlé načítání"}
    ]
    
    cols = st.columns(2)
    for i, feature in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="padding: 15px; margin: 10px 0; border-left: 4px solid #FFD700;">
                <div style="font-size: 1.5rem;">{feature['icon']} <strong>{feature['title']}</strong></div>
                <div style="color: #888; margin-top: 5px;">{feature['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # PWA Manifest a Service Worker
    st.markdown("""
    <script>
    // PWA Installation prompt
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        // Show install button
        console.log('PWA install prompt available');
    });
    
    // Register Service Worker for PWA
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('SW registered: ', registration);
            })
            .catch(function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
    }
    </script>
    """, unsafe_allow_html=True)


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
    # Responsive sidebar header
    st.markdown("<h1 style='font-size: 1.5rem; margin-bottom: 1rem;'>💪 FitTrack</h1>", unsafe_allow_html=True)
    user_info = st.session_state.get('user', {})
    st.markdown(f"<p style='color: var(--primary); font-weight: 600;'>👤 {user_info.get('username', 'User')}</p>", unsafe_allow_html=True)
    
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
        'dashboard': '📊 Přehled',
    'stats': '📈 Statistiky',
        'workouts': '💪 Moje tréninky',
        'new_workout': '➕ Nový trénink',
        'achievements': '🏆 Úspěchy',
        'tools': '⚙️ Nástroje',
        'pwa_setup': '📱 Mobilní aplikace',
        'catalog': '📚 Katalog cviků',
        'export': '📥 Export',
    }
    
    if user_info.get('is_admin'):
        pages['admin'] = '⚙️ Správa'
    
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
elif page == 'achievements':
    achievements_page()
elif page == 'tools':
    tools_page()
elif page == 'pwa_setup':
    pwa_setup_page()
elif page == 'catalog':
    catalog_page()
elif page == 'export':
    export_page()
elif page == 'admin':
    admin_page()
