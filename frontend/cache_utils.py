"""
Cache utilities for API calls
Provides cached versions of frequently accessed data
"""
import streamlit as st
from config import API_BASE
from auth import _safe_json


@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes
def get_exercise_catalog():
    """Get cached exercise catalog"""
    from config import EXERCISE_CATALOG
    return EXERCISE_CATALOG


@st.cache_data(ttl=60, show_spinner=False)  # Cache for 1 minute
def get_user_stats(user_id):
    """Get cached user statistics"""
    try:
        session = st.session_state['session']
        r = session.get(f"{API_BASE}/stats", timeout=5)
        if r.ok:
            return _safe_json(r).get('stats', {})
    except Exception:
        pass
    return {}


@st.cache_data(ttl=120, show_spinner=False)  # Cache for 2 minutes, hide spinner
def get_user_workouts(user_id):
    """Get cached user workouts"""
    try:
        session = st.session_state['session']
        r = session.get(f"{API_BASE}/workouts", timeout=5)
        if r.ok:
            return _safe_json(r).get('workouts', [])
    except Exception:
        pass
    return []


@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes
def get_workout_templates():
    """Get cached workout templates"""
    # Predefined workout templates
    return [
        {
            'id': 'ppl_push',
            'name': '💪 Push (Hrudník/Ramena/Triceps)',
            'exercises': [
                {'name': 'Bench press', 'sets': 4, 'reps': '8-10'},
                {'name': 'Incline dumbbell press', 'sets': 3, 'reps': '10-12'},
                {'name': 'Shoulder press', 'sets': 3, 'reps': '8-10'},
                {'name': 'Lateral raises', 'sets': 3, 'reps': '12-15'},
                {'name': 'Triceps pushdowns', 'sets': 3, 'reps': '12-15'},
            ]
        },
        {
            'id': 'ppl_pull',
            'name': '💪 Pull (Záda/Biceps)',
            'exercises': [
                {'name': 'Deadlift', 'sets': 4, 'reps': '5-8'},
                {'name': 'Pull-ups', 'sets': 3, 'reps': '8-12'},
                {'name': 'Barbell rows', 'sets': 3, 'reps': '8-10'},
                {'name': 'Face pulls', 'sets': 3, 'reps': '15-20'},
                {'name': 'Barbell curls', 'sets': 3, 'reps': '10-12'},
            ]
        },
        {
            'id': 'ppl_legs',
            'name': '🦵 Legs (Nohy/Core)',
            'exercises': [
                {'name': 'Squat', 'sets': 4, 'reps': '8-10'},
                {'name': 'Romanian deadlift', 'sets': 3, 'reps': '10-12'},
                {'name': 'Leg press', 'sets': 3, 'reps': '12-15'},
                {'name': 'Leg curls', 'sets': 3, 'reps': '12-15'},
                {'name': 'Calf raises', 'sets': 4, 'reps': '15-20'},
            ]
        },
        {
            'id': 'full_body',
            'name': '🔥 Full Body',
            'exercises': [
                {'name': 'Squat', 'sets': 3, 'reps': '8-10'},
                {'name': 'Bench press', 'sets': 3, 'reps': '8-10'},
                {'name': 'Barbell rows', 'sets': 3, 'reps': '8-10'},
                {'name': 'Shoulder press', 'sets': 3, 'reps': '8-10'},
                {'name': 'Pull-ups', 'sets': 3, 'reps': 'max'},
            ]
        },
        {
            'id': 'upper_body',
            'name': '💪 Upper Body',
            'exercises': [
                {'name': 'Bench press', 'sets': 4, 'reps': '8-10'},
                {'name': 'Pull-ups', 'sets': 3, 'reps': '8-12'},
                {'name': 'Shoulder press', 'sets': 3, 'reps': '8-10'},
                {'name': 'Barbell rows', 'sets': 3, 'reps': '8-10'},
                {'name': 'Dips', 'sets': 3, 'reps': '8-12'},
            ]
        },
        {
            'id': 'lower_body',
            'name': '🦵 Lower Body',
            'exercises': [
                {'name': 'Squat', 'sets': 4, 'reps': '6-8'},
                {'name': 'Romanian deadlift', 'sets': 3, 'reps': '8-10'},
                {'name': 'Leg press', 'sets': 3, 'reps': '10-12'},
                {'name': 'Leg extensions', 'sets': 3, 'reps': '12-15'},
                {'name': 'Leg curls', 'sets': 3, 'reps': '12-15'},
            ]
        }
    ]


@st.cache_data(ttl=180, show_spinner=False)  # Cache for 3 minutes
def get_recent_achievements(user_id):
    """Get cached user achievements"""
    try:
        session = st.session_state['session']
        r = session.get(f"{API_BASE}/achievements", timeout=5)
        if r.ok:
            return _safe_json(r).get('achievements', [])
    except Exception:
        pass
    return []


def clear_user_cache(user_id):
    """Clear all cached data for a specific user"""
    get_user_stats.clear()
    get_user_workouts.clear()
    get_recent_achievements.clear()


def clear_all_cache():
    """Clear all cached data"""
    st.cache_data.clear()
