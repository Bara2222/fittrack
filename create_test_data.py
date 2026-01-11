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
    """Create test user Emilek with sample data"""
    app = create_app()
    
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username='Emilek').first()
        if existing_user:
            print("User Emilek already exists. Deleting old data...")
            db.session.delete(existing_user)
            db.session.commit()
        
        # Create user Emilek
        print("Creating user Emilek...")
        user = User(
            username='Emilek',
            password=generate_password_hash('Emilek1@'),
            email='emilek@b.cz',
            age=25,
            height_cm=180,
            weight_kg=78.0
        )
        db.session.add(user)
        db.session.commit()
        
        print(f"User Emilek created with ID: {user.id}")
        
        # Create 8 workout sessions over the last month (20+ exercises)
        print("Creating 10 workout sessions with 30+ exercises...")
        
        workouts_data = [
            # Workout 1: Push Day - Recent (2 days ago)
            {
                'date': date.today() - timedelta(days=2),
                'note': "Push Day - Hrudník a triceps 💪",
                'exercises': [
                    {'name': "Bench press", 'sets': 4, 'reps': 10, 'weight': 75.0},
                    {'name': "Incline dumbbell press", 'sets': 4, 'reps': 10, 'weight': 28.0},
                    {'name': "Cable flyes", 'sets': 3, 'reps': 12, 'weight': 20.0},
                    {'name': "Tricep dips", 'sets': 3, 'reps': 12, 'weight': None},
                    {'name': "Triceps overhead extension", 'sets': 3, 'reps': 15, 'weight': 18.0}
                ]
            },
            # Workout 2: Pull Day (5 days ago)
            {
                'date': date.today() - timedelta(days=5),
                'note': "Pull Day - Záda a biceps 🔥",
                'exercises': [
                    {'name': "Mrtvý tah", 'sets': 4, 'reps': 8, 'weight': 90.0},
                    {'name': "Přítahy na hrazdě", 'sets': 4, 'reps': 7, 'weight': None},
                    {'name': "Barbell rows", 'sets': 4, 'reps': 10, 'weight': 65.0},
                    {'name': "Lat pulldown", 'sets': 3, 'reps': 12, 'weight': 55.0},
                    {'name': "Biceps zdvih", 'sets': 3, 'reps': 12, 'weight': 22.0},
                    {'name': "Hammer curls", 'sets': 3, 'reps': 12, 'weight': 18.0}
                ]
            },
            # Workout 3: Legs Day (7 days ago)
            {
                'date': date.today() - timedelta(days=7),
                'note': "Leg Day - Nohy a gluteus 🦵",
                'exercises': [
                    {'name': "Dřep", 'sets': 5, 'reps': 8, 'weight': 85.0},
                    {'name': "Romanian deadlift", 'sets': 4, 'reps': 10, 'weight': 75.0},
                    {'name': "Leg press", 'sets': 4, 'reps': 12, 'weight': 140.0},
                    {'name': "Leg curl", 'sets': 3, 'reps': 15, 'weight': 45.0},
                    {'name': "Calf raises", 'sets': 4, 'reps': 20, 'weight': 55.0}
                ]
            },
            # Workout 4: Push Day (10 days ago)
            {
                'date': date.today() - timedelta(days=10),
                'note': "Push Day - Ramena a triceps",
                'exercises': [
                    {'name': "Shoulder press", 'sets': 4, 'reps': 10, 'weight': 26.0},
                    {'name': "Lateral raises", 'sets': 4, 'reps': 12, 'weight': 12.0},
                    {'name': "Front raises", 'sets': 3, 'reps': 12, 'weight': 10.0},
                    {'name': "Triceps kliky", 'sets': 4, 'reps': 10, 'weight': 60.0}
                ]
            },
            # Workout 5: Pull Day (13 days ago)
            {
                'date': date.today() - timedelta(days=13),
                'note': "Pull Day - Celá záda",
                'exercises': [
                    {'name': "Veslování", 'sets': 4, 'reps': 10, 'weight': 60.0},
                    {'name': "T-bar rows", 'sets': 3, 'reps': 10, 'weight': 50.0},
                    {'name': "Face pulls", 'sets': 3, 'reps': 15, 'weight': 15.0},
                    {'name': "Shrugs", 'sets': 4, 'reps': 15, 'weight': 32.0}
                ]
            },
            # Workout 6: Legs Day (16 days ago)
            {
                'date': date.today() - timedelta(days=16),
                'note': "Leg Day - Silový trénink",
                'exercises': [
                    {'name': "Dřep", 'sets': 5, 'reps': 5, 'weight': 95.0},
                    {'name': "Výpady", 'sets': 4, 'reps': 10, 'weight': 22.0},
                    {'name': "Leg extension", 'sets': 3, 'reps': 15, 'weight': 50.0},
                    {'name': "Bulgarian split squat", 'sets': 3, 'reps': 12, 'weight': 18.0}
                ]
            },
            # Workout 7: HIIT Cardio (19 days ago)
            {
                'date': date.today() - timedelta(days=19),
                'note': "HIIT & Funkční trénink 🏃",
                'exercises': [
                    {'name': "Burpees", 'sets': 5, 'reps': 12, 'weight': None},
                    {'name': "Mountain climbers", 'sets': 4, 'reps': 25, 'weight': None},
                    {'name': "Kettlebell swing", 'sets': 4, 'reps': 15, 'weight': 20.0},
                    {'name': "Box jumps", 'sets': 3, 'reps': 12, 'weight': None}
                ]
            },
            # Workout 8: Upper Body (22 days ago)
            {
                'date': date.today() - timedelta(days=22),
                'note': "Upper Body - Mix",
                'exercises': [
                    {'name': "Bench press", 'sets': 4, 'reps': 8, 'weight': 70.0},
                    {'name': "Barbell rows", 'sets': 4, 'reps': 8, 'weight': 60.0},
                    {'name': "Shoulder press", 'sets': 3, 'reps': 10, 'weight': 24.0},
                    {'name': "Biceps zdvih", 'sets': 3, 'reps': 12, 'weight': 20.0}
                ]
            },
            # Workout 9: Push Day (25 days ago)
            {
                'date': date.today() - timedelta(days=25),
                'note': "Push Day - Objemový",
                'exercises': [
                    {'name': "Bench press", 'sets': 4, 'reps': 12, 'weight': 65.0},
                    {'name': "Incline bench press", 'sets': 4, 'reps': 10, 'weight': 60.0},
                    {'name': "Chest flyes", 'sets': 3, 'reps': 15, 'weight': 20.0},
                    {'name': "Tricep dips", 'sets': 4, 'reps': 10, 'weight': None}
                ]
            },
            # Workout 10: Pull Day (28 days ago)
            {
                'date': date.today() - timedelta(days=28),
                'note': "Pull Day - První trénink měsíce 💪",
                'exercises': [
                    {'name': "Mrtvý tah", 'sets': 5, 'reps': 6, 'weight': 85.0},
                    {'name': "Přítahy na hrazdě", 'sets': 4, 'reps': 5, 'weight': None},
                    {'name': "Veslování", 'sets': 4, 'reps': 10, 'weight': 55.0},
                    {'name': "Biceps preacher curl", 'sets': 3, 'reps': 12, 'weight': 16.0}
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
        print(f"   - User: Emilek (email: emilek@b.cz, password: Emilek1@)")
        print(f"   - {len(workouts_data)} workout sessions")
        print(f"   - {total_exercises} total exercises")
        print(f"   - User ID: {user.id}")
        
        print("\n🎯 Doporučené cíle pro Emilka (vytvoř manuálně ve frontendu):")
        print("   1. 💪 Bench press 100kg (současná: 75kg, cíl: 100kg) - zbývá: 25kg")
        print("   2. 💪 Dřep 120kg (současná: 85kg, cíl: 120kg) - zbývá: 35kg")
        print("   3. 💪 Mrtvý tah 140kg (současná: 90kg, cíl: 140kg) - zbývá: 50kg")
        print("   4. 🎯 10 přítahů na hrazdě (současná: 7, cíl: 10) - zbývá: 3")
        print("   5. ⚖️ Nabrat svalovou hmotu na 82kg (současná: 78kg, cíl: 82kg) - zbývá: 4kg")
        print("\n   DŮLEŽITÉ: U všech cílů je 'zbývá' KLADNÉ číslo!")
        print("   Vzorec: zbývá = cíl - současná (musí být > 0)")
        
        return user

if __name__ == "__main__":
    try:
        user = create_test_user()
        print("\n✅ Test data creation completed successfully!")
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()