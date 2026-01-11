"""
Extra Pages Module
Contains achievements, tools and other additional pages for FitTrack frontend
"""
import streamlit as st
from config import API_BASE
from auth import _safe_json
from datetime import datetime, timedelta
from collections import Counter


def calculate_workout_streak():
    """Calculate current workout streak (consecutive days)"""
    session = st.session_state['session']
    try:
        r = session.get(f"{API_BASE}/workouts", timeout=5)
        if r.ok:
            workouts = _safe_json(r).get('workouts', [])
            if not workouts:
                return 0
            
            # Sort by date
            dates = sorted([datetime.fromisoformat(w['date'].replace('Z', '+00:00')).date() 
                          for w in workouts], reverse=True)
            
            if not dates:
                return 0
            
            # Check if most recent workout was today or yesterday
            today = datetime.now().date()
            if dates[0] not in [today, today - timedelta(days=1)]:
                return 0
            
            # Count consecutive days
            streak = 1
            expected_date = dates[0] - timedelta(days=1)
            
            for date in dates[1:]:
                if date == expected_date:
                    streak += 1
                    expected_date -= timedelta(days=1)
                elif date < expected_date:
                    break
            
            return streak
    except Exception:
        return 0
    return 0


def calculate_1rm(weight, reps):
    """Calculate one-rep max using Epley formula"""
    if reps == 1:
        return weight
    return weight * (1 + reps / 30.0)


def calculate_plate_distribution(target_weight, barbell_weight):
    """Calculate plate distribution for target weight"""
    available_plates = [25, 20, 15, 10, 5, 2.5, 1.25]
    
    # Calculate weight needed per side
    weight_per_side = (target_weight - barbell_weight) / 2
    
    if weight_per_side <= 0:
        return []
    
    plates = []
    remaining = weight_per_side
    
    for plate in available_plates:
        while remaining >= plate:
            plates.append(plate)
            remaining -= plate
    
    return plates


def achievements_page():
    """Stránka úspěchů a sledování pokroku"""
    st.markdown('<div class="main-header">🏆 Úspěchy & Pokrok</div>', unsafe_allow_html=True)
    
    # Současný streak
    streak = calculate_workout_streak()
    st.markdown(f'''
    <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
         border-radius: 20px; margin: 20px 0;">
        <div style="font-size: 4rem; font-weight: 900; color: #ffd700;">{streak}</div>
        <div style="font-size: 1.2rem; color: #ffffff; margin-top: 10px;">Denní série 🔥</div>
        <div style="font-size: 0.9rem; color: #888; margin-top: 5px;">
            {'Skvělá práce! Pokračuj!' if streak > 0 else 'Začni dnes a vybuduj si sérii!'}
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Mock stats pro kontrolu achievementů
    session = st.session_state['session']
    try:
        r = session.get(f"{API_BASE}/stats", timeout=5)
        stats = _safe_json(r).get('stats', {}) if r.ok else {}
        total_workouts = stats.get('total_workouts', 0)
        total_volume = stats.get('total_volume', 0)
    except Exception:
        total_workouts = 0
        total_volume = 0
    
    # Initialize earned achievements
    if 'earned_achievements' not in st.session_state:
        st.session_state['earned_achievements'] = []
    
    # All possible achievements
    all_achievements = [
        {'id': 'first_workout', 'name': '🏋️ První trénink', 'desc': 'Započal jsi svou fitness cestu!', 'condition': total_workouts >= 1},
        {'id': 'ten_workouts', 'name': '💪 Desítka', 'desc': '10 tréninků dokončeno!', 'condition': total_workouts >= 10},
        {'id': 'fifty_workouts', 'name': '🎯 Padesátka', 'desc': '50 tréninků - jsi na správné cestě!', 'condition': total_workouts >= 50},
        {'id': 'hundred_workouts', 'name': '💯 Stovka', 'desc': '100 tréninků! Jsi legenda!', 'condition': total_workouts >= 100},
        {'id': 'volume_1k', 'name': '🚀 1000kg Club', 'desc': 'Celkový objem přes 1000kg!', 'condition': total_volume >= 1000},
        {'id': 'volume_10k', 'name': '⭐ 10000kg Club', 'desc': 'Celkový objem přes 10000kg!', 'condition': total_volume >= 10000},
        {'id': 'streak_3', 'name': '🔥 Trojka', 'desc': '3 dny v řadě!', 'condition': streak >= 3},
        {'id': 'streak_7', 'name': '⚡ Týdenní válečník', 'desc': '7 dní streak!', 'condition': streak >= 7},
        {'id': 'streak_30', 'name': '👑 Měsíční král', 'desc': '30 dní streak!', 'condition': streak >= 30},
    ]
    
    # Check and award new achievements
    for achievement in all_achievements:
        if achievement['condition'] and achievement['id'] not in st.session_state['earned_achievements']:
            st.session_state['earned_achievements'].append(achievement['id'])
            st.balloons()
            st.success(f"🎉 Nový úspěch odemčen: {achievement['name']}")
    
    # Zobrazení úspěchů
    st.markdown("### 🎆 Vaše úspěchy")
    st.markdown("<br>", unsafe_allow_html=True)
    
    earned = st.session_state.get('earned_achievements', [])
    
    cols = st.columns(3)
    for i, achievement in enumerate(all_achievements):
        with cols[i % 3]:
            is_earned = achievement['id'] in earned
            opacity = '1' if is_earned else '0.4'
            border_color = '#ffd700' if is_earned else '#333'
            
            st.markdown(f'''
            <div style="opacity: {opacity}; margin: 10px 0; padding: 20px; background: #1a1a1a; 
                 border: 2px solid {border_color}; border-radius: 12px; text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 10px;">
                    {achievement['name'].split()[0]}
                </div>
                <div style="font-size: 1rem; font-weight: 700; color: #ffffff; margin-bottom: 5px;">
                    {' '.join(achievement['name'].split()[1:])}
                </div>
                <div style="font-size: 0.85rem; color: #888;">
                    {achievement['desc']}
                </div>
            </div>
            ''', unsafe_allow_html=True)


def tools_page():
    """Stránka fitness nástrojů a kalkulátorů"""
    st.markdown('<div class="main-header">⚙️ Fitness nástroje</div>', unsafe_allow_html=True)
    
    tool_tabs = st.tabs(["🏋️ 1RM kalkulátor", "🎯 Kalkulátor kotoučů", "📊 BMI kalkulátor"])
    
    # 1RM Calculator
    with tool_tabs[0]:
        st.markdown("### Kalkulátor maximálního opakování")
        st.markdown("Vypočítejte své teoretické maximum na jedno opakování (1RM) podle váhy a počtu opakování.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("Váha (kg)", min_value=1.0, max_value=500.0, value=100.0, step=2.5)
        with col2:
            reps = st.number_input("Počet opakování", min_value=1, max_value=50, value=5)
        
        if st.button("Vypočítat 1RM", type="primary", use_container_width=True):
            one_rm = calculate_1rm(weight, reps)
            
            st.markdown(f'''
            <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
                 border-radius: 15px; margin: 20px 0;">
                <div style="font-size: 3rem; font-weight: 900; color: #ffd700;">{one_rm:.1f} kg</div>
                <div style="font-size: 1rem; color: #ffffff; margin-top: 10px;">Vaše odhadované 1RM</div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Show percentage breakdown
            st.markdown("**Tréninkové procenta:**")
            percentages = [95, 90, 85, 80, 75, 70, 65, 60]
            
            for i in range(0, len(percentages), 4):
                cols = st.columns(4)
                for j, pct in enumerate(percentages[i:i+4]):
                    with cols[j]:
                        training_weight = one_rm * (pct / 100)
                        st.metric(f"{pct}%", f"{training_weight:.1f} kg")
    
    # Plate Calculator
    with tool_tabs[1]:
        st.markdown("### 🏋 Kalkulátor kotoučů")
        st.markdown("Zjistěte, které kotouče potřebujete na každou stranu činky pro dosažení cílové váhy.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            target = st.number_input("Cílová váha (kg)", min_value=20.0, max_value=500.0, value=100.0, step=2.5, key="plate_target")
        with col2:
            barbell = st.number_input("Váha činky (kg)", min_value=15.0, max_value=25.0, value=20.0, step=2.5, key="plate_barbell")
        
        if st.button("Vypočítat kotouče", type="primary", use_container_width=True):
            plates = calculate_plate_distribution(target, barbell)
            
            if plates:
                st.success(f"Pro dosažení {target}kg s činkou {barbell}kg potřebujete:")
                
                # Show plate breakdown
                plate_counts = Counter(plates)
                
                st.markdown("**Potřebné kotouče na každou stranu:**")
                for plate, count in sorted(plate_counts.items(), reverse=True):
                    st.markdown(f"- **{count}x** kotouč **{plate}kg**")
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.info(f"💡 Celková váha: {target}kg = Činka ({barbell}kg) + Kotouče ({sum(plates) * 2}kg)")
            else:
                st.warning("Cílová váha je příliš nízká nebo se rovná váze činky!")
    
    # BMI Calculator
    with tool_tabs[2]:
        st.markdown("### 📊 BMI kalkulátor")
        st.markdown("Vypočítejte svůj Body Mass Index (BMI).")
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            height = st.number_input("Výška (cm)", min_value=100, max_value=250, value=175)
        with col2:
            weight_bmi = st.number_input("Váha (kg)", min_value=30.0, max_value=300.0, value=75.0, step=0.5, key="bmi_weight")
        
        if st.button("Vypočítat BMI", type="primary", use_container_width=True):
            height_m = height / 100
            bmi = weight_bmi / (height_m ** 2)
            
            # Determine category
            if bmi < 18.5:
                category = "Podváha"
                color = "#3b82f6"
            elif bmi < 25:
                category = "Normální váha"
                color = "#22c55e"
            elif bmi < 30:
                category = "Nadváha"
                color = "#f59e0b"
            else:
                category = "Obezita"
                color = "#ef4444"
            
            st.markdown(f'''
            <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
                 border-radius: 15px; margin: 20px 0;">
                <div style="font-size: 3rem; font-weight: 900; color: {color};">{bmi:.1f}</div>
                <div style="font-size: 1.2rem; color: #ffffff; margin-top: 10px;">{category}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            st.markdown("**Interpretace BMI:**")
            st.markdown("- **< 18.5**: Podváha")
            st.markdown("- **18.5 - 24.9**: Normální váha")
            st.markdown("- **25 - 29.9**: Nadváha")
            st.markdown("- **≥ 30**: Obezita")


def settings_page():
    """Stránka nastavení aplikace"""
    st.markdown('<div class="main-header">⚙️ Nastavení</div>', unsafe_allow_html=True)
    
    st.markdown("### 👤 Profil")
    user = st.session_state.get('user', {})
    
    # Get values with safe defaults - handle None values
    user_age = int(user.get('age') or 25)
    user_height = int(user.get('height_cm') or 175)
    user_weight = float(user.get('weight_kg') or 75.0)
    
    # Ensure values are within valid ranges
    user_age = max(13, min(100, user_age))
    user_height = max(120, min(250, user_height))
    user_weight = max(30.0, min(300.0, user_weight))
    
    # Show current BMI
    if user_height > 0:
        current_bmi = user_weight / ((user_height / 100) ** 2)
        
        # Determine BMI category and color
        if current_bmi < 18.5:
            bmi_category = "Podváha"
            bmi_color = "#3b82f6"
        elif current_bmi < 25:
            bmi_category = "Normální váha"
            bmi_color = "#22c55e"
        elif current_bmi < 30:
            bmi_category = "Nadváha"
            bmi_color = "#f59e0b"
        else:
            bmi_category = "Obezita"
            bmi_color = "#ef4444"
        
        st.markdown(f"""
        <div style="padding: 15px; background: #1a1a1a; border-left: 4px solid {bmi_color}; 
             border-radius: 12px; margin-bottom: 20px;">
            <div style="font-size: 0.9rem; color: #888; margin-bottom: 5px;">Váš aktuální BMI:</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {bmi_color};">
                {current_bmi:.1f} <span style="font-size: 1rem; color: #ffffff;">({bmi_category})</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.form("settings_form"):
        # Account info (read-only)
        st.markdown("**Informace o účtu:**")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Uživatelské jméno", value=user.get('username', ''), disabled=True)
        with col2:
            st.text_input("Email", value=user.get('email', ''), disabled=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Editable personal info
        st.markdown("**Osobní údaje:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            age = st.number_input(
                "Věk", 
                min_value=13, 
                max_value=100, 
                value=user_age, 
                step=1,
                help="Zadejte váš věk (13-100 let)"
            )
        
        with col2:
            height = st.number_input(
                "Výška (cm)", 
                min_value=120, 
                max_value=250, 
                value=user_height, 
                step=1,
                help="Zadejte výšku v centimetrech"
            )
        
        with col3:
            weight = st.number_input(
                "Váha (kg)", 
                min_value=30.0, 
                max_value=300.0, 
                value=user_weight, 
                step=0.1,
                help="Zadejte váhu v kilogramech"
            )
        
        # Show live BMI calculation preview
        if height > 0 and weight > 0:
            new_bmi = weight / ((height / 100) ** 2)
            
            # Determine new BMI category
            if new_bmi < 18.5:
                new_bmi_category = "Podváha"
                new_bmi_color = "#3b82f6"
                new_bmi_icon = "⚠️"
            elif new_bmi < 25:
                new_bmi_category = "Normální váha"
                new_bmi_color = "#22c55e"
                new_bmi_icon = "✅"
            elif new_bmi < 30:
                new_bmi_category = "Nadváha"
                new_bmi_color = "#f59e0b"
                new_bmi_icon = "⚠️"
            else:
                new_bmi_category = "Obezita"
                new_bmi_color = "#ef4444"
                new_bmi_icon = "⚠️"
            
            st.markdown(f"""
            <div style="padding: 12px; background: #0a0a0a; border: 1px solid {new_bmi_color}; 
                 border-radius: 8px; margin-top: 10px;">
                <div style="font-size: 0.85rem; color: #888;">Nový BMI:</div>
                <div style="font-size: 1.3rem; font-weight: 700; color: {new_bmi_color};">
                    {new_bmi_icon} {new_bmi:.1f} - {new_bmi_category}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show BMI change
            if user_height > 0:
                bmi_change = new_bmi - current_bmi
                if abs(bmi_change) > 0.1:
                    change_color = "#22c55e" if abs(bmi_change) < 3 else "#f59e0b"
                    change_symbol = "↑" if bmi_change > 0 else "↓"
                    st.markdown(f"""
                    <div style="font-size: 0.8rem; color: {change_color}; margin-top: 5px;">
                        Změna: {change_symbol} {abs(bmi_change):.1f} bodů
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Info box with tips
        st.info("""
        💡 **Tipy pro přesné zadání:**
        - Měřte se ráno před jídlem pro konzistentní váhu
        - Výšku měřte bez bot
        - Pravidelně aktualizujte údaje pro přesné statistiky
        """)
        
        submitted = st.form_submit_button("💾 Uložit změny", use_container_width=True, type="primary")
        
        if submitted:
            # Comprehensive validation
            errors = []
            warnings = []
            
            # Age validation
            if age < 13:
                errors.append("❌ Věk musí být minimálně 13 let")
            elif age > 100:
                errors.append("❌ Věk nesmí přesáhnout 100 let")
            elif age < 16:
                warnings.append("⚠️ Pro osoby mladší 16 let doporučujeme konzultaci s trenérem")
            elif age > 70:
                warnings.append("⚠️ Pro osoby starší 70 let doporučujeme konzultaci s lékařem před intenzivním tréninkem")
                
            # Height validation
            if height < 120:
                errors.append("❌ Výška musí být minimálně 120 cm")
            elif height > 250:
                errors.append("❌ Výška nesmí přesáhnout 250 cm")
            elif height < 140:
                warnings.append("⚠️ Zadaná výška je neobvykle nízká. Zkontrolujte prosím správnost údaje.")
            elif height > 220:
                warnings.append("⚠️ Zadaná výška je neobvykle vysoká. Zkontrolujte prosím správnost údaje.")
                
            # Weight validation
            if weight < 30:
                errors.append("❌ Váha musí být minimálně 30 kg")
            elif weight > 300:
                errors.append("❌ Váha nesmí přesáhnout 300 kg")
            elif weight < 40:
                warnings.append("⚠️ Zadaná váha je neobvykle nízká. Zkontrolujte prosím správnost údaje.")
            elif weight > 200:
                warnings.append("⚠️ Zadaná váha je velmi vysoká. Doporučujeme konzultaci s lékařem.")
            
            # BMI validation (comprehensive check)
            height_m = height / 100
            bmi = weight / (height_m ** 2)
            
            if bmi < 12:
                errors.append("❌ Kombinace váhy a výšky není realistická (BMI příliš nízké). Zkontrolujte zadané hodnoty.")
            elif bmi > 50:
                errors.append("❌ Kombinace váhy a výšky není realistická (BMI příliš vysoké). Zkontrolujte zadané hodnoty.")
            elif bmi < 16:
                warnings.append("⚠️ Váš BMI je velmi nízký. Zvažte konzultaci s lékařem nebo nutričním specialistou.")
            elif bmi > 40:
                warnings.append("⚠️ Váš BMI je velmi vysoký. Doporučujeme konzultaci s lékařem před zahájením intenzivního tréninku.")
            
            # Check for major changes
            if user_height > 0 and user_weight > 0:
                old_bmi = user_weight / ((user_height / 100) ** 2)
                bmi_difference = abs(bmi - old_bmi)
                
                if bmi_difference > 5:
                    warnings.append("⚠️ Změna BMI je velmi velká. Zkontrolujte prosím zadané hodnoty.")
                
                weight_change = abs(weight - user_weight)
                if weight_change > 30:
                    warnings.append(f"⚠️ Změna váhy o {weight_change:.1f} kg je velmi velká. Je to správně?")
                
                height_change = abs(height - user_height)
                if height_change > 10:
                    warnings.append(f"⚠️ Změna výšky o {height_change} cm je neobvyklá. Zkontrolujte údaje.")
            
            # Display errors
            if errors:
                st.markdown("### ❌ Chyby ve formuláři:")
                for error in errors:
                    st.error(error)
                st.stop()
            
            # Display warnings
            if warnings:
                st.markdown("### ⚠️ Upozornění:")
                for warning in warnings:
                    st.warning(warning)
                st.markdown("---")
            
            # Save data if no errors
            session = st.session_state['session']
            payload = {
                'age': int(age), 
                'height_cm': int(height), 
                'weight_kg': float(round(weight, 1))
            }
            
            try:
                r = session.post(f"{API_BASE}/profile", json=payload, timeout=5)
                if r.ok:
                    st.success('✅ Profil byl úspěšně aktualizován!')
                    st.balloons()
                    
                    # Update local user state
                    if 'user' not in st.session_state:
                        st.session_state['user'] = {}
                    st.session_state['user'].update(payload)
                    
                    # Show success metrics
                    st.markdown(f"""
                    <div style="padding: 15px; background: #1a1a1a; border-left: 4px solid #22c55e; 
                         border-radius: 12px; margin-top: 10px;">
                        <div style="font-size: 0.9rem; color: #22c55e; font-weight: 700;">
                            📊 Aktualizované údaje:
                        </div>
                        <div style="font-size: 0.85rem; color: #cccccc; margin-top: 8px;">
                            • Věk: {age} let<br>
                            • Výška: {height} cm<br>
                            • Váha: {weight:.1f} kg<br>
                            • BMI: {bmi:.1f} ({new_bmi_category})
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.info("💾 Data byla uložena. Stránka se automaticky obnoví za 2 sekundy...")
                    import time
                    time.sleep(2)
                    st.rerun()
                else:
                    from auth import _display_api_error
                    _display_api_error(r)
            except Exception as e:
                st.error(f'❌ Nepodařilo se kontaktovat API: {str(e)}')
    
    st.markdown("---")
    st.markdown("### 🎨 Vzhled")
    st.info("🚧 Přizpůsobení tématu bude dostupné v příští verzi")
    
    st.markdown("---")
    st.markdown("### 🔔 Notifikace")
    st.info("🚧 Nastavení notifikací bude dostupné v příští verzi")


def workout_plans_page():
    """Stránka plánů tréninků"""
    st.markdown('<div class="main-header">📋 Plány tréninků</div>', unsafe_allow_html=True)
    
    # Initialize workout plans in session state
    if 'workout_plans' not in st.session_state:
        st.session_state['workout_plans'] = []
    
    tabs = st.tabs(["📚 Předpřipravené programy", "✏️ Moje plány", "➕ Vytvořit plán"])
    
    # Tab 1: Pre-made programs
    with tabs[0]:
        st.markdown("### 🏋️ Předpřipravené tréninkové programy")
        st.markdown("Vyberte si program podle své úrovně a cílů:")
        st.markdown("<br>", unsafe_allow_html=True)
        
        programs = [
            {
                'name': '🌱 Začátečník - Full Body',
                'level': 'Začátečník',
                'duration': '4 týdny',
                'frequency': '3x týdně',
                'description': 'Ideální pro začátečníky. Zaměření na základní cviky a správnou techniku.',
                'workouts': [
                    {'day': 'Pondělí', 'exercises': ['Dřep', 'Bench press', 'Mrtvý tah', 'Overhead press']},
                    {'day': 'Středa', 'exercises': ['Dřep', 'Pull-up', 'Incline bench', 'Shrugs']},
                    {'day': 'Pátek', 'exercises': ['Romanian deadlift', 'Dips', 'Rows', 'Lateral raises']}
                ]
            },
            {
                'name': '💪 Střední - Push Pull Legs',
                'level': 'Pokročilý',
                'duration': '8 týdnů',
                'frequency': '6x týdně',
                'description': 'Klasický PPL program pro budování svalové hmoty a síly.',
                'workouts': [
                    {'day': 'Push (Pondělí, Čtvrtek)', 'exercises': ['Bench press', 'Overhead press', 'Incline DB press', 'Lateral raises', 'Triceps']},
                    {'day': 'Pull (Úterý, Pátek)', 'exercises': ['Deadlift', 'Pull-ups', 'Rows', 'Face pulls', 'Biceps']},
                    {'day': 'Legs (Středa, Sobota)', 'exercises': ['Squat', 'Leg press', 'Romanian DL', 'Leg curls', 'Calves']}
                ]
            },
            {
                'name': '🔥 Síla - 5x5',
                'level': 'Pokročilý',
                'duration': '12 týdnů',
                'frequency': '3x týdně',
                'description': 'Program zaměřený na maximální sílu. 5 sérií po 5 opakováních.',
                'workouts': [
                    {'day': 'Trénink A', 'exercises': ['Squat 5x5', 'Bench press 5x5', 'Barbell row 5x5']},
                    {'day': 'Trénink B', 'exercises': ['Squat 5x5', 'Overhead press 5x5', 'Deadlift 1x5']}
                ]
            },
            {
                'name': '🏃 Vytrvalost & Kondice',
                'level': 'Všechny úrovně',
                'duration': '6 týdnů',
                'frequency': '4x týdně',
                'description': 'Kombinace siloviny a kondičních cvičení pro celkovou fitness.',
                'workouts': [
                    {'day': 'HIIT Upper', 'exercises': ['Push-ups', 'Pull-ups', 'Burpees', 'Mountain climbers']},
                    {'day': 'HIIT Lower', 'exercises': ['Jump squats', 'Lunges', 'Box jumps', 'Sprints']},
                    {'day': 'Circuit', 'exercises': ['Kettlebell swings', 'Battle ropes', 'Sled push', 'Row']}
                ]
            }
        ]
        
        for program in programs:
            with st.expander(f"**{program['name']}** - {program['level']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**⏱️ Trvání:** {program['duration']}")
                with col2:
                    st.markdown(f"**📅 Frekvence:** {program['frequency']}")
                with col3:
                    st.markdown(f"**🎯 Úroveň:** {program['level']}")
                
                st.markdown(f"**Popis:** {program['description']}")
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**Rozložení tréninků:**")
                
                for workout in program['workouts']:
                    st.markdown(f"- **{workout['day']}**: {', '.join(workout['exercises'])}")
                
                if st.button(f"✅ Použít program: {program['name']}", key=f"use_{program['name']}", use_container_width=True):
                    st.success(f"Program '{program['name']}' byl přidán do vašich plánů!")
                    st.session_state['workout_plans'].append({
                        'name': program['name'],
                        'type': 'predefined',
                        'data': program
                    })
    
    # Tab 2: My plans
    with tabs[1]:
        st.markdown("### 📝 Moje vytvořené plány")
        
        if not st.session_state.get('workout_plans'):
            st.info("🎯 Zatím nemáte žádné uložené plány. Vytvořte si vlastní nebo použijte předpřipravený program!")
        else:
            for i, plan in enumerate(st.session_state['workout_plans']):
                with st.expander(f"**{plan['name']}**"):
                    st.markdown(f"**Typ:** {'Předpřipravený program' if plan['type'] == 'predefined' else 'Vlastní plán'}")
                    
                    if plan['type'] == 'predefined':
                        data = plan['data']
                        st.markdown(f"**Trvání:** {data['duration']} | **Frekvence:** {data['frequency']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🗑️ Smazat", key=f"delete_plan_{i}", use_container_width=True):
                            st.session_state['workout_plans'].pop(i)
                            st.rerun()
                    with col2:
                        if st.button("📋 Použít dnes", key=f"use_plan_{i}", use_container_width=True):
                            st.session_state['page'] = 'new_workout'
                            st.rerun()
    
    # Tab 3: Create new plan
    with tabs[2]:
        st.markdown("### ✏️ Vytvořit vlastní plán")
        st.markdown("Vytvořte si vlastní tréninkový plán přesně podle vašich představ.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("create_plan_form"):
            plan_name = st.text_input("Název plánu", placeholder="např. Moje Push day")
            plan_description = st.text_area("Popis plánu", placeholder="Stručný popis...")
            
            st.markdown("**Tréninkové dny:**")
            num_days = st.number_input("Počet dní v týdnu", min_value=1, max_value=7, value=3)
            
            st.markdown("**Cviky:** (zadejte názvy cviků oddělené čárkou)")
            exercises = st.text_area("Seznam cviků", placeholder="Bench press, Dřep, Mrtvý tah...")
            
            submitted = st.form_submit_button("💾 Uložit plán", use_container_width=True, type="primary")
            
            if submitted:
                if plan_name and exercises:
                    exercise_list = [ex.strip() for ex in exercises.split(',')]
                    st.session_state['workout_plans'].append({
                        'name': plan_name,
                        'type': 'custom',
                        'description': plan_description,
                        'days': num_days,
                        'exercises': exercise_list
                    })
                    st.success(f"✅ Plán '{plan_name}' byl úspěšně vytvořen!")
                    st.rerun()
                else:
                    st.error("Vyplňte prosím název plánu a seznam cviků!")


def goals_page():
    """Stránka cílů a sledování pokroku"""
    st.markdown('<div class="main-header">🎯 Moje cíle</div>', unsafe_allow_html=True)
    
    # Check user authentication
    current_user = st.session_state.get('user', {})
    if not current_user:
        st.warning("⚠️ Uživatel není správně přihlášen")
        return
    
    # Initialize goals in session state
    if 'fitness_goals' not in st.session_state:
        # Check if this is Emil and initialize his goals
        if current_user and current_user.get('username') == 'Emil':
            try:
                from emil_goals import initialize_emil_goals
                st.session_state['fitness_goals'] = initialize_emil_goals()
                st.success("✅ Cíle úspěšně načteny!")
            except ImportError:
                st.session_state['fitness_goals'] = []
        else:
            st.session_state['fitness_goals'] = []
    
    tabs = st.tabs(["📊 Aktivní cíle", "➕ Přidat cíl", "✅ Dokončené"])
    
    # Tab 1: Active goals
    with tabs[0]:
        st.markdown("### 🎯 Vaše aktivní cíle")
        
        # Add button to load Emil's test goals
        current_user = st.session_state.get('user', {})
        if current_user and current_user.get('username') == 'Emil':
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Načíst testovací cíle", help="Načte přednastavené cíle pro uživatele Emil"):
                    try:
                        from emil_goals import initialize_emil_goals
                        st.session_state['fitness_goals'] = initialize_emil_goals()
                        st.success("✅ Testovací cíle načteny!")
                        st.rerun()
                    except ImportError:
                        st.error("❌ Chyba při načítání testovacích cílů")
        
        active_goals = [g for g in st.session_state.get('fitness_goals', []) if not g.get('completed')]
        
        if not active_goals:
            st.info("🎯 Zatím nemáte žádné aktivní cíle. Začněte tím, že si nějaký vytvoříte!")
            
            # Show hint for Emil
            if current_user and current_user.get('username') == 'Emil':
                st.info("💡 Jako uživatel Emil můžete použít tlačítko '🔄 Načíst testovací cíle' výše.")
        else:
            for i, goal in enumerate(active_goals):
                with st.container():
                    st.markdown(f"""
                    <div style="padding: 25px; background: #1a1a1a; border-left: 4px solid #ffd700; 
                         border-radius: 12px; margin: 20px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
                        <h3 style="color: #ffd700; margin-bottom: 10px; font-size: 1.4em;">{goal['icon']} {goal['name']}</h3>
                        <p style="color: #cccccc; margin-bottom: 20px; font-size: 1.1em;">{goal['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Progress calculation
                    current = goal.get('current', 0)
                    target = goal.get('target', 100)
                    progress = min(100, (current / target * 100)) if target > 0 else 0
                    
                    # Progress bar with better spacing
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.progress(progress / 100)
                    with col2:
                        st.markdown(f"<div style='text-align: center; font-weight: bold; font-size: 1.2em; color: #ffd700;'>{progress:.0f}%</div>", unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Stats with better alignment
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Aktuálně", f"{current:.1f} {goal.get('unit', '')}")
                    with col2:
                        st.metric("Cíl", f"{target:.1f} {goal.get('unit', '')}")
                    with col3:
                        remaining = target - current
                        st.metric("Zbývá", f"{remaining:.1f} {goal.get('unit', '')}")
                    with col4:
                        deadline = goal.get('deadline', 'Neuvedeno')
                        st.metric("Deadline", deadline)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Actions with better layout
                    col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 0.5])
                    with col1:
                        new_value = st.number_input(
                            f"Aktualizovat pokrok", 
                            min_value=0.0, 
                            value=float(current),
                            step=0.5,
                            key=f"update_goal_{i}"
                        )
                    with col2:
                        if st.button("💾 Uložit", key=f"save_goal_{i}", use_container_width=True, type="primary"):
                            st.session_state['fitness_goals'][i]['current'] = new_value
                            if new_value >= target:
                                st.session_state['fitness_goals'][i]['completed'] = True
                                st.balloons()
                                st.success(f"🎉 Gratulujeme! Dosáhli jste cíle: {goal['name']}")
                            st.rerun()
                    with col3:
                        if st.button("🗑️ Smazat", key=f"delete_goal_{i}", use_container_width=True):
                            st.session_state['fitness_goals'].pop(i)
                            st.rerun()
                    
                    # Separator between goals
                    st.markdown("<hr style='margin: 30px 0; border: 1px solid #333;'>", unsafe_allow_html=True)
    
    # Tab 2: Add new goal
    with tabs[1]:
        st.markdown("### ➕ Vytvořit nový cíl")
        st.markdown("Nastavte si konkrétní, měřitelný cíl a sledujte svůj pokrok!")
        st.markdown("<br>", unsafe_allow_html=True)
        
        goal_type = st.selectbox(
            "Typ cíle",
            ["💪 Síla", "⚖️ Váha", "📊 Objem", "🔥 Tréninky", "🎯 Vlastní"]
        )
        
        with st.form("create_goal_form"):
            goal_name = st.text_input("Název cíle", placeholder="např. Dřep 100kg")
            goal_description = st.text_area("Popis cíle", placeholder="Stručný popis vašeho cíle...")
            
            col1, col2 = st.columns(2)
            with col1:
                current_value = st.number_input("Současná hodnota", min_value=0.0, value=0.0, step=0.5)
                target_value = st.number_input("Cílová hodnota", min_value=0.0, value=100.0, step=0.5)
            with col2:
                unit = st.text_input("Jednotka", value="kg", placeholder="kg, count, %...")
                deadline = st.date_input("Deadline (volitelné)")
            
            submitted = st.form_submit_button("🎯 Vytvořit cíl", use_container_width=True, type="primary")
            
            if submitted:
                if goal_name and target_value > 0:
                    # Determine icon based on type
                    icon = goal_type.split()[0]
                    
                    st.session_state['fitness_goals'].append({
                        'name': goal_name,
                        'description': goal_description,
                        'icon': icon,
                        'type': goal_type,
                        'current': current_value,
                        'target': target_value,
                        'unit': unit,
                        'deadline': deadline.strftime('%d.%m.%Y') if deadline else 'Neuvedeno',
                        'completed': False,
                        'created': datetime.now().strftime('%d.%m.%Y')
                    })
                    # Show success message before rerun
                    st.toast(f"✅ Cíl '{goal_name}' byl úspěšně vytvořen! 🎯", icon="✅")
                    st.rerun()
                else:
                    st.error("Vyplňte prosím název cíle a cílovou hodnotu!")
    
    # Tab 3: Completed goals
    with tabs[2]:
        st.markdown("### ✅ Dokončené cíle")
        
        completed_goals = [g for g in st.session_state.get('fitness_goals', []) if g.get('completed')]
        
        if not completed_goals:
            st.info("📝 Zatím jste nedokončili žádný cíl. Pokračujte v tréninku!")
        else:
            st.success(f"🎉 Gratulujeme! Dokončili jste {len(completed_goals)} cíl(ů)!")
            
            for goal in completed_goals:
                st.markdown(f"""
                <div style="padding: 15px; background: #1a1a1a; border-left: 4px solid #22c55e; 
                     border-radius: 12px; margin: 10px 0; opacity: 0.8;">
                    <h4 style="color: #22c55e; margin-bottom: 5px;">✅ {goal['name']}</h4>
                    <p style="color: #888; font-size: 0.9rem;">{goal['description']}</p>
                    <p style="color: #666; font-size: 0.85rem; margin-top: 10px;">
                        Dokončeno: {goal['current']} {goal['unit']} / {goal['target']} {goal['unit']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
