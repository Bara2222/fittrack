# backend/api_routes.py
"""
API Routes for FitTrack Backend
RESTful API endpoints with input validation and error handling
"""
import os
import io
import csv
import datetime
from flask import Blueprint, jsonify, request, url_for, redirect
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from backend.app import db, logger
from backend.database_models import User, Workout, WorkoutExercise

# Create blueprint
api_bp = Blueprint('api', __name__)


# ============================================================================
# AUTHENTICATION & USER MANAGEMENT
# ============================================================================

@api_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json() or {}
        
        # Validation
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'ok': False, 'error': 'Username and password are required'}), 400
        
        if len(username) < 3:
            return jsonify({'ok': False, 'error': 'Username must be at least 3 characters'}), 400
        
        if len(password) < 8:
            return jsonify({'ok': False, 'error': 'Password must be at least 8 characters'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({'ok': False, 'error': 'Username already exists'}), 400
        
        # Create user
        new_user = User(
            username=username,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f'New user registered: {username}')
        return jsonify({'ok': True, 'message': 'Registration successful'})
    
    except Exception as e:
        logger.error(f'Registration error: {str(e)}')
        db.session.rollback()
        return jsonify({'ok': False, 'error': 'Registration failed'}), 500


@api_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json() or {}
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'ok': False, 'error': 'Username and password are required'}), 400
        
        # Check for admin
        admin_password = os.getenv('ADMIN_PASSWORD', 'Admin&4')
        if username.lower() == 'admin' and password == admin_password:
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    password=generate_password_hash(password, method='pbkdf2:sha256')
                )
                db.session.add(admin)
                db.session.commit()
            login_user(admin)
            logger.info('Admin logged in')
            return jsonify({'ok': True, 'message': 'Logged in as admin', 'is_admin': True})
        
        # Regular user login
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            logger.warning(f'Failed login attempt for: {username}')
            return jsonify({'ok': False, 'error': 'Invalid credentials'}), 401
        
        login_user(user)
        logger.info(f'User logged in: {username}')
        return jsonify({'ok': True, 'message': 'Login successful', 'is_admin': False})
    
    except Exception as e:
        logger.error(f'Login error: {str(e)}')
        return jsonify({'ok': False, 'error': 'Login failed'}), 500


@api_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """User logout"""
    username = current_user.username
    logout_user()
    logger.info(f'User logged out: {username}')
    return jsonify({'ok': True, 'message': 'Logged out successfully'})


@api_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user information"""
    try:
        user_data = current_user.to_dict(include_sensitive=True)
        return jsonify({'ok': True, 'user': user_data})
    except Exception as e:
        logger.error(f'Error fetching user data: {str(e)}')
        return jsonify({'ok': False, 'error': 'Failed to fetch user data'}), 500


@api_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Get or update user profile"""
    if request.method == 'GET':
        try:
            return jsonify({
                'ok': True,
                'profile': {
                    'age': current_user.age,
                    'height_cm': current_user.height_cm,
                    'weight_kg': current_user.weight_kg,
                    'profile_completed': current_user.profile_completed
                }
            })
        except Exception as e:
            logger.error(f'Error fetching profile: {str(e)}')
            return jsonify({'ok': False, 'error': 'Failed to fetch profile'}), 500
    
    # POST - Update profile
    try:
        data = request.get_json() or {}
        
        age = data.get('age')
        height = data.get('height_cm') or data.get('height')
        weight = data.get('weight_kg') or data.get('weight')
        
        # Validation
        if age is None or height is None or weight is None:
            return jsonify({'ok': False, 'error': 'Age, height_cm, and weight_kg are required'}), 400
        
        age = int(age)
        height = float(height)
        weight = float(weight)
        
        if not (1 <= age <= 120):
            return jsonify({'ok': False, 'error': 'Age must be between 1 and 120'}), 400
        if not (50 <= height <= 300):
            return jsonify({'ok': False, 'error': 'Height must be between 50 and 300 cm'}), 400
        if not (20 <= weight <= 500):
            return jsonify({'ok': False, 'error': 'Weight must be between 20 and 500 kg'}), 400
        
        # Update user
        user = User.query.get(current_user.id)
        user.age = age
        user.height_cm = height
        user.weight_kg = weight
        db.session.commit()
        
        logger.info(f'Profile updated for user: {current_user.username}')
        return jsonify({'ok': True, 'message': 'Profile updated successfully'})
    
    except ValueError:
        return jsonify({'ok': False, 'error': 'Invalid numeric values'}), 400
    except Exception as e:
        logger.error(f'Profile update error: {str(e)}')
        db.session.rollback()
        return jsonify({'ok': False, 'error': 'Profile update failed'}), 500


# ============================================================================
# WORKOUT MANAGEMENT
# ============================================================================

@api_bp.route('/workouts', methods=['GET'])
@login_required
def get_workouts():
    """Get all workouts for current user"""
    try:
        workouts = Workout.query.filter_by(user_id=current_user.id)\
            .order_by(Workout.date.desc()).all()
        
        workouts_data = [workout.to_dict() for workout in workouts]
        return jsonify({'ok': True, 'workouts': workouts_data})
    
    except Exception as e:
        logger.error(f'Error fetching workouts: {str(e)}')
        return jsonify({'ok': False, 'error': 'Failed to fetch workouts'}), 500


@api_bp.route('/workouts/<int:workout_id>', methods=['GET'])
@login_required
def get_workout_detail(workout_id):
    """Get detailed information about a specific workout"""
    try:
        workout = Workout.query.filter_by(id=workout_id, user_id=current_user.id).first()
        
        if not workout:
            return jsonify({'ok': False, 'error': 'Workout not found'}), 404
        
        workout_data = workout.to_dict(include_exercises=True)
        return jsonify({'ok': True, 'workout': workout_data})
    
    except Exception as e:
        logger.error(f'Error fetching workout detail: {str(e)}')
        return jsonify({'ok': False, 'error': 'Failed to fetch workout'}), 500


@api_bp.route('/workouts', methods=['POST'])
@login_required
def create_workout():
    """Create a new workout"""
    try:
        data = request.get_json() or {}
        
        # Parse date
        date_str = data.get('date')
        try:
            workout_date = datetime.date.fromisoformat(date_str) if date_str else datetime.date.today()
        except (ValueError, TypeError):
            return jsonify({'ok': False, 'error': 'Invalid date format (use YYYY-MM-DD)'}), 400
        
        note = data.get('note', '')
        exercises = data.get('exercises', [])
        
        # Create workout
        workout = Workout(
            user_id=current_user.id,
            date=workout_date,
            note=note
        )
        db.session.add(workout)
        db.session.flush()  # Get workout.id before adding exercises
        
        # Add exercises
        for ex_data in exercises:
            if not ex_data.get('name'):
                continue
            
            exercise = WorkoutExercise(
                workout_id=workout.id,
                name=ex_data['name'],
                sets=int(ex_data.get('sets', 3)),
                reps=int(ex_data.get('reps', 10)),
                weight=float(ex_data['weight']) if ex_data.get('weight') else None
            )
            db.session.add(exercise)
        
        db.session.commit()
        
        logger.info(f'Workout created: {workout.id} for user {current_user.username}')
        return jsonify({'ok': True, 'id': workout.id}), 201
    
    except ValueError as e:
        return jsonify({'ok': False, 'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        logger.error(f'Error creating workout: {str(e)}')
        db.session.rollback()
        return jsonify({'ok': False, 'error': 'Failed to create workout'}), 500


@api_bp.route('/workouts/<int:workout_id>', methods=['DELETE'])
@login_required
def delete_workout(workout_id):
    """Delete a workout"""
    try:
        workout = Workout.query.filter_by(id=workout_id, user_id=current_user.id).first()
        
        if not workout:
            return jsonify({'ok': False, 'error': 'Workout not found'}), 404
        
        db.session.delete(workout)
        db.session.commit()
        
        logger.info(f'Workout deleted: {workout_id} by user {current_user.username}')
        return jsonify({'ok': True, 'message': 'Workout deleted successfully'})
    
    except Exception as e:
        logger.error(f'Error deleting workout: {str(e)}')
        db.session.rollback()
        return jsonify({'ok': False, 'error': 'Failed to delete workout'}), 500


# ============================================================================
# EXERCISE MANAGEMENT
# ============================================================================

@api_bp.route('/exercises/<int:workout_id>/add', methods=['POST'])
@login_required
def add_exercise(workout_id):
    """Add an exercise to a workout"""
    try:
        workout = Workout.query.filter_by(id=workout_id, user_id=current_user.id).first()
        
        if not workout:
            return jsonify({'ok': False, 'error': 'Workout not found'}), 404
        
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'ok': False, 'error': 'Exercise name is required'}), 400
        
        exercise = WorkoutExercise(
            workout_id=workout.id,
            name=name,
            sets=int(data.get('sets', 3)),
            reps=int(data.get('reps', 10)),
            weight=float(data['weight']) if data.get('weight') else None
        )
        db.session.add(exercise)
        db.session.commit()
        
        logger.info(f'Exercise added to workout {workout_id}: {name}')
        return jsonify({'ok': True, 'id': exercise.id}), 201
    
    except ValueError as e:
        return jsonify({'ok': False, 'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        logger.error(f'Error adding exercise: {str(e)}')
        db.session.rollback()
        return jsonify({'ok': False, 'error': 'Failed to add exercise'}), 500


@api_bp.route('/exercises/<int:exercise_id>', methods=['DELETE'])
@login_required
def delete_exercise(exercise_id):
    """Delete an exercise"""
    try:
        exercise = WorkoutExercise.query\
            .join(Workout)\
            .filter(Workout.user_id == current_user.id, WorkoutExercise.id == exercise_id)\
            .first()
        
        if not exercise:
            return jsonify({'ok': False, 'error': 'Exercise not found'}), 404
        
        workout_id = exercise.workout_id
        db.session.delete(exercise)
        db.session.commit()
        
        logger.info(f'Exercise deleted: {exercise_id}')
        return jsonify({'ok': True, 'workout_id': workout_id})
    
    except Exception as e:
        logger.error(f'Error deleting exercise: {str(e)}')
        db.session.rollback()
        return jsonify({'ok': False, 'error': 'Failed to delete exercise'}), 500


# ============================================================================
# CATALOG & UTILITIES
# ============================================================================

@api_bp.route('/catalog', methods=['GET'])
@login_required
def get_exercise_catalog():
    """Get list of available exercises"""
    catalog = [
        'Bench press', 'Dřep', 'Mrtvý tah', 'Přítahy na hrazdě',
        'Tlaky na ramena', 'Biceps zdvih', 'Triceps kliky',
        'Výpady', 'Leg press', 'Veslování', 'Kettlebell swing', 'Plank'
    ]
    return jsonify({'ok': True, 'exercises': catalog})


@api_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """Get user statistics"""
    try:
        total_workouts = Workout.query.filter_by(user_id=current_user.id).count()
        
        recent_workouts = Workout.query.filter_by(user_id=current_user.id)\
            .order_by(Workout.date.desc()).limit(5).all()
        
        recent_exercises = sum(workout.exercises.count() for workout in recent_workouts)
        
        return jsonify({
            'ok': True,
            'stats': {
                'total_workouts': total_workouts,
                'recent_exercises': recent_exercises
            }
        })
    
    except Exception as e:
        logger.error(f'Error fetching stats: {str(e)}')
        return jsonify({'ok': False, 'error': 'Failed to fetch statistics'}), 500


@api_bp.route('/quickstart/<level>', methods=['POST'])
@login_required
def quickstart_workout(level):
    """Create a workout from a predefined template"""
    try:
        level = level.lower()
        
        presets = {
            'zacatecnik': {'label': 'Začátečník', 'sets': 3, 'reps': 10},
            'pokracily': {'label': 'Pokročilý', 'sets': 4, 'reps': 10},
            'expert': {'label': 'Expert', 'sets': 5, 'reps': 8}
        }
        
        if level not in presets:
            return jsonify({'ok': False, 'error': 'Invalid level (use: zacatecnik, pokracily, expert)'}), 400
        
        config = presets[level]
        
        workout = Workout(
            user_id=current_user.id,
            date=datetime.date.today(),
            note=f"Rychlý start – {config['label']}"
        )
        db.session.add(workout)
        db.session.flush()
        
        # Add default exercises
        default_exercises = ['Dřep', 'Bench press', 'Veslování']
        for name in default_exercises:
            exercise = WorkoutExercise(
                workout_id=workout.id,
                name=name,
                sets=config['sets'],
                reps=config['reps']
            )
            db.session.add(exercise)
        
        db.session.commit()
        
        logger.info(f'Quickstart workout created: {level} for user {current_user.username}')
        return jsonify({'ok': True, 'id': workout.id})
    
    except Exception as e:
        logger.error(f'Error creating quickstart workout: {str(e)}')
        db.session.rollback()
        return jsonify({'ok': False, 'error': 'Failed to create workout'}), 500


# ============================================================================
# EXPORT
# ============================================================================

@api_bp.route('/export/csv', methods=['GET'])
@login_required
def export_csv():
    """Export user workouts to CSV"""
    try:
        si = io.StringIO()
        writer = csv.writer(si)
        
        # CSV headers (Czech)
        writer.writerow(['ID', 'Datum', 'Poznámka', 'Cvik', 'Série', 'Opakování', 'Váha (kg)'])
        
        workouts = Workout.query.filter_by(user_id=current_user.id)\
            .order_by(Workout.date.desc()).all()
        
        for workout in workouts:
            for exercise in workout.exercises:
                writer.writerow([
                    workout.id,
                    workout.date.strftime('%d.%m.%Y'),
                    workout.note or '',
                    exercise.name,
                    exercise.sets,
                    exercise.reps,
                    exercise.weight or ''
                ])
        
        csv_data = si.getvalue()
        logger.info(f'CSV export for user {current_user.username}')
        return jsonify({'ok': True, 'csv': csv_data})
    
    except Exception as e:
        logger.error(f'CSV export error: {str(e)}')
        return jsonify({'ok': False, 'error': 'Export failed'}), 500


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@api_bp.route('/admin/users', methods=['GET'])
@login_required
def admin_get_users():
    """Get all users (admin only)"""
    if current_user.username != 'admin':
        return jsonify({'ok': False, 'error': 'Unauthorized'}), 403
    
    try:
        users = User.query.order_by(User.id.asc()).all()
        
        users_data = []
        for user in users:
            user_info = user.to_dict()
            user_info['workout_count'] = Workout.query.filter_by(user_id=user.id).count()
            users_data.append(user_info)
        
        return jsonify({'ok': True, 'users': users_data})
    
    except Exception as e:
        logger.error(f'Admin users fetch error: {str(e)}')
        return jsonify({'ok': False, 'error': 'Failed to fetch users'}), 500


# ============================================================================
# OAUTH (GOOGLE)
# ============================================================================

@api_bp.route('/google/login', methods=['GET'])
def google_login():
    """Initiate Google OAuth login"""
    try:
        from backend.oauth import oauth, is_configured
        
        if not is_configured() or oauth is None:
            return jsonify({'ok': False, 'error': 'Google OAuth is not configured'}), 501
        
        redirect_uri = url_for('api.google_callback', _external=True)
        auth_url, state = oauth.google.create_authorization_url(redirect_uri)
        
        return jsonify({'ok': True, 'auth_url': auth_url, 'state': state})
    
    except Exception as e:
        logger.error(f'Google login error: {str(e)}')
        return jsonify({'ok': False, 'error': 'OAuth initialization failed'}), 500


@api_bp.route('/google/callback', methods=['GET'])
def google_callback():
    """Handle Google OAuth callback"""
    try:
        from backend.oauth import oauth, is_configured
        
        if not is_configured() or oauth is None:
            return redirect('http://localhost:8501/?auth=error&msg=OAuth+not+configured')
        
        token = oauth.google.authorize_access_token()
        userinfo = token.get('userinfo')
        
        if not userinfo:
            try:
                userinfo = oauth.google.parse_id_token(token)
            except Exception:
                pass
        
        if not userinfo:
            return redirect('http://localhost:8501/?auth=error&msg=Failed+to+get+user+info')
        
        sub = userinfo.get('sub')
        email = userinfo.get('email')
        name = userinfo.get('name') or (email.split('@')[0] if email else f'user_{sub[:6]}')
        
        # Find or create user
        user = User.query.filter(
            (User.oauth_provider == 'google') & (User.oauth_sub == sub)
        ).first()
        
        if not user and email:
            user = User.query.filter_by(email=email).first()
        
        if not user:
            user = User(
                username=name,
                email=email,
                oauth_provider='google',
                oauth_sub=sub,
                password=generate_password_hash(os.urandom(16).hex())
            )
            db.session.add(user)
            db.session.commit()
        
        login_user(user)
        logger.info(f'Google OAuth login: {user.username}')
        return redirect('http://localhost:8501/?auth=success')
    
    except Exception as e:
        logger.error(f'Google callback error: {str(e)}')
        return redirect(f'http://localhost:8501/?auth=error&msg={str(e)}')
