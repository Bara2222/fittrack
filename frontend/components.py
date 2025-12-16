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


def show_toast(message, toast_type="success", duration=3000):
    """
    Show modern toast notification with animation
    Types: success, error, warning, info
    """
    icons = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️"
    }
    
    colors = {
        "success": "#10b981",
        "error": "#ef4444",
        "warning": "#f59e0b",
        "info": "#3b82f6"
    }
    
    icon = icons.get(toast_type, "ℹ️")
    color = colors.get(toast_type, "#3b82f6")
    
    toast_id = f"toast_{toast_type}_{hash(message)}"
    
    st.markdown(f"""
    <style>
    @keyframes slideInRight {{
        from {{
            transform: translateX(100%);
            opacity: 0;
        }}
        to {{
            transform: translateX(0);
            opacity: 1;
        }}
    }}
    @keyframes slideOutRight {{
        from {{
            transform: translateX(0);
            opacity: 1;
        }}
        to {{
            transform: translateX(100%);
            opacity: 0;
        }}
    }}
    .toast-notification {{
        position: fixed;
        top: 20px;
        right: 20px;
        background: {color};
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 15px;
        font-weight: 600;
        animation: slideInRight 0.3s ease-out;
        min-width: 300px;
        max-width: 500px;
    }}
    .toast-icon {{
        font-size: 24px;
    }}
    </style>
    <div id="{toast_id}" class="toast-notification">
        <span class="toast-icon">{icon}</span>
        <span>{message}</span>
    </div>
    <script>
        setTimeout(() => {{
            const toast = document.getElementById('{toast_id}');
            if (toast) {{
                toast.style.animation = 'slideOutRight 0.3s ease-out';
                setTimeout(() => toast.remove(), 300);
            }}
        }}, {duration});
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
    """Show modern empty state with illustration"""
    st.markdown(f"""
    <style>
    .empty-state {{
        text-align: center;
        padding: 60px 20px;
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        border-radius: 20px;
        margin: 40px 0;
        border: 2px solid #2a2a2a;
    }}
    .empty-state-icon {{
        font-size: 80px;
        margin-bottom: 20px;
        opacity: 0.8;
        animation: float 3s ease-in-out infinite;
    }}
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-10px); }}
    }}
    .empty-state-title {{
        font-size: 28px;
        font-weight: 800;
        color: #ffd700;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .empty-state-text {{
        font-size: 16px;
        color: #cccccc;
        margin-bottom: 30px;
        line-height: 1.6;
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;
    }}
    </style>
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


def lazy_load_image(image_url, alt_text="", placeholder_height="200px"):
    """Lazy load images with Intersection Observer"""
    unique_id = f"img_{hash(image_url)}"
    st.markdown(f"""
    <style>
    .lazy-image-container {{
        width: 100%;
        height: {placeholder_height};
        background: linear-gradient(90deg, #1a1a1a 25%, #2a2a2a 50%, #1a1a1a 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 12px;
        overflow: hidden;
    }}
    @keyframes shimmer {{
        0% {{ background-position: -200% 0; }}
        100% {{ background-position: 200% 0; }}
    }}
    .lazy-image {{
        width: 100%;
        height: auto;
        opacity: 0;
        transition: opacity 0.5s ease-in;
    }}
    .lazy-image.loaded {{
        opacity: 1;
    }}
    </style>
    <div class="lazy-image-container" id="container_{unique_id}">
        <img 
            data-src="{image_url}" 
            alt="{alt_text}"
            class="lazy-image"
            id="{unique_id}"
        />
    </div>
    <script>
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.onload = () => {{
                        img.classList.add('loaded');
                        img.parentElement.style.height = 'auto';
                        img.parentElement.style.background = 'none';
                    }};
                    observer.unobserve(img);
                }}
            }});
        }}, {{ threshold: 0.1 }});
        
        const lazyImage = document.getElementById('{unique_id}');
        if (lazyImage) observer.observe(lazyImage);
    </script>
    """, unsafe_allow_html=True)


def render_app_header(show_time=True, show_login_button=True):
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
                # Open settings page
                st.session_state['page'] = 'settings'
                st.rerun()
        else:
            # Only show login button if show_login_button is True
            if show_login_button:
                if st.button("🔐 Přihlásit se", use_container_width=True, type="primary"):
                    st.session_state['show_login_form'] = True
                    st.rerun()
            else:
                st.write("")


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
        
        if st.button("📋 Plány tréninků", use_container_width=True, type="primary" if current_page == 'workout_plans' else "secondary"):
            st.session_state['page'] = 'workout_plans'
            st.rerun()
        
        if st.button("🎯 Cíle", use_container_width=True, type="primary" if current_page == 'goals' else "secondary"):
            st.session_state['page'] = 'goals'
            st.rerun()
        
        if st.button("🏆 Úspěchy", use_container_width=True, type="primary" if current_page == 'achievements' else "secondary"):
            st.session_state['page'] = 'achievements'
            st.rerun()
        
        if st.button("⚙️ Nástroje", use_container_width=True, type="primary" if current_page == 'tools' else "secondary"):
            st.session_state['page'] = 'tools'
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
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0; color: #888;">
        <p style="margin: 5px 0;">© {current_year} FitTrack. Všechna práva vyhrazena.</p>
        <p style="margin: 5px 0; font-size: 14px;">
            🎓 Maturitní závěrečná práce | Vytvořeno s ❤️ pro fitness nadšence
        </p>
    </div>
    """, unsafe_allow_html=True)
