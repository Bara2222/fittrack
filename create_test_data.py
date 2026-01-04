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
        
        # Create 5 workout sessions
        print("Creating 5 workout sessions...")
        
        # Workout 1: Push Day (3 days ago)
        workout1 = Workout(
            user_id=user.id,
            date=date.today() - timedelta(days=3),
            note="Push trénink - hrudník, ramena, triceps"
        )
        db.session.add(workout1)
        db.session.flush()  # Get workout ID
        
        # Exercises for workout 1
        exercises1 = [
            WorkoutExercise(workout_id=workout1.id, name="Bench press", sets=4, reps=8, weight=80.0),
            WorkoutExercise(workout_id=workout1.id, name="Incline dumbbell press", sets=3, reps=10, weight=30.0),
            WorkoutExercise(workout_id=workout1.id, name="Shoulder press", sets=3, reps=10, weight=25.0),
            WorkoutExercise(workout_id=workout1.id, name="Lateral raises", sets=3, reps=15, weight=12.0),
            WorkoutExercise(workout_id=workout1.id, name="Tricep dips", sets=3, reps=12, weight=None)
        ]
        for ex in exercises1:
            db.session.add(ex)
        
        # Workout 2: Pull Day (2 days ago)
        workout2 = Workout(
            user_id=user.id,
            date=date.today() - timedelta(days=2),
            note="Pull trénink - záda, biceps"
        )
        db.session.add(workout2)
        db.session.flush()
        
        exercises2 = [
            WorkoutExercise(workout_id=workout2.id, name="Pull-ups", sets=4, reps=6, weight=None),
            WorkoutExercise(workout_id=workout2.id, name="Barbell rows", sets=4, reps=8, weight=70.0),
            WorkoutExercise(workout_id=workout2.id, name="Lat pulldown", sets=3, reps=10, weight=60.0),
            WorkoutExercise(workout_id=workout2.id, name="Bicep curls", sets=3, reps=12, weight=20.0),
            WorkoutExercise(workout_id=workout2.id, name="Hammer curls", sets=3, reps=12, weight=18.0)
        ]
        for ex in exercises2:
            db.session.add(ex)
        
        # Workout 3: Legs Day (1 day ago)
        workout3 = Workout(
            user_id=user.id,
            date=date.today() - timedelta(days=1),
            note="Nohy a gluteus"
        )
        db.session.add(workout3)
        db.session.flush()
        
        exercises3 = [
            WorkoutExercise(workout_id=workout3.id, name="Squats", sets=4, reps=10, weight=90.0),
            WorkoutExercise(workout_id=workout3.id, name="Romanian deadlift", sets=3, reps=10, weight=80.0),
            WorkoutExercise(workout_id=workout3.id, name="Leg press", sets=3, reps=15, weight=120.0),
            WorkoutExercise(workout_id=workout3.id, name="Calf raises", sets=4, reps=20, weight=50.0),
            WorkoutExercise(workout_id=workout3.id, name="Lunges", sets=3, reps=12, weight=None)
        ]
        for ex in exercises3:
            db.session.add(ex)
        
        # Workout 4: Upper Body (1 week ago)
        workout4 = Workout(
            user_id=user.id,
            date=date.today() - timedelta(days=7),
            note="Celý horní korpus"
        )
        db.session.add(workout4)
        db.session.flush()
        
        exercises4 = [
            WorkoutExercise(workout_id=workout4.id, name="Deadlift", sets=4, reps=6, weight=100.0),
            WorkoutExercise(workout_id=workout4.id, name="Chest flyes", sets=3, reps=12, weight=22.0),
            WorkoutExercise(workout_id=workout4.id, name="Face pulls", sets=3, reps=15, weight=15.0),
            WorkoutExercise(workout_id=workout4.id, name="Close-grip bench press", sets=3, reps=10, weight=65.0)
        ]
        for ex in exercises4:
            db.session.add(ex)
        
        # Workout 5: Full Body (10 days ago)
        workout5 = Workout(
            user_id=user.id,
            date=date.today() - timedelta(days=10),
            note="Celotělový trénink"
        )
        db.session.add(workout5)
        db.session.flush()
        
        exercises5 = [
            WorkoutExercise(workout_id=workout5.id, name="Burpees", sets=3, reps=10, weight=None),
            WorkoutExercise(workout_id=workout5.id, name="Mountain climbers", sets=3, reps=20, weight=None),
            WorkoutExercise(workout_id=workout5.id, name="Push-ups", sets=3, reps=15, weight=None),
            WorkoutExercise(workout_id=workout5.id, name="Plank", sets=3, reps=60, weight=None),
            WorkoutExercise(workout_id=workout5.id, name="Jumping jacks", sets=3, reps=30, weight=None)
        ]
        for ex in exercises5:
            db.session.add(ex)
        
        # Commit all data
        db.session.commit()
        
        print("✅ Successfully created:")
        print(f"   - User: Emil (password: Emil159&)")
        print(f"   - 5 workout sessions with exercises")
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