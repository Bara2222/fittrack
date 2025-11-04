import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime
import webbrowser

# Use secrets if available, otherwise default to localhost
try:
    API_BASE = st.secrets.get('api_base', 'http://localhost:5000/api')
except:
    API_BASE = 'http://localhost:5000/api'

# Initialize session
if 'session' not in st.session_state:
    st.session_state['session'] = requests.Session()

session = st.session_state['session']

# Initialize login state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'

# Check for Google OAuth callback
query_params = st.query_params
if 'auth' in query_params:
    if query_params['auth'] == 'success':
        st.session_state['logged_in'] = True
        st.success('Přihlášení přes Google úspěšné!')
        # Clear query params
        st.query_params.clear()
    elif query_params['auth'] == 'error':
        st.error(f"Chyba při přihlášení: {query_params.get('msg', 'Unknown error')}")
        st.query_params.clear()

# Page config
st.set_page_config(
    page_title="FitTrack",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
        margin: 0.5rem;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .stat-label {
        font-size: 1rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

def check_login():
    """Check if user is logged in by calling /api/me"""
    try:
        r = session.get(f"{API_BASE}/me")
        if r.ok:
            st.session_state['logged_in'] = True
            st.session_state['user'] = r.json().get('user')
            return True
    except:
        pass
    st.session_state['logged_in'] = False
    st.session_state['user'] = None
    return False

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
                    r = session.post(f"{API_BASE}/login", json={'username': username, 'password': password})
                    if r.ok:
                        data = r.json()
                        st.session_state['logged_in'] = True
                        st.session_state['user'] = {'username': username, 'is_admin': data.get('is_admin', False)}
                        st.success("Přihlášení úspěšné!")
                        st.rerun()
                    else:
                        st.error(r.json().get('error', 'Chyba při přihlášení'))
        
        st.markdown("---")
        st.subheader("Nebo se přihlaste přes Google")
        if st.button("🔐 Přihlásit se přes Google", use_container_width=True):
            r = session.get(f"{API_BASE}/google/login")
            if r.ok:
                auth_url = r.json().get('auth_url')
                st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', unsafe_allow_html=True)
                st.info(f"Přesměrování na Google... Pokud se nic nestane, [klikněte sem]({auth_url})")
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
                elif len(new_password) < 8:
                    st.error("Heslo musí mít minimálně 8 znaků")
                else:
                    r = session.post(f"{API_BASE}/register", json={'username': new_username, 'password': new_password})
                    if r.ok:
                        st.success("Registrace úspěšná! Nyní se můžete přihlásit.")
                    else:
                        st.error(r.json().get('error', 'Chyba při registraci'))

def dashboard_page():
    st.markdown('<div class="main-header">📊 Dashboard</div>', unsafe_allow_html=True)
    
    # Stats
    r = session.get(f"{API_BASE}/stats")
    if r.ok:
        stats = r.json().get('stats', {})
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
            r = session.post(f"{API_BASE}/quickstart/zacatecnik")
            if r.ok:
                st.success("Trénink vytvořen!")
                st.session_state['page'] = 'workouts'
                st.rerun()
    
    with col2:
        if st.button("🟡 Pokročilý", use_container_width=True):
            r = session.post(f"{API_BASE}/quickstart/pokracily")
            if r.ok:
                st.success("Trénink vytvořen!")
                st.session_state['page'] = 'workouts'
                st.rerun()
    
    with col3:
        if st.button("🔴 Expert", use_container_width=True):
            r = session.post(f"{API_BASE}/quickstart/expert")
            if r.ok:
                st.success("Trénink vytvořen!")
                st.session_state['page'] = 'workouts'
                st.rerun()
    
    st.markdown("---")
    
    # Recent workouts
    st.subheader("📅 Poslední tréninky")
    r = session.get(f"{API_BASE}/workouts")
    if r.ok:
        workouts = r.json().get('workouts', [])[:5]
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

def workouts_page():
    st.markdown('<div class="main-header">💪 Moje tréninky</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Nový trénink", use_container_width=True):
            st.session_state['page'] = 'new_workout'
            st.rerun()
    
    st.markdown("---")
    
    r = session.get(f"{API_BASE}/workouts")
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
    r = session.get(f"{API_BASE}/workouts/{wid}")
    
    if not r.ok:
        st.error("Trénink nenalezen")
        return
    
    workout = r.json().get('workout')
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f'<div class="main-header">🏋️ Trénink z {workout["date"]}</div>', unsafe_allow_html=True)
    with col2:
        if st.button("🗑️ Smazat trénink", use_container_width=True):
            r = session.delete(f"{API_BASE}/workouts/{wid}")
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
                    r = session.delete(f"{API_BASE}/exercises/{ex['id']}")
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
                r = session.post(f"{API_BASE}/exercises/{wid}/add", json=payload)
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
                r = session.post(f"{API_BASE}/workouts", json=payload)
                if r.status_code == 201:
                    st.success("Trénink vytvořen!")
                    st.session_state['page'] = 'workouts'
                    st.rerun()
                else:
                    st.error("Chyba při vytváření tréninku")

def catalog_page():
    st.markdown('<div class="main-header">📚 Katalog cviků</div>', unsafe_allow_html=True)
    
    r = session.get(f"{API_BASE}/catalog")
    if not r.ok:
        st.error("Nepodařilo se načíst katalog")
        return
    
    catalog = r.json().get('exercises', [])
    
    st.write("Základní cviky pro inspiraci:")
    
    cols = st.columns(3)
    for idx, exercise in enumerate(catalog):
        with cols[idx % 3]:
            st.markdown(f"✅ **{exercise}**")

def export_page():
    st.markdown('<div class="main-header">📥 Export dat</div>', unsafe_allow_html=True)
    
    st.write("Exportujte všechna vaše data do CSV formátu.")
    
    if st.button("📊 Stáhnout CSV", use_container_width=True):
        r = session.get(f"{API_BASE}/export/csv")
        if r.ok:
            csv_data = r.json().get('csv')
            st.download_button(
                label="💾 Uložit CSV soubor",
                data=csv_data,
                file_name=f"fittrack_{date.today().isoformat()}.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.success("CSV připraveno ke stažení!")
        else:
            st.error("Chyba při exportu")

def admin_page():
    if not st.session_state.get('user', {}).get('is_admin'):
        st.error("Nemáte oprávnění")
        return
    
    st.markdown('<div class="main-header">⚙️ Admin panel</div>', unsafe_allow_html=True)
    
    r = session.get(f"{API_BASE}/admin/users")
    if not r.ok:
        st.error("Chyba při načítání uživatelů")
        return
    
    users = r.json().get('users', [])
    
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
        login_page()
        st.stop()

# Sidebar navigation
with st.sidebar:
    st.title("💪 FitTrack")
    user_info = st.session_state.get('user', {})
    st.write(f"👤 **{user_info.get('username', 'User')}**")
    
    st.markdown("---")
    
    pages = {
        'dashboard': '📊 Dashboard',
        'workouts': '💪 Moje tréninky',
        'new_workout': '➕ Nový trénink',
        'catalog': '📚 Katalog cviků',
        'export': '📥 Export',
    }
    
    if user_info.get('is_admin'):
        pages['admin'] = '⚙️ Admin'
    
    for key, label in pages.items():
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state['page'] = key
            st.rerun()
    
    st.markdown("---")
    
    if st.button("🚪 Odhlásit se", use_container_width=True):
        r = session.post(f"{API_BASE}/logout")
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.session_state['page'] = 'dashboard'
        session.cookies.clear()
        st.rerun()

# Render current page
page = st.session_state.get('page', 'dashboard')

if page == 'dashboard':
    dashboard_page()
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
