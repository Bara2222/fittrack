"""
Utility functions for FitTrack Streamlit application.
Contains achievements, calculators, theme handling, and other helper functions.
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
from config import API_BASE, AVAILABLE_PLATES, DEFAULT_BARBELL_WEIGHT


def calculate_1rm(weight, reps):
    """Calculate 1RM using Epley formula"""
    if reps <= 1:
        return weight
    return weight * (1 + reps / 30.0)


def calculate_plate_distribution(target_weight, barbell_weight=DEFAULT_BARBELL_WEIGHT):
    """Calculate optimal plate distribution for target weight"""
    weight_to_load = target_weight - barbell_weight
    if weight_to_load <= 0:
        return []
    
    # Available plates (kg) - each side
    result = []
    
    # Calculate for one side (divide by 2)
    side_weight = weight_to_load / 2
    
    for plate in AVAILABLE_PLATES:
        count = int(side_weight // plate)
        if count > 0:
            result.extend([plate] * count)
            side_weight -= plate * count
    
    return result


def render_plate_visual(plates):
    """Render visual representation of plates on barbell"""
    if not plates:
        return '<div class="plate-visual"><div class="barbell"></div></div>'
    
    plate_html = '<div class="plate-visual">'
    
    # Left side plates
    for plate in reversed(plates):
        plate_class = f"plate-{str(plate).replace('.', '_')}"
        plate_html += f'<div class="plate {plate_class}">{plate}</div>'
    
    # Barbell
    plate_html += '<div class="barbell"></div>'
    
    # Right side plates (mirror)
    for plate in plates:
        plate_class = f"plate-{str(plate).replace('.', '_')}"
        plate_html += f'<div class="plate {plate_class}">{plate}</div>'
    
    plate_html += '</div>'
    return plate_html


def calculate_workout_streak():
    """Calculate current workout streak"""
    try:
        session = st.session_state['session']
        r = session.get(f"{API_BASE}/workouts", timeout=5)
        if not r.ok:
            return 0
        
        from auth import _safe_json
        workouts = _safe_json(r).get('workouts', [])
        if not workouts:
            return 0
        
        # Sort by date descending
        workout_dates = sorted([pd.to_datetime(w['date']).date() for w in workouts], reverse=True)
        
        streak = 0
        current_date = pd.Timestamp.now().date()
        
        for workout_date in workout_dates:
            # Allow for 1 day gap (rest day)
            if (current_date - workout_date).days <= 2:
                streak += 1
                current_date = workout_date - timedelta(days=1)
            else:
                break
        
        return streak
    except Exception:
        return 0


def check_achievements(user_stats):
    """Check and return new achievements"""
    achievements = []
    
    total_workouts = user_stats.get('total_workouts', 0)
    total_volume = user_stats.get('total_volume', 0)
    streak = calculate_workout_streak()
    
    # Workout milestones
    if total_workouts >= 1 and 'first_workout' not in st.session_state.get('earned_achievements', []):
        achievements.append({'id': 'first_workout', 'name': '🏋️ První trénink', 'desc': 'Započal jsi svou fitness cestu!'})
    
    if total_workouts >= 10 and 'ten_workouts' not in st.session_state.get('earned_achievements', []):
        achievements.append({'id': 'ten_workouts', 'name': '💪 Desítka', 'desc': '10 tréninků dokončeno!'})
    
    if total_workouts >= 50 and 'fifty_workouts' not in st.session_state.get('earned_achievements', []):
        achievements.append({'id': 'fifty_workouts', 'name': '🎯 Padesátka', 'desc': '50 tréninků - jsi na správné cestě!'})
    
    # Volume milestones
    if total_volume >= 1000 and 'volume_1k' not in st.session_state.get('earned_achievements', []):
        achievements.append({'id': 'volume_1k', 'name': '🚀 1000kg Club', 'desc': 'Celkový objem přes 1000kg!'})
    
    # Streak achievements
    if streak >= 3 and 'streak_3' not in st.session_state.get('earned_achievements', []):
        achievements.append({'id': 'streak_3', 'name': '🔥 Trojka', 'desc': '3 dny v řadě!'})
    
    if streak >= 7 and 'streak_7' not in st.session_state.get('earned_achievements', []):
        achievements.append({'id': 'streak_7', 'name': '⚡ Týdenní válečník', 'desc': '7 dní streak!'})
    
    return achievements

def calculate_training_load(workouts_data):
    """Calculate training load based on RPE and volume"""
    total_load = 0
    
    for workout in workouts_data:
        workout_load = 0
        for exercise in workout.get('exercises', []):
            volume = exercise.get('sets', 0) * exercise.get('reps', 0)
            weight = exercise.get('weight', 0) or 1  # Default to bodyweight
            rpe = exercise.get('rpe', 6)  # Default moderate intensity
            
            exercise_load = volume * weight * (rpe / 10)
            workout_load += exercise_load
        
        total_load += workout_load
    
    return total_load

def create_volume_trend_chart(df):
    """Create interactive volume trend chart with projections"""
    if df.empty:
        return None
    
    # Calculate weekly volume
    df['week'] = df['date'].dt.isocalendar().week
    weekly_volume = df.groupby('week')['volume'].sum().reset_index()
    
    # Simple linear projection for next 4 weeks
    if len(weekly_volume) >= 3:
        from sklearn.linear_model import LinearRegression
        import numpy as np
        
        X = np.array(weekly_volume['week']).reshape(-1, 1)
        y = weekly_volume['volume']
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict next 4 weeks
        next_weeks = np.array(range(weekly_volume['week'].max() + 1, 
                                   weekly_volume['week'].max() + 5)).reshape(-1, 1)
        predictions = model.predict(next_weeks)
        
        # Add predictions to chart
        pred_df = pd.DataFrame({
            'week': next_weeks.flatten(),
            'volume': predictions,
            'type': 'Predikce'
        })
        
        chart_df = weekly_volume.copy()
        chart_df['type'] = 'Skutečnost'
        
        combined_df = pd.concat([
            chart_df[['week', 'volume', 'type']],
            pred_df
        ])
        
        fig = px.line(combined_df, x='week', y='volume', color='type',
                     title='Trend objemu tréninku s predikcí',
                     labels={'week': 'Týden', 'volume': 'Objem (kg)', 'type': 'Typ'})
        
        fig.update_traces(mode='lines+markers')
        return fig
    
    return None

def calculate_muscle_recovery_score(workout_history, muscle_group):
    """Calculate recovery score for specific muscle group"""
    if not workout_history:
        return 100  # Fully recovered if no recent training
    
    # Find last workout that trained this muscle group
    last_workout = None
    for workout in reversed(workout_history):
        for exercise in workout.get('exercises', []):
            if get_muscle_group(exercise['name']) == muscle_group:
                last_workout = workout
                break
        if last_workout:
            break
    
    if not last_workout:
        return 100  # Fully recovered
    
    # Calculate days since last training
    last_date = pd.to_datetime(last_workout['date'])
    days_elapsed = (pd.Timestamp.now() - last_date).days
    
    # Recovery score based on muscle group recovery time
    recovery_times = {
        'hrudník': 2,
        'záda': 3,
        'ramena': 1,
        'biceps': 1,
        'triceps': 1,
        'nohy': 3,
        'core': 1
    }
    
    recovery_time = recovery_times.get(muscle_group, 2)
    recovery_score = min(100, (days_elapsed / recovery_time) * 100)
    
    return recovery_score

def get_muscle_group(exercise_name):
    """Categorize exercise by primary muscle group"""
    name_lower = exercise_name.lower()
    
    muscle_map = {
        'hrudník': ['bench', 'tlak', 'press', 'fly', 'chest'],
        'záda': ['pull', 'tah', 'row', 'deadlift', 'mrtvý', 'lat'],
        'ramena': ['shoulder', 'rameno', 'lateral', 'overhead', 'deltoid'],
        'biceps': ['curl', 'bicep'],
        'triceps': ['tricep', 'extension', 'dip'],
        'nohy': ['squat', 'dřep', 'leg', 'lunge', 'calf'],
        'core': ['plank', 'abs', 'crunch', 'core']
    }
    
    for muscle, keywords in muscle_map.items():
        if any(keyword in name_lower for keyword in keywords):
            return muscle
    
    return 'ostatní'

def create_body_heatmap(muscle_data):
    """Create body heatmap visualization"""
    # Simple bar chart representation of muscle group training
    muscle_df = pd.DataFrame(list(muscle_data.items()), columns=['Muscle', 'Volume'])
    
    fig = px.bar(muscle_df, x='Muscle', y='Volume',
                title='Zatížení svalových skupin',
                color='Volume',
                color_continuous_scale='YlOrRd')
    
    fig.update_layout(
        plot_bgcolor='#1c1c1c',
        paper_bgcolor='#000000',
        font_color='#ffffff'
    )
    
    return fig

def export_workout_as_image(workout_data):
    """Export workout as shareable image"""
    # This would create a formatted image of the workout
    # For now, return formatted text
    
    output = f"""
    🏋️ FITTRACK WORKOUT
    
    📅 Datum: {workout_data.get('date', 'N/A')}
    📝 Poznámka: {workout_data.get('note', 'Bez poznámky')}
    
    💪 CVIKY:
    """
    
    for i, exercise in enumerate(workout_data.get('exercises', []), 1):
        output += f"""
    {i}. {exercise.get('name', 'N/A')}
       {exercise.get('sets', 0)}x {exercise.get('reps', 0)}"""
        
        if exercise.get('weight'):
            output += f" @ {exercise.get('weight')}kg"
        
        output += "\n"
    
    return output

def calculate_estimated_calories_burned(exercises, user_weight=75):
    """Estimate calories burned based on exercises and user weight"""
    # MET values for different exercise types
    met_values = {
        'cardio': 8.0,
        'strength': 6.0,
        'bodyweight': 4.0
    }
    
    total_calories = 0
    
    for exercise in exercises:
        # Categorize exercise
        name_lower = exercise['name'].lower()
        if any(x in name_lower for x in ['run', 'bike', 'cardio']):
            met = met_values['cardio']
        elif exercise.get('weight', 0) > 0:
            met = met_values['strength']
        else:
            met = met_values['bodyweight']
        
        # Estimate duration based on sets and reps
        estimated_minutes = exercise.get('sets', 0) * 3  # ~3 minutes per set
        
        # Calories = MET * weight(kg) * time(hours)
        calories = met * user_weight * (estimated_minutes / 60)
        total_calories += calories
    
    return round(total_calories)

def generate_workout_insights(workout_data):
    """Generate AI-like insights about workout"""
    insights = []
    
    total_exercises = len(workout_data.get('exercises', []))
    total_sets = sum(ex.get('sets', 0) for ex in workout_data.get('exercises', []))
    total_reps = sum(ex.get('sets', 0) * ex.get('reps', 0) for ex in workout_data.get('exercises', []))
    
    # Volume insights
    if total_sets > 20:
        insights.append("🔥 Vysokoobjemový trénink - skvělé pro růst svalů!")
    elif total_sets < 10:
        insights.append("⚡ Krátký a intenzivní trénink - ideální pro sílu!")
    
    # Exercise variety
    if total_exercises > 8:
        insights.append("🎯 Široká variabilita cviků - komplexní rozvoj!")
    elif total_exercises < 4:
        insights.append("🎯 Fokusovaný trénink - maximální koncentrace!")
    
    # Rep range analysis
    avg_reps = total_reps / max(total_sets, 1)
    if avg_reps > 12:
        insights.append("💪 Vytrvalostní rozsah - skvělé pro kondici!")
    elif avg_reps < 6:
        insights.append("⚡ Silový rozsah - budování maximální síly!")
    
    return insights

def create_activity_heatmap(workouts):
    """Create GitHub-style activity heatmap"""
    if not workouts:
        return ""
    
    # Get last 365 days
    end_date = pd.Timestamp.now().date()
    start_date = end_date - timedelta(days=365)
    
    # Create date range
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Count workouts per day
    workout_counts = {}
    for workout in workouts:
        workout_date = pd.to_datetime(workout['date']).date()
        if start_date <= workout_date <= end_date:
            workout_counts[workout_date] = workout_counts.get(workout_date, 0) + 1
    
    # Generate heatmap HTML
    heatmap_html = '<div class="heatmap-calendar">'
    
    for day in date_range:
        day_date = day.date()
        count = workout_counts.get(day_date, 0)
        
        # Determine level based on workout count
        if count == 0:
            level = ''
        elif count == 1:
            level = 'level-1'
        elif count == 2:
            level = 'level-2'
        elif count == 3:
            level = 'level-3'
        else:
            level = 'level-4'
        
        heatmap_html += f'<div class="heatmap-day {level}" title="{day_date}: {count} workout(s)"></div>'
    
    heatmap_html += '</div>'
    return heatmap_html

def get_all_achievements():
    """Return all available achievements"""
    return [
        {'id': 'first_workout', 'name': '🏋️ První trénink', 'desc': 'Započal jsi svou fitness cestu!'},
        {'id': 'ten_workouts', 'name': '💪 Desítka', 'desc': '10 tréninků dokončeno!'},
        {'id': 'fifty_workouts', 'name': '🎯 Padesátka', 'desc': '50 tréninků - jsi na správné cestě!'},
        {'id': 'hundred_workouts', 'name': '🚀 Stovka', 'desc': '100 tréninků - jsi fitness legenda!'},
        {'id': 'volume_1k', 'name': '🏋️ 1000kg Club', 'desc': 'Celkový objem přes 1000kg!'},
        {'id': 'volume_5k', 'name': '💎 5000kg Club', 'desc': 'Celkový objem přes 5000kg!'},
        {'id': 'streak_3', 'name': '🔥 Trojka', 'desc': '3 dny v řadě!'},
        {'id': 'streak_7', 'name': '⚡ Týdenní válečník', 'desc': '7 dní streak!'},
        {'id': 'streak_30', 'name': '🏆 Měsíční mistr', 'desc': '30 dní streak!'},
        {'id': 'heavy_lift', 'name': '🏋️‍♀️ Silák', 'desc': 'Zvedl jsi více než 100kg!'},
        {'id': 'consistent', 'name': '📅 Konzistentní', 'desc': '30 tréninků v 60 dnech!'},
        {'id': 'variety', 'name': '🎨 Všestranný', 'desc': 'Vyzkoušel jsi 20+ různých cviků!'},
    ]

def format_duration(minutes):
    """Format duration in minutes to human-readable format"""
    if minutes < 60:
        return f"{int(minutes)} min"
    
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    
    if mins == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {mins}min"

def calculate_bmi(weight_kg, height_cm):
    """Calculate BMI"""
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)

def get_bmi_category(bmi):
    """Get BMI category"""
    if bmi < 18.5:
        return "Podváha", "#3b82f6"
    elif bmi < 25:
        return "Normální váha", "#10b981"
    elif bmi < 30:
        return "Nadváha", "#f59e0b"
    else:
        return "Obezita", "#ef4444"

def calculate_calories_burned(exercises, user_weight=75, duration_minutes=60):
    """Calculate estimated calories burned during workout"""
    # Base metabolic rate during exercise (METs)
    # Strength training: ~6 METs
    # Cardio: ~8 METs
    
    base_met = 6.0  # Average for strength training
    
    # Calories = METs × weight in kg × time in hours
    calories = base_met * user_weight * (duration_minutes / 60)
    
    return round(calories)

def toggle_theme():
    """Toggle between light and dark theme"""
    current_theme = st.session_state.get('theme', 'dark')
    new_theme = 'light' if current_theme == 'dark' else 'dark'
    st.session_state['theme'] = new_theme
    return new_theme

def calculate_training_volume(exercises):
    """Calculate total training volume (sets × reps × weight)"""
    total_volume = 0
    
    for exercise in exercises:
        sets = exercise.get('sets', 0)
        reps = exercise.get('reps', 0)
        weight = exercise.get('weight', 0)
        
        if weight and weight > 0:
            total_volume += sets * reps * weight
    
    return total_volume