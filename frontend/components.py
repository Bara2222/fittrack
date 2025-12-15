"""
UI Components Module
Reusable UI components and widgets for FitTrack frontend
"""
import streamlit as st


def show_loading(text="Načítám..."):
    """Show loading spinner with text"""
    st.markdown(f"""
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <p class="loading-text">{text}</p>
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


def confirm_dialog(title, message, confirm_key):
    """Show confirmation dialog"""
    if f'confirm_{confirm_key}' not in st.session_state:
        st.session_state[f'confirm_{confirm_key}'] = False
    
    if not st.session_state[f'confirm_{confirm_key}']:
        st.warning(f"⚠️ **{title}**")
        st.write(message)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Ano, pokračovat", key=f"yes_{confirm_key}", use_container_width=True):
                st.session_state[f'confirm_{confirm_key}'] = True
                st.rerun()
        with col2:
            if st.button("❌ Zrušit", key=f"no_{confirm_key}", use_container_width=True):
                st.session_state[f'confirm_{confirm_key}'] = False
                return False
        return False
    else:
        # Reset confirmation after action
        st.session_state[f'confirm_{confirm_key}'] = False
        return True


def show_empty_state(icon, title, message, button_text=None, button_action=None):
    """Show empty state with optional action button"""
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-state-icon">{icon}</div>
        <div class="empty-state-title">{title}</div>
        <div class="empty-state-text">{message}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if button_text and button_action:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(button_text, use_container_width=True, type="primary"):
                button_action()


def render_app_header(show_time=True):
    """Render top navigation bar with optional time display and login/user info"""
    from datetime import datetime
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 2rem;">💪</span>
            <span style="font-size: 1.5rem; font-weight: 700; color: #ffd700;">FitTrack</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Empty space where time used to be
        st.write("")
    
    with col3:
        if st.session_state.get('logged_in'):
            user = st.session_state.get('user', {})
            username = user.get('username', 'Uživatel')
            if st.button(f"👤 {username}", use_container_width=True):
                # Open profile editor directly
                st.session_state['page'] = 'dashboard'
                st.session_state['edit_profile'] = True
                st.rerun()
        else:
            if st.button("🔐 Přihlásit se", use_container_width=True, type="primary"):
                st.session_state['show_login_form'] = True
                st.rerun()


def render_sidebar_navigation():
    """Render sidebar navigation for logged-in users"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <span style="font-size: 2.5rem;">💪</span><br>
            <span style="font-size: 1.8rem; font-weight: 800; color: #ffd700;">FitTrack</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation buttons
        current_page = st.session_state.get('page', 'dashboard')
        
        if st.button("📊 Dashboard", use_container_width=True, type="primary" if current_page == 'dashboard' else "secondary"):
            st.session_state['page'] = 'dashboard'
            st.rerun()
        
        if st.button("💪 Moje tréninky", use_container_width=True, type="primary" if current_page == 'workouts' else "secondary"):
            st.session_state['page'] = 'workouts'
            st.rerun()
        
        if st.button("📈 Statistiky", use_container_width=True, type="primary" if current_page == 'statistics' else "secondary"):
            st.session_state['page'] = 'statistics'
            st.rerun()
        
        if st.button("📚 Katalog cviků", use_container_width=True, type="primary" if current_page == 'catalog' else "secondary"):
            st.session_state['page'] = 'catalog'
            st.rerun()
        
        if st.button("📥 Export dat", use_container_width=True, type="primary" if current_page == 'export' else "secondary"):
            st.session_state['page'] = 'export'
            st.rerun()
        
        # Admin section if user is admin
        user = st.session_state.get('user', {})
        if user.get('is_admin'):
            st.markdown("---")
            st.markdown("**Admin**")
            if st.button("⚙️ Administrace", use_container_width=True, type="primary" if current_page == 'admin' else "secondary"):
                st.session_state['page'] = 'admin'
                st.rerun()
        
        st.markdown("---")
        
        # Logout button at bottom
        from auth import logout
        if st.button("🚪 Odhlásit se", use_container_width=True):
            logout()
        else:
            if st.button("🔐 Přihlásit se", use_container_width=True, type="primary"):
                st.session_state['show_login_form'] = True
                st.rerun()


def render_footer():
    """Render footer at the bottom of every page"""
    from datetime import datetime
    current_year = datetime.now().year
    
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
