"""
Dashboard and Statistics Pages Module
Displays workout statistics, progress tracking, and performance analytics
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta

from config import API_BASE
from components import show_loading, show_empty_state, show_toast
from auth import _safe_json, _display_api_error
from utils import calculate_1rm


def dashboard_page():
    """Display main dashboard with overview and templates"""
    st.markdown('<div class="main-header page-transition">📊 Přehled</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    session = st.session_state['session']
    
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
        st.error("❌ Nepodařilo se načíst statistiky")
        st.info("💡 Zkuste obnovit stránku nebo kontaktujte podporu, pokud problém přetrvává.")
    
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
    
    session = st.session_state['session']
    
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
    
    if len(workouts) < 2:
        st.info("💡 Pro график frekvence potřebujete alespoň 2 tréninky.")
    else:
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
    
    if len(exercise_counts) == 0:
        st.info("💡 Zatím nemáte dost cviků pro analýzu.")
    else:
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

    # === MUSCLE GROUP ANALYSIS ===
    st.markdown("## 🗺️ Analýza zatížení svalových skupin")
    
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
    
    st.markdown("---")

    # === EXERCISE CATEGORIZATION ===
    st.markdown("## 📂 Rozdělení cviků podle kategorie")
    
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
    st.markdown("## 🗓️ Týdenní aktivita")
    
    workout_dates = pd.to_datetime([w['date'] for w in workouts])
    df_workouts = pd.DataFrame({'date': workout_dates})
    df_workouts['weekday'] = df_workouts['date'].dt.day_name()
    
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
