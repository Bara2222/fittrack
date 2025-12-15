"""
Workouts Pages Module
Handles workout listing, creation, and detail views
"""
import streamlit as st
from datetime import date
import pandas as pd

from config import API_BASE
from components import show_loading, show_empty_state, confirm_dialog
from auth import _safe_json, _display_api_error


def workouts_page():
    """Display list of user's workouts with search and filtering"""
    st.markdown('<div class="main-header">💪 Moje tréninky</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    session = st.session_state['session']
    
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
        st.error("❌ Nepodařilo se načíst tréninky")
        return
    
    workouts = r.json().get('workouts', [])
    
    if not workouts:
        def go_to_new_workout():
            st.session_state['page'] = 'new_workout'
            st.rerun()
        
        show_empty_state(
            "💪",
            "Žádné tréninky",
            "Zatím nemáte žádné zaznamenané tréninky. Začněte svou fitness cestu!",
            "➕ Vytvořit první trénink",
            go_to_new_workout
        )
        return
    
    # Search and filtering
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🔍 Vyhledávání a řazení")
    
    search_query = st.text_input(
        "Hledat trénink...",
        placeholder="Vyhledat podle data nebo poznámky",
    )
    
    col1, col2 = st.columns([2, 1])
    with col1:
        sort_by = st.selectbox(
            "Řadit podle:",
            ["Nejnovější první", "Nejstarší první", "Nejvíce cviků", "Nejméně cviků"],
            key="sort_workouts"
        )
    with col2:
        st.markdown(f"**Nalezeno:** {len(workouts)} tréninků")
    
    st.markdown("---")
    
    # Create DataFrame
    df_data = []
    for w in workouts:
        df_data.append({
            'Datum': w['date'],
            'Poznámka': w.get('note', ''),
            'Poznámka_short': w.get('note', '')[:50] + ('...' if len(w.get('note', '')) > 50 else ''),
            'Počet cviků': w['exercise_count'],
            'ID': w['id']
        })
    
    df = pd.DataFrame(df_data)
    
    # Filter by search
    if search_query:
        search_lower = search_query.lower()
        datum_col = df['Datum'].astype(str)
        poznamka_col = df['Poznámka'].astype(str)
        mask = (
            datum_col.str.contains(search_lower, case=False, na=False) |
            poznamka_col.str.contains(search_lower, case=False, na=False)
        )
        df = df[mask]
        
        if len(df) == 0:
            show_empty_state(
                "🔍",
                "Nenalezeny žádné výsledky",
                f"Pro dotaz '{search_query}' nebyly nalezeny žádné tréninky.",
            )
            return
    
    # Sort
    if sort_by == "Nejnovější první":
        df = df.sort_values('Datum', ascending=False)
    elif sort_by == "Nejstarší první":
        df = df.sort_values('Datum', ascending=True)
    elif sort_by == "Nejvíce cviků":
        df = df.sort_values('Počet cviků', ascending=False)
    elif sort_by == "Nejméně cviků":
        df = df.sort_values('Počet cviků', ascending=True)
    
    # Pagination
    items_per_page = 10
    total_pages = (len(df) + items_per_page - 1) // items_per_page
    
    if 'workout_page' not in st.session_state:
        st.session_state['workout_page'] = 1
    
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Předchozí", disabled=(st.session_state['workout_page'] == 1)):
                st.session_state['workout_page'] -= 1
                st.rerun()
        with col2:
            st.markdown(f"<div style='text-align: center; padding: 10px;'>Stránka **{st.session_state['workout_page']}** z **{total_pages}**</div>", unsafe_allow_html=True)
        with col3:
            if st.button("Další ➡️", disabled=(st.session_state['workout_page'] == total_pages)):
                st.session_state['workout_page'] += 1
                st.rerun()
        st.markdown("---")
    
    # Get page items
    start_idx = (st.session_state['workout_page'] - 1) * items_per_page
    end_idx = start_idx + items_per_page
    df_page = df.iloc[start_idx:end_idx]
    
    # Display workouts
    for idx, row in df_page.iterrows():
        col1, col2, col3, col4 = st.columns([2, 4, 2, 2])
        with col1:
            st.write(f"**{row['Datum']}**")
        with col2:
            st.write(row['Poznámka_short'])
        with col3:
            st.write(f"🏋️ {row['Počet cviků']} cviků")
        with col4:
            if st.button("Detail", key=f"view_{row['ID']}"):
                st.session_state['selected_workout'] = row['ID']
                st.session_state['page'] = 'workout_detail'
                st.rerun()
        st.markdown("---")


def workout_detail_page():
    """Display detailed view of a single workout"""
    st.markdown('<div class="main-header">🏋️ Detail tréninku</div>', unsafe_allow_html=True)
    
    session = st.session_state['session']
    
    if 'selected_workout' not in st.session_state:
        st.error("❌ Žádný trénink nebyl vybrán")
        return
    
    wid = st.session_state['selected_workout']
    
    # Loading state
    detail_placeholder = st.empty()
    with detail_placeholder.container():
        show_loading("Načítám detail tréninku...")
    
    r = session.get(f"{API_BASE}/workouts/{wid}", timeout=5)
    detail_placeholder.empty()
    
    if not r.ok:
        st.error("❌ Trénink nenalezen")
        return
    
    workout = _safe_json(r).get('workout')
    
    # Header with actions
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f'<div class="main-header">🏋️ Trénink z {workout["date"]}</div>', unsafe_allow_html=True)
    with col2:
        if st.button("🔄 Duplikovat", use_container_width=True):
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
                st.success("✅ Trénink duplikován!")
                new_id = _safe_json(dup_r).get('id')
                st.session_state['selected_workout'] = new_id
                st.rerun()
    with col3:
        if st.button("🗑️ Smazat", use_container_width=True):
            if confirm_dialog(
                "Smazat trénink?", 
                "Opravdu chcete smazat tento trénink? Tato akce je nevratná!",
                f"delete_workout_{wid}"
            ):
                r = session.delete(f"{API_BASE}/workouts/{wid}", timeout=5)
                if r.ok:
                    st.success("✅ Trénink smazán!")
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
                    if confirm_dialog(
                        "Smazat cvik?",
                        f"Opravdu chcete smazat cvik '{ex['name']}'?",
                        f"delete_exercise_{ex['id']}"
                    ):
                        r = session.delete(f"{API_BASE}/exercises/{ex['id']}", timeout=5)
                        if r.ok:
                            st.success("✅ Cvik smazán!")
                            st.rerun()
            st.markdown("---")
    else:
        show_empty_state("🏋️", "Žádné cviky", "Přidejte první cvik níže!")
    
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
                st.error("❌ Vyplňte název cviku")
            else:
                payload = {
                    'name': ex_name,
                    'sets': ex_sets,
                    'reps': ex_reps,
                    'weight': ex_weight if ex_weight > 0 else None
                }
                r = session.post(f"{API_BASE}/exercises/{wid}/add", json=payload, timeout=5)
                if r.ok:
                    st.success("✅ Cvik přidán!")
                    st.rerun()
                else:
                    st.error("❌ Chyba při přidávání cviku")


def new_workout_page():
    """Create a new workout"""
    st.markdown('<div class="main-header">➕ Nový trénink</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    session = st.session_state['session']
    
    # Check if exercises were selected from catalog
    workout_builder = st.session_state.get('workout_builder', [])
    
    if workout_builder:
        st.info(f"📚 Používáte {len(workout_builder)} cviky z katalogu")
        with st.expander("Zobrazit vybrané cviky"):
            for ex in workout_builder:
                st.write(f"• **{ex['name']}** ({ex['category']} - {ex['difficulty']})")
        
        if st.button("🗑️ Zrušit a vytvořit prázdný trénink"):
            st.session_state['workout_builder'] = []
            st.rerun()
        st.markdown("---")
    
    # Quick template buttons
    st.subheader("🚀 Rychlé vytvoření")
    template_cols = st.columns(4)
    templates = st.session_state.get('workout_templates', [])
    for idx, template in enumerate(templates[:4]):
        with template_cols[idx]:
            if st.button(f"📋 {template['name']}", key=f"quick_{idx}", use_container_width=True):
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
                        st.success("✅ Poslední trénink načten!")
                        st.rerun()
        except Exception:
            st.error("❌ Nepodařilo se načíst poslední trénink")
    
    st.markdown("---")
    
    with st.form("new_workout_form"):
        workout_date = st.date_input("Datum", value=date.today())
        note = st.text_area("Poznámka")
        
        st.subheader("Cviky")
        st.write("Přidejte cviky do tréninku:")
        
        # Use workout_builder if available, otherwise use manual input
        if workout_builder:
            exercises = []
            for i, selected_ex in enumerate(workout_builder):
                st.markdown(f"**{i+1}. {selected_ex['name']}** ({selected_ex['category']})")
                col1, col2, col3 = st.columns(3)
                with col1:
                    ex_sets = st.number_input(f"Série", value=3, min_value=1, key=f"sets_{i}")
                with col2:
                    ex_reps = st.number_input(f"Opakování", value=10, min_value=1, key=f"reps_{i}")
                with col3:
                    ex_weight = st.number_input(f"Váha (kg)", value=0.0, step=2.5, key=f"weight_{i}")
                
                exercises.append({
                    'name': selected_ex['name'],
                    'sets': ex_sets,
                    'reps': ex_reps,
                    'weight': ex_weight if ex_weight > 0 else None
                })
        else:
            # Manual exercise input
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
                st.error("❌ Přidejte alespoň jeden cvik")
            elif len(exercises) > 20:
                st.error("❌ Příliš mnoho cviků (max 20 na trénink)")
            else:
                invalid = [ex for ex in exercises if not ex['name'] or ex['sets'] < 1 or ex['reps'] < 1]
                if invalid:
                    st.error("❌ Všechny cviky musí mít jméno, série a opakování")
                else:
                    payload = {
                        'date': workout_date.isoformat(),
                        'note': note.strip()[:500],
                        'exercises': exercises
                    }
                    try:
                        r = session.post(f"{API_BASE}/workouts", json=payload, timeout=5)
                        if r.status_code == 201:
                            st.success("✅ Trénink vytvořen!")
                            # Clear workout builder after successful creation
                            if 'workout_builder' in st.session_state:
                                st.session_state['workout_builder'] = []
                            st.session_state['page'] = 'workouts'
                            st.rerun()
                        else:
                            _display_api_error(r, "vytváření tréninku")
                    except Exception as e:
                        st.error(f"❌ Chyba připojení: {str(e)}")
