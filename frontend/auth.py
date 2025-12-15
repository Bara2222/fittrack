"""
Authentication module for FitTrack Streamlit application.
Handles login, registration, OAuth, and session management.
"""
import streamlit as st
import requests
from config import API_BASE


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
    """Centralized display for API errors without request IDs."""
    try:
        payload = resp.json()
    except Exception:
        payload = None

    if payload and isinstance(payload, dict):
        msg = payload.get('error') or payload.get('message')
        if msg:
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
        st.error('Neznámá chyba')


def _password_strength(pw: str):
    """Return (score 0-5, color, label, width%)"""
    score = 0
    if len(pw) >= 8:
        score += 1
    if any(c.islower() for c in pw):
        score += 1
    if any(c.isupper() for c in pw):
        score += 1
    if any(c.isdigit() for c in pw):
        score += 1
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in pw):
        score += 1
    
    if score <= 1:
        return score, "#ef4444", "Velmi slabé", "20%"
    elif score == 2:
        return score, "#fb923c", "Slabé", "40%"
    elif score == 3:
        return score, "#fbbf24", "Střední", "60%"
    elif score == 4:
        return score, "#a3e635", "Silné", "80%"
    else:
        return score, "#22c55e", "Velmi silné", "100%"


def initialize_session():
    """Initialize session state for authentication."""
    if 'session' not in st.session_state:
        st.session_state['session'] = requests.Session()
    
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    if 'page' not in st.session_state:
        st.session_state['page'] = 'dashboard'
    if 'show_login_form' not in st.session_state:
        st.session_state['show_login_form'] = False


def check_oauth_callback():
    """Check for Google OAuth callback and handle authentication."""
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
    session = st.session_state['session']
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
    session = st.session_state['session']
    
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
                    st.session_state['user'].update({
                        'age': payload['age'], 
                        'height_cm': payload['height_cm'], 
                        'weight_kg': payload['weight_kg'], 
                        'profile_completed': True
                    })
                    st.rerun()
                else:
                    err = _safe_json(r).get('error')
                    st.error(err or 'Chyba při ukládání profilu')
            except Exception:
                st.error('Nepodařilo se kontaktovat API')
    st.stop()


def login_page():
    """Handle login and registration forms."""
    session = st.session_state['session']
    
    # Toggle back to landing page
    if st.button("← Zpět na hlavní stránku"):
        st.session_state['show_login_form'] = False
        st.session_state['show_register_form'] = False
        st.rerun()

    # Determine which form to show
    show_register = st.session_state.get('show_register_form', False)
    
    if not show_register:
        # LOGIN FORM
        st.markdown('<div class="main-header">🔐 Přihlášení</div>', unsafe_allow_html=True)
        
        with st.form('login_form'):
            username = st.text_input('Uživatelské jméno nebo email')
            password = st.text_input('Heslo', type='password')
            submitted = st.form_submit_button('Přihlásit se', use_container_width=True)
            
            if submitted:
                if not username or not password:
                    st.error('Vyplňte všechna pole')
                else:
                    try:
                        r = session.post(f"{API_BASE}/login", 
                                       json={'username': username, 'password': password}, 
                                       timeout=5)
                        if r.ok:
                            st.session_state['logged_in'] = True
                            user_data = _safe_json(r)
                            st.session_state['user'] = user_data.get('user', {})
                            st.success('Úspěšně přihlášen!')
                            st.rerun()
                        else:
                            _display_api_error(r)
                    except Exception as e:
                        st.error('Nepodařilo se připojit k serveru')

        st.markdown("---")
        # Google OAuth
        oauth_url = f"{API_BASE.replace('/api', '')}/auth/google"
        if st.button("🌐 Přihlásit se přes Google", use_container_width=True):
            st.markdown(f'<meta http-equiv="refresh" content="0; url={oauth_url}">', 
                      unsafe_allow_html=True)
        
        # Link to registration
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; padding: 20px; background: #0a0a0a; border-radius: 12px; margin-top: 20px;'>
            <p style='color: #cccccc; margin-bottom: 10px;'>Nemáte ještě účet?</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📝 Registrujte se", use_container_width=True, type="primary"):
                st.session_state['show_register_form'] = True
                st.rerun()
    
    else:
        # REGISTRATION FORM
        st.markdown('<div class="main-header">📝 Registrace</div>', unsafe_allow_html=True)
        
        with st.form('register_form'):
            username = st.text_input('Uživatelské jméno')
            email = st.text_input('Email')
            password = st.text_input('Heslo', type='password')
            
            # Password strength indicator
            if password:
                score, color, label, width = _password_strength(password)
                st.markdown(f"""
                <div style='margin: 10px 0;'>
                    <div style='font-size: 12px; margin-bottom: 5px;'>Síla hesla: <span style='color: {color}; font-weight: bold;'>{label}</span></div>
                    <div style='background: #333; border-radius: 10px; height: 8px; overflow: hidden;'>
                        <div style='background: {color}; height: 100%; width: {width}; transition: all 0.3s;'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            password2 = st.text_input('Potvrzení hesla', type='password')
            submitted = st.form_submit_button('Registrovat se', use_container_width=True)
            
            if submitted:
                if not all([username, email, password, password2]):
                    st.error('Vyplňte všechna pole')
                elif password != password2:
                    st.error('Hesla se neshodují')
                elif len(password) < 8:
                    st.error('Heslo musí mít alespoň 8 znaků')
                else:
                    try:
                        r = session.post(f"{API_BASE}/register", 
                                       json={
                                           'username': username, 
                                           'email': email, 
                                           'password': password
                                       }, 
                                       timeout=5)
                        if r.ok:
                            st.success('Registrace úspěšná! Nyní se můžete přihlásit.')
                            st.session_state['show_register_form'] = False
                            st.rerun()
                        else:
                            _display_api_error(r)
                    except Exception as e:
                        st.error('Nepodařilo se připojit k serveru')
        
        # Link to login
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; padding: 20px; background: #0a0a0a; border-radius: 12px; margin-top: 20px;'>
            <p style='color: #cccccc; margin-bottom: 10px;'>Už máte účet?</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔐 Přihlásit se", use_container_width=True, type="primary"):
                st.session_state['show_register_form'] = False
                st.rerun()


def logout():
    """Handle user logout."""
    session = st.session_state['session']
    try:
        r = session.post(f"{API_BASE}/logout", timeout=5)
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.session_state['page'] = 'dashboard'
        st.session_state['edit_profile'] = False
        session.cookies.clear()
        st.rerun()
    except Exception:
        # Force logout even if API call fails
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.session_state['page'] = 'dashboard'
        st.session_state['edit_profile'] = False
        session.cookies.clear()
        st.rerun()


# Initialize session state on module import
initialize_session()