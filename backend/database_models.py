# backend/database_models.py
"""
Database Models
SQLAlchemy ORM models for FitTrack application
"""
from datetime import datetime
from flask_login import UserMixin
from backend import db

class User(UserMixin, db.Model):
    """User model for authentication and profile"""
    __tablename__ = 'user'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)  # Hashed password
    
    # Profile fields
    email = db.Column(db.String(255), unique=True, nullable=True, index=True)
    age = db.Column(db.Integer, nullable=True)
    height_cm = db.Column(db.Float, nullable=True)
    weight_kg = db.Column(db.Float, nullable=True)
    
    # OAuth fields
    oauth_provider = db.Column(db.String(50), nullable=True)  # 'google', etc.
    oauth_sub = db.Column(db.String(255), nullable=True, unique=True, index=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    
    # Relationships
    workouts = db.relationship('Workout', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def profile_completed(self):
        """Check if user has completed their profile"""
        return all([
            self.age is not None,
            self.height_cm is not None,
            self.weight_kg is not None
        ])
    
    def to_dict(self, include_sensitive=False):
        """Serialize user to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email or '',
            'age': self.age,
            'height_cm': self.height_cm,
            'weight_kg': self.weight_kg,
            'oauth_provider': self.oauth_provider or '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'profile_completed': self.profile_completed
        }
        if include_sensitive:
            data['is_admin'] = (self.username == 'admin')
        return data


class Workout(db.Model):
    """Workout session model"""
    __tablename__ = 'workout'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    note = db.Column(db.Text, nullable=True)
    
    # Relationships
    user = db.relationship('User', back_populates='workouts')
    exercises = db.relationship('WorkoutExercise', back_populates='workout', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Workout {self.id} on {self.date}>'
    
    def to_dict(self, include_exercises=False):
        """Serialize workout to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'note': self.note or '',
            'exercise_count': self.exercises.count()
        }
        if include_exercises:
            data['exercises'] = [ex.to_dict() for ex in self.exercises.all()]
        return data


class WorkoutExercise(db.Model):
    """Exercise within a workout"""
    __tablename__ = 'workout_exercise'
    
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    sets = db.Column(db.Integer, nullable=False, default=3)
    reps = db.Column(db.Integer, nullable=False, default=10)
    weight = db.Column(db.Float, nullable=True)
    
    # Relationships
    workout = db.relationship('Workout', back_populates='exercises')
    
    def __repr__(self):
        return f'<Exercise {self.name} - {self.sets}x{self.reps}>'
    
    def to_dict(self):
        """Serialize exercise to dictionary"""
        return {
            'id': self.id,
            'workout_id': self.workout_id,
            'name': self.name,
            'sets': self.sets,
            'reps': self.reps,
            'weight': self.weight
        }
