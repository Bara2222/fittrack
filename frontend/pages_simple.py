"""
Pages Module
Contains page rendering functions for FitTrack frontend
"""
import streamlit as st
from config import API_BASE
from components import render_app_header, render_footer, show_loading, show_empty_state, lazy_load_image
from auth import _safe_json, _display_api_error
from cache_utils import get_exercise_catalog


def landing_page():
    """Landing page with intro and login button"""
    from auth import login_page
    
    # Check if we should show login or register form
    if st.session_state.get('show_login_form', False) or st.session_state.get('show_register_form', False):
        login_page()
        st.stop()
        return
    
    # Render header with login button
    render_app_header()

    # Hero section
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px 30px 20px; background: #000000; max-width: 1200px; margin: 0 auto;">
        <div class="hero-subtitle">VÁŠE FITNESS NA PRVNÍM MÍSTĚ</div>
        <h1 class="main-header">FitTrack</h1>
        <div class="hero-description">
            Profesionální tréninkový deník pro maximalizaci vašich výsledků.<br>
            Sledujte pokrok, plánujte tréninky a dosahujte cílů efektivněji než kdy předtím.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Add spacing
    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

    # Feature cards - better centered
    col_space1, col1, col2, col3, col_space2 = st.columns([0.5, 1, 1, 1, 0.5])
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="card-icon">📊</div>
            <div class="card-title">Detailní statistiky</div>
            <div class="card-description">
                Komplexní přehled vašeho pokroku s grafickou vizualizací výkonů a analýzou trendů.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="card-icon">💪</div>
            <div class="card-title">Plánování tréninků</div>
            <div class="card-description">
                Rozsáhlá databáze cvičení s možností vytváření vlastních tréninkových plánů na míru.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="card-icon">🌐</div>
            <div class="card-title">Webová aplikace</div>
            <div class="card-description">
                Přístup kdykoliv a odkudkoliv prostřednictvím moderního webového rozhraní.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Why FitTrack section
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    .benefit-box {
        padding: 20px;
        background: #0a0a0a;
        border-left: 4px solid #ffd700;
        border-radius: 12px;
        margin-bottom: 15px;
    }
    .benefit-title {
        color: #ffd700;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .benefit-desc {
        color: #cccccc;
        font-size: 14px;
        line-height: 1.6;
    }
    .cta-section {
        text-align: center;
        padding: 2rem 1.5rem;
        background: #0a0a0a;
        border-radius: 20px;
        margin: 20px 0;
    }
    .cta-title {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .cta-subtitle {
        color: #cccccc;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    .stats-row {
        display: flex;
        justify-content: center;
        gap: 3rem;
        margin-bottom: 1.5rem;
    }
    .stat-item {
        text-align: center;
    }
    .stat-number {
        font-size: 2.2rem;
        font-weight: 900;
        color: #ffd700;
        margin-bottom: 0.2rem;
    }
    .stat-label {
        color: #ffffff;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    </style>
    <div style='text-align: center; padding: 30px 20px 20px 20px; max-width: 1200px; margin: 0 auto;'>
        <h2 style='font-size: 32px; font-weight: 800; color: #ffd700; margin-bottom: 25px; text-transform: uppercase; letter-spacing: 1px;'>Proč FitTrack?</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Benefits with better spacing
    col_space1, col1, col2, col_space2 = st.columns([0.5, 1, 1, 0.5])
    with col1:
        st.markdown("""
        <div class='benefit-box'>
            <h4 class='benefit-title'>✓ Jednoduché a intuitivní</h4>
            <p class='benefit-desc'>
                Začněte cvičit během několika sekund. Žádné složité nastavení ani komplikace.
            </p>
        </div>
        <div class='benefit-box'>
            <h4 class='benefit-title'>✓ Profesionální nástroje</h4>
            <p class='benefit-desc'>
                Vše co potřebujete pro efektivní sledování pokroku na jednom místě.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='benefit-box'>
            <h4 class='benefit-title'>✓ Rychlý start</h4>
            <p class='benefit-desc'>
                Předpřipravené tréninkové plány pro začátečníky i pokročilé sportovce.
            </p>
        </div>
        <div class='benefit-box'>
            <h4 class='benefit-title'>✓ Vaše data v bezpečí</h4>
            <p class='benefit-desc'>
                Maximální ochrana vašich osobních údajů a tréninkové historie.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # Call to action - centered and clean
    st.markdown("""
    <div style='max-width: 1200px; margin: 0 auto;'>
        <div class='cta-section'>
            <h2 class='cta-title'>Připraveni změnit své fitness?</h2>
            <p class='cta-subtitle'>Začněte sledovat své tréninky ještě dnes</p>
            <div class='stats-row'>
                <div class='stat-item'>
                    <div class='stat-number'>100+</div>
                    <div class='stat-label'>Cvičení</div>
                </div>
                <div class='stat-item'>
                    <div class='stat-number'>24/7</div>
                    <div class='stat-label'>Přístup</div>
                </div>
                <div class='stat-item'>
                    <div class='stat-number'>∞</div>
                    <div class='stat-label'>Možnosti</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Button centered
    col_space1, c2, col_space2 = st.columns([1, 1, 1])
    with c2:
        if st.button("🚀 ZAČÍT CVIČIT", use_container_width=True, type="primary", key="cta_button"):
            st.session_state['show_login_form'] = True
            st.rerun()
    
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
    
    render_footer()
    st.stop()


def catalog_page():
    """Exercise catalog page with cached data"""
    
    st.markdown('<div class="main-header">📚 Katalog cviků</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Use cached exercise catalog
    EXERCISE_CATALOG = get_exercise_catalog()
    
    # Initialize selected exercises in session state
    if 'workout_builder' not in st.session_state:
        st.session_state['workout_builder'] = []
    
    # Show selected exercises summary
    if st.session_state['workout_builder']:
        st.success(f"✅ Vybráno {len(st.session_state['workout_builder'])} cviků pro trénink")
        cols = st.columns([3, 1])
        with cols[0]:
            selected_names = [ex['name'] for ex in st.session_state['workout_builder']]
            st.write(f"**Vybrané cviky:** {', '.join(selected_names)}")
        with cols[1]:
            if st.button("🗑️ Vymazat výběr", use_container_width=True):
                st.session_state['workout_builder'] = []
                st.rerun()
        
        if st.button("➕ Vytvořit trénink s těmito cviky", type="primary", use_container_width=True):
            st.session_state['page'] = 'new_workout'
            st.rerun()
        st.markdown("---")
    
    # Filter by category
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🎯 Filtrovat podle svalové skupiny")
    
    # Get all categories from EXERCISE_CATALOG dictionary keys
    categories = ['Vše'] + list(EXERCISE_CATALOG.keys())
    selected_category = st.selectbox("Kategorie", categories, key="catalog_filter")
    
    # Filter exercises - flatten the dictionary structure
    if selected_category == 'Vše':
        filtered = []
        for category, exercises in EXERCISE_CATALOG.items():
            for ex in exercises:
                ex_copy = ex.copy()
                ex_copy['category'] = category
                filtered.append(ex_copy)
    else:
        filtered = []
        for ex in EXERCISE_CATALOG.get(selected_category, []):
            ex_copy = ex.copy()
            ex_copy['category'] = selected_category
            filtered.append(ex_copy)
    
    if not filtered:
        show_empty_state(
            "📭",
            "Žádné cviky",
            "Pro vybranou kategorii nejsou k dispozici žádné cviky."
        )
        return
    
    # Display exercises in cards
    st.markdown(f"**Nalezeno {len(filtered)} cviků**")
    
    for ex in filtered:
        with st.expander(f"💪 {ex.get('name', 'Bez názvu')}"):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**Kategorie:** {ex.get('category', 'Ostatní')}")
                st.markdown(f"**Obtížnost:** {ex.get('difficulty', 'Střední')}")
                st.markdown("---")
                
                # Check if already selected
                already_selected = any(
                    sel_ex['name'] == ex.get('name') 
                    for sel_ex in st.session_state['workout_builder']
                )
                
                if already_selected:
                    st.success("✅ Přidáno")
                    if st.button("➖ Odebrat", key=f"remove_{ex.get('name')}", use_container_width=True):
                        st.session_state['workout_builder'] = [
                            sel_ex for sel_ex in st.session_state['workout_builder'] 
                            if sel_ex['name'] != ex.get('name')
                        ]
                        st.rerun()
                else:
                    if st.button("➕ Přidat do tréninku", key=f"add_{ex.get('name')}", use_container_width=True):
                        st.session_state['workout_builder'].append({
                            'name': ex.get('name'),
                            'category': ex.get('category', 'Ostatní'),
                            'difficulty': ex.get('difficulty', 'Střední')
                        })
                        st.rerun()
            
            with col2:
                st.markdown(f"**Popis:** {ex.get('description', 'Bez popisu')}")
                
                if ex.get('tips'):
                    st.markdown("**💡 Tipy:**")
                    for tip in ex['tips']:
                        st.markdown(f"• {tip}")


def export_page():
    """Data export page"""
    st.markdown('<div class="main-header">📥 Export dat</div>', unsafe_allow_html=True)
    
    st.info("💡 Exportujte svá tréninkové data do CSV formátu pro další analýzu.")
    
    session = st.session_state['session']
    
    if st.button("📥 Stáhnout CSV", use_container_width=True, type="primary"):
        with st.spinner("Generuji export..."):
            try:
                r = session.get(f"{API_BASE}/export/csv", timeout=10)
                if r.ok:
                    # Offer download
                    st.download_button(
                        label="💾 Uložit soubor",
                        data=r.content,
                        file_name="fittrack_export.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    st.success("✅ Export připraven ke stažení!")
                else:
                    _display_api_error(r, "Export dat")
            except Exception as e:
                st.error(f"❌ Chyba při exportu: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 📊 Co export obsahuje?")
    st.markdown("""
    - **Tréninky**: Datum, název, poznámky
    - **Cviky**: Název cviku, série, opakování, váha
    - **Statistiky**: Celkový objem, počet tréninků
    """)
