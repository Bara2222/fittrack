"""
Admin, Achievements, and Tools Pages Module
Manages user administration, achievements tracking, and fitness tools
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta

from config import API_BASE
from auth import _safe_json, _display_api_error
from utils import calculate_1rm


def admin_page():
    """Admin panel for managing users"""
    session = st.session_state['session']
    
    # Check if user is admin
    if not st.session_state.get('user', {}).get('is_admin'):
        st.error("❌ Nemáte oprávnění pro přístup na tuto stránku")
        return
    
    st.markdown('<div class="main-header">⚙️ Správce</div>', unsafe_allow_html=True)
    
    # Load users
    try:
        r = session.get(f"{API_BASE}/admin/users", timeout=5)
        if not r.ok:
            st.error("❌ Chyba při načítání uživatelů")
            return
        
        users = _safe_json(r).get('users', [])
    except Exception as e:
        st.error(f"❌ Chyba připojení: {str(e)}")
        return
    
    st.subheader(f"👥 Celkem uživatelů: {len(users)}")
    
    # Create DataFrame
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
    
    if df_data:
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Žádní uživatelé")


def achievements_page():
    """Achievements and progress tracking page"""
    st.markdown('<div class="main-header">🏆 Úspěchy & Pokrok</div>', unsafe_allow_html=True)
    
    session = st.session_state['session']
    
    # Calculate workout streak
    try:
        r = session.get(f"{API_BASE}/workouts", timeout=5)
        workouts = _safe_json(r).get('workouts', []) if r.ok else []
        
        # Simple streak calculation: count consecutive days
        if workouts:
            dates = sorted([datetime.fromisoformat(w['date']).date() for w in workouts])
            streak = 1
            for i in range(len(dates) - 1, 0, -1):
                if (dates[i-1] - dates[i]).days == -1:
                    streak += 1
                else:
                    break
        else:
            streak = 0
    except Exception:
        streak = 0
    
    # Display streak counter
    st.markdown(f'''
    <div style="text-align: center; margin: 30px 0; padding: 30px; background: linear-gradient(135deg, #FFD700, #FFED4E); border-radius: 15px;">
        <div style="font-size: 3rem; font-weight: bold; color: #000;">{streak}</div>
        <div style="font-size: 1.2rem; color: #000; font-weight: 600;">Denní série 🔥</div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Get statistics for achievements
    try:
        r = session.get(f"{API_BASE}/stats", timeout=5)
        stats = _safe_json(r).get('stats', {}) if r.ok else {}
    except Exception:
        stats = {}
    
    # Define all achievements
    all_achievements = [
        {'id': 'first_workout', 'name': '🏋️ První trénink', 'desc': 'Započal jsi svou fitness cestu!', 'condition': stats.get('total_workouts', 0) >= 1},
        {'id': 'ten_workouts', 'name': '💪 Desítka', 'desc': '10 tréninků dokončeno!', 'condition': stats.get('total_workouts', 0) >= 10},
        {'id': 'fifty_workouts', 'name': '🎯 Padesátka', 'desc': '50 tréninků - jsi na správné cestě!', 'condition': stats.get('total_workouts', 0) >= 50},
        {'id': 'volume_1k', 'name': '🚀 1000kg Club', 'desc': 'Celkový objem přes 1000kg!', 'condition': stats.get('total_volume', 0) >= 1000},
        {'id': 'streak_3', 'name': '🔥 Trojka', 'desc': '3 dny v řadě!', 'condition': streak >= 3},
        {'id': 'streak_7', 'name': '⚡ Týdenní válečník', 'desc': '7 dní streak!', 'condition': streak >= 7}
    ]
    
    st.markdown("#### 🎆 Vaše úspěchy")
    cols = st.columns(2)
    for i, achievement in enumerate(all_achievements):
        with cols[i % 2]:
            opacity = '1' if achievement['condition'] else '0.3'
            status = '✅' if achievement['condition'] else '🔒'
            st.markdown(f'''
            <div style="opacity: {opacity}; margin: 15px 0; padding: 15px; border: 2px solid #FFD700; border-radius: 8px;">
                <div style="font-size: 1.1rem; font-weight: bold;">
                    {status} {achievement['name']}
                </div>
                <div style="font-size: 0.9rem; color: #999; margin-top: 8px;">
                    {achievement['desc']}
                </div>
            </div>
            ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Show stats summary
    st.markdown("#### 📊 Váš přehled")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🏋️ Tréninků", stats.get('total_workouts', 0))
    with col2:
        st.metric("🏋️ Cviků", stats.get('recent_exercises', 0))
    with col3:
        st.metric("⚖️ Celkový objem", f"{stats.get('total_volume', 0):,.0f} kg")


def tools_page():
    """Fitness tools and calculators page"""
    st.markdown('<div class="main-header">⚙️ Fitness nástroje</div>', unsafe_allow_html=True)
    
    tool_tabs = st.tabs(["🏋️ 1RM kalkulátor", "🎯 Kalkulátor kotoučů"])
    
    # 1RM Calculator
    with tool_tabs[0]:
        st.markdown("#### 💪 Kalkulátor maximálního opakování")
        
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("Váha (kg)", min_value=1.0, max_value=500.0, value=100.0, step=2.5, key="rm_weight_tools")
        with col2:
            reps = st.number_input("Počet opakování", min_value=1, max_value=50, value=5, key="rm_reps_tools")
        
        if st.button("Vypočítat 1RM", type="primary", use_container_width=True):
            one_rm = calculate_1rm(weight, reps)
            st.markdown(f'<div style="text-align: center; font-size: 2.5rem; font-weight: bold; color: #FFD700; margin: 20px 0;">{one_rm:.1f} kg</div>', unsafe_allow_html=True)
            
            # Show percentage breakdown
            st.markdown("**Tréninkové procenta:**")
            percentages = [95, 90, 85, 80, 75, 70, 65]
            cols = st.columns(4)
            for i, pct in enumerate(percentages):
                with cols[i % 4]:
                    training_weight = one_rm * (pct / 100)
                    st.metric(f"{pct}%", f"{training_weight:.1f} kg")
    
    # Plate Calculator
    with tool_tabs[1]:
        st.markdown("#### 🏋️ Kalkulátor kotoučů")
        
        col1, col2 = st.columns(2)
        with col1:
            target = st.number_input("Cílová váha (kg)", min_value=20.0, max_value=500.0, value=100.0, step=2.5, key="plate_target")
        with col2:
            barbell = st.number_input("Váha činky (kg)", min_value=15.0, max_value=25.0, value=20.0, step=2.5, key="plate_barbell")
        
        if st.button("Vypočítat kotouče", type="primary", use_container_width=True):
            plates = calculate_plate_distribution(target, barbell)
            
            if plates:
                st.markdown("**Rozmístění kotoučů (každá strana):**")
                
                # Show plate breakdown
                from collections import Counter
                plate_counts = Counter(plates)
                
                st.markdown("**Potřebné kotouče (každá strana):**")
                for plate, count in sorted(plate_counts.items(), reverse=True):
                    st.write(f"• {count}x {plate}kg kotouč{'e' if count > 1 else ''}")
                
                # Visual representation
                st.markdown("**Vizuální znázornění:**")
                visual_str = "Činка " + " | ".join([f"{p}kg" for p in plates]) + " | Činка"
                st.code(visual_str)
            else:
                st.warning("❌ Cílová váha je příliš nízká nebo se rovná váze činky!")


def pwa_setup_page():
    """Progressive Web App installation and offline features"""
    st.markdown('<div class="main-header">📱 Instalace mobilní aplikace</div>', unsafe_allow_html=True)
    
    # Installation instructions
    st.markdown("""
    #### 🚀 Nainstalujte FitTrack jako mobilní aplikaci
    
    **Pro Android/Chrome:**
    1. Otevřete tuto stránku v prohlížeči Chrome
    2. Klepněte na menu (tři tečky) → "Přidat na plochu"
    3. Vyberte název aplikace a klepněte na "Přidat"
    
    **Pro iPhone/Safari:**
    1. Otevřete tuto stránku v Safari
    2. Klepněte na tlačítko Sdílet → "Přidat na plochu"
    3. Vyberte název aplikace a klepněte na "Přidat"
    
    **Pro počítač/Desktop:**
    1. Hledejte ikonu instalace v adresním řádku
    2. Klikněte na "Instalovat FitTrack"
    """)
    
    st.markdown("---")
    
    # Offline features
    st.markdown("#### 📶 Offline funkce")
    st.markdown("""
    ✅ Dostupné v offline režimu:
    - Zobrazení historie tréninků (z cache)
    - Použití fitness kalkulátorů (1RM, kotouče)
    - Prohlížení šablon tréninků
    - Čtení detailů jednotlivých tréninků
    
    ❌ Vyžaduje připojení:
    - Vytváření nových tréninků
    - Synchronizace dat
    - Přístup k pokročilým statistikám
    
    *Poznámka: Offline data jsou automaticky synchronizovány při obnovení spojení.*
    """)
    
    st.markdown("---")
    
    # Features showcase
    st.markdown("#### 🎯 Funkce aplikace")
    
    features = [
        {"icon": "🏋️", "title": "Sledování tréninků", "desc": "Zaznamenávejte cviky, série a opakování"},
        {"icon": "📊", "title": "Analýza pokroku", "desc": "Vizualizujte svou fitness cestu"},
        {"icon": "🎯", "title": "Účetnictví cílů", "desc": "Nastavte a sledujte fitness cíle"},
        {"icon": "📱", "title": "Mobilní přívětivost", "desc": "Ideální pro použití v posilovně"},
        {"icon": "🔄", "title": "Synchronizace", "desc": "Přístup k datům odkudkoliv"},
        {"icon": "⚡", "title": "Rychlý výkon", "desc": "Optimalizováno pro rychlé načítání"}
    ]
    
    cols = st.columns(2)
    for i, feature in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="padding: 15px; margin: 10px 0; border-left: 4px solid #FFD700; border-radius: 4px; background: rgba(255,215,0,0.1);">
                <div style="font-size: 1.3rem; font-weight: bold; margin-bottom: 8px;">{feature['icon']} {feature['title']}</div>
                <div style="color: #999;">{feature['desc']}</div>
            </div>
            """, unsafe_allow_html=True)


# Helper functions for calculators
def calculate_plate_distribution(target, barbell):
    """Calculate which plates are needed to reach target weight"""
    if target <= barbell:
        return None
    
    # Available plates (in kg)
    available_plates = [25, 20, 15, 10, 7.5, 5, 2.5, 2, 1.5, 1, 0.5]
    
    # Calculate weight per side
    weight_per_side = (target - barbell) / 2
    
    plates = []
    remaining = weight_per_side
    
    for plate_weight in available_plates:
        while remaining >= plate_weight:
            plates.append(plate_weight)
            remaining -= plate_weight
    
    # Check if we can make exact weight
    if abs(remaining) < 0.01:
        return sorted(plates, reverse=True)
    
    return None
