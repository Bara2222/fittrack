"""
Test data creation script for FitTrack
Creates test user Emil with workouts and goals
"""
import sys
import os
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app, db
from backend.database_models import User, Workout, WorkoutExercise

def create_test_user():
    """Create test user Emil with sample data"""
    app = create_app()
    
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username='Emil').first()
        if existing_user:
            print("User Emil already exists. Deleting old data...")
            db.session.delete(existing_user)
            db.session.commit()
        
        # Create user Emil
        print("Creating user Emil...")
        user = User(
            username='Emil',
            password=generate_password_hash('Emil159&'),
            email='emil@test.com',
            age=28,
            height_cm=178,
            weight_kg=75.5
        )
        db.session.add(user)
        db.session.commit()
        
        print(f"User Emil created with ID: {user.id}")
        
        # Create 8 workout sessions over the last month (20+ exercises)
        print("Creating 8 workout sessions with 20+ exercises...")
        
        workouts_data = [
            # Workout 1: Push Day (3 days ago)
            {
                'date': date.today() - timedelta(days=3),
                'note': "Push trénink - hrudník, ramena, triceps",
                'exercises': [
                    {'name': "Bench press", 'sets': 4, 'reps': 8, 'weight': 80.0},
                    {'name': "Incline dumbbell press", 'sets': 3, 'reps': 10, 'weight': 30.0},
                    {'name': "Shoulder press", 'sets': 3, 'reps': 10, 'weight': 25.0},
                    {'name': "Lateral raises", 'sets': 3, 'reps': 15, 'weight': 12.0},
                    {'name': "Tricep dips", 'sets': 3, 'reps': 12, 'weight': None}
                ]
            },
            # Workout 2: Pull Day (5 days ago)
            {
                'date': date.today() - timedelta(days=5),
                'note': "Pull trénink - záda, biceps",
                'exercises': [
                    {'name': "Přítahy na hrazdě", 'sets': 4, 'reps': 6, 'weight': None},
                    {'name': "Barbell rows", 'sets': 4, 'reps': 8, 'weight': 70.0},
                    {'name': "Lat pulldown", 'sets': 3, 'reps': 10, 'weight': 60.0},
                    {'name': "Biceps zdvih", 'sets': 3, 'reps': 12, 'weight': 20.0},
                    {'name': "Hammer curls", 'sets': 3, 'reps': 12, 'weight': 18.0}
                ]
            },
            # Workout 3: Legs Day (8 days ago)
            {
                'date': date.today() - timedelta(days=8),
                'note': "Nohy a gluteus",
                'exercises': [
                    {'name': "Dřep", 'sets': 4, 'reps': 10, 'weight': 90.0},
                    {'name': "Romanian deadlift", 'sets': 3, 'reps': 10, 'weight': 80.0},
                    {'name': "Leg press", 'sets': 3, 'reps': 15, 'weight': 120.0},
                    {'name': "Calf raises", 'sets': 4, 'reps': 20, 'weight': 50.0}
                ]
            },
            # Workout 4: Upper Body (12 days ago)
            {
                'date': date.today() - timedelta(days=12),
                'note': "Celý horní korpus",
                'exercises': [
                    {'name': "Mrtvý tah", 'sets': 4, 'reps': 6, 'weight': 100.0},
                    {'name': "Chest flyes", 'sets': 3, 'reps': 12, 'weight': 22.0},
                    {'name': "Face pulls", 'sets': 3, 'reps': 15, 'weight': 15.0},
                    {'name': "Triceps kliky", 'sets': 3, 'reps': 10, 'weight': 65.0}
                ]
            },
            # Workout 5: HIIT Cardio (15 days ago)
            {
                'date': date.today() - timedelta(days=15),
                'note': "HIIT cardio a funkční trénink",
                'exercises': [
                    {'name': "Burpees", 'sets': 4, 'reps': 12, 'weight': None},
                    {'name': "Mountain climbers", 'sets': 4, 'reps': 25, 'weight': None},
                    {'name': "Kettlebell swing", 'sets': 3, 'reps': 15, 'weight': 16.0}
                ]
            },
            # Workout 6: Push Day (18 days ago)
            {
                'date': date.today() - timedelta(days=18),
                'note': "Push trénink - silový",
                'exercises': [
                    {'name': "Bench press", 'sets': 5, 'reps': 5, 'weight': 85.0},
                    {'name': "Tlaky na ramena", 'sets': 4, 'reps': 8, 'weight': 27.0},
                    {'name': "Cable flyes", 'sets': 3, 'reps': 12, 'weight': 25.0},
                    {'name': "Triceps overhead extension", 'sets': 3, 'reps': 12, 'weight': 20.0}
                ]
            },
            # Workout 7: Pull Day (22 days ago)
            {
                'date': date.today() - timedelta(days=22),
                'note': "Pull trénink - objemový",
                'exercises': [
                    {'name': "Veslování", 'sets': 4, 'reps': 10, 'weight': 65.0},
                    {'name': "T-bar rows", 'sets': 3, 'reps': 10, 'weight': 55.0},
                    {'name': "Biceps preacher curl", 'sets': 3, 'reps': 12, 'weight': 18.0},
                    {'name': "Shrugs", 'sets': 4, 'reps': 15, 'weight': 35.0}
                ]
            },
            # Workout 8: Legs Day (26 days ago)
            {
                'date': date.today() - timedelta(days=26),
                'note': "Nohy - silový den",
                'exercises': [
                    {'name': "Dřep", 'sets': 5, 'reps': 5, 'weight': 95.0},
                    {'name': "Výpady", 'sets': 3, 'reps': 12, 'weight': 20.0},
                    {'name': "Leg curl", 'sets': 3, 'reps': 12, 'weight': 40.0},
                    {'name': "Leg extension", 'sets': 3, 'reps': 15, 'weight': 50.0}
                ]
            }
        ]
        
        total_exercises = 0
        for i, workout_data in enumerate(workouts_data, 1):
            workout = Workout(
                user_id=user.id,
                date=workout_data['date'],
                note=workout_data['note']
            )
            db.session.add(workout)
            db.session.flush()
            
            for ex_data in workout_data['exercises']:
                exercise = WorkoutExercise(
                    workout_id=workout.id,
                    name=ex_data['name'],
                    sets=ex_data['sets'],
                    reps=ex_data['reps'],
                    weight=ex_data['weight']
                )
                db.session.add(exercise)
                total_exercises += 1
            
            print(f"   ✓ Workout {i}/{len(workouts_data)}: {workout_data['note']} ({len(workout_data['exercises'])} cviků)")
        
        # Commit all data
        db.session.commit()
        
        print("\n✅ Successfully created:")
        print(f"   - User: Emil (password: Emil159&)")
        print(f"   - {len(workouts_data)} workout sessions")
        print(f"   - {total_exercises} total exercises")
        print(f"   - User ID: {user.id}")
        
        print("\n🎯 Note about goals:")
        print("   Goals are stored in session_state in the frontend.")
        print("   You'll need to create them manually through the web interface.")
        print("   Suggested goals for Emil:")
        print("   1. Bench press 100kg (current: 80kg)")
        print("   2. Lose 3kg weight (current: 75.5kg, target: 72.5kg)")
        print("   3. Do 10 pull-ups (current: 6)")
        print("   4. Train 4x per week (current: varies)")
        
        return user

if __name__ == "__main__":
    try:
        user = create_test_user()
        print("\n✅ Test data creation completed successfully!")
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()