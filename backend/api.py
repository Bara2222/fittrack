from flask import Blueprint, jsonify, request, session, url_for, redirect
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db, app
from models import User, Workout, WorkoutExercise
from flask_cors import CORS
import datetime
import os
import io
import csv

api_bp = Blueprint('api', __name__)
CORS(api_bp, supports_credentials=True, origins=['http://localhost:8501', 'http://127.0.0.1:8501'])


@api_bp.route('/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'ok': False, 'error': 'username and password required'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'ok': False, 'error': 'username already exists'}), 400
    new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'ok': True, 'message': 'registered successfully'})


@api_bp.route('/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'ok': False, 'error': 'username and password required'}), 400
    
    # Check for admin
    admin_password = os.getenv('ADMIN_PASSWORD', 'Admin&4')
    if username.lower() == 'admin' and password == admin_password:
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(admin)
            db.session.commit()
        login_user(admin)
        return jsonify({'ok': True, 'message': 'logged in as admin', 'is_admin': True})
    
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'ok': False, 'error': 'invalid credentials'}), 401
    login_user(user)
    return jsonify({'ok': True, 'message': 'logged in', 'is_admin': False})


@api_bp.route('/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({'ok': True, 'message': 'logged out'})


@api_bp.route('/me', methods=['GET'])
@login_required
def api_me():
    profile_completed = all([
        current_user.age is not None,
        current_user.height_cm is not None,
        current_user.weight_kg is not None
    ])
    return jsonify({'ok': True, 'user': {
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email or '',
        'is_admin': current_user.username == 'admin',
        'age': current_user.age,
        'height_cm': current_user.height_cm,
        'weight_kg': current_user.weight_kg,
        'profile_completed': profile_completed
    }})


@api_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def api_profile():
    """GET returns current profile fields. POST updates age/height/weight."""
    if request.method == 'GET':
        return jsonify({'ok': True, 'profile': {
            'age': current_user.age,
            'height_cm': current_user.height_cm,
            'weight_kg': current_user.weight_kg,
            'profile_completed': all([current_user.age is not None, current_user.height_cm is not None, current_user.weight_kg is not None])
        }})

    data = request.get_json() or {}
    try:
        age = data.get('age')
        height = data.get('height_cm') or data.get('height')
        weight = data.get('weight_kg') or data.get('weight')
        # Basic validation
        if age is None or height is None or weight is None:
            return jsonify({'ok': False, 'error': 'age, height_cm and weight_kg are required'}), 400
        age = int(age)
        height = float(height)
        weight = float(weight)
        if age <= 0 or height <= 0 or weight <= 0:
            return jsonify({'ok': False, 'error': 'values must be positive'}), 400

        # persist
        u = User.query.get(current_user.id)
        u.age = age
        u.height_cm = height
        u.weight_kg = weight
        db.session.add(u)
        db.session.commit()
        return jsonify({'ok': True, 'message': 'profile updated'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@api_bp.route('/workouts', methods=['GET'])
@login_required
def api_workouts_list():
    items = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc()).all()
    out = []
    for w in items:
        out.append({'id': w.id, 'date': w.date.isoformat(), 'note': w.note or '', 'exercise_count': len(w.exercises)})
    return jsonify({'ok': True, 'workouts': out})


@api_bp.route('/workouts/<int:wid>', methods=['GET'])
@login_required
def api_workout_detail(wid):
    w = Workout.query.filter_by(id=wid, user_id=current_user.id).first()
    if not w:
        return jsonify({'ok': False, 'error': 'not found'}), 404
    exercises = []
    for e in w.exercises:
        exercises.append({'id': e.id, 'name': e.name, 'sets': e.sets, 'reps': e.reps, 'weight': e.weight})
    return jsonify({'ok': True, 'workout': {'id': w.id, 'date': w.date.isoformat(), 'note': w.note or '', 'exercises': exercises}})


@api_bp.route('/workouts', methods=['POST'])
@login_required
def api_workout_create():
    data = request.get_json() or {}
    date_s = data.get('date')
    note = data.get('note')
    exercises = data.get('exercises', [])
    try:
        date_obj = datetime.date.fromisoformat(date_s) if date_s else datetime.date.today()
    except Exception:
        return jsonify({'ok': False, 'error': 'invalid date'}), 400
    w = Workout(user_id=current_user.id, date=date_obj, note=note)
    db.session.add(w)
    db.session.flush()
    for ex in exercises:
        name = ex.get('name')
        sets = ex.get('sets', 3)
        reps = ex.get('reps', 10)
        weight = ex.get('weight')
        db.session.add(WorkoutExercise(workout_id=w.id, name=name, sets=sets, reps=reps, weight=weight))
    db.session.commit()
    return jsonify({'ok': True, 'id': w.id}), 201


@api_bp.route('/workouts/<int:wid>', methods=['DELETE'])
@login_required
def api_workout_delete(wid):
    w = Workout.query.filter_by(id=wid, user_id=current_user.id).first()
    if not w:
        return jsonify({'ok': False, 'error': 'not found'}), 404
    db.session.delete(w)
    db.session.commit()
    return jsonify({'ok': True, 'message': 'deleted'})


@api_bp.route('/exercises/<int:eid>', methods=['DELETE'])
@login_required
def api_exercise_delete(eid):
    ex = WorkoutExercise.query.join(Workout).filter(Workout.user_id==current_user.id, WorkoutExercise.id==eid).first()
    if not ex:
        return jsonify({'ok': False, 'error': 'not found'}), 404
    wid = ex.workout_id
    db.session.delete(ex)
    db.session.commit()
    return jsonify({'ok': True, 'workout_id': wid})


@api_bp.route('/exercises/<int:wid>/add', methods=['POST'])
@login_required
def api_exercise_add(wid):
    w = Workout.query.filter_by(id=wid, user_id=current_user.id).first()
    if not w:
        return jsonify({'ok': False, 'error': 'workout not found'}), 404
    data = request.get_json() or {}
    name = data.get('name')
    sets = data.get('sets', 3)
    reps = data.get('reps', 10)
    weight = data.get('weight')
    if not name:
        return jsonify({'ok': False, 'error': 'name required'}), 400
    ex = WorkoutExercise(workout_id=w.id, name=name, sets=sets, reps=reps, weight=weight)
    db.session.add(ex)
    db.session.commit()
    return jsonify({'ok': True, 'id': ex.id}), 201


@api_bp.route('/catalog', methods=['GET'])
@login_required
def api_exercise_catalog():
    catalog = [
        'Bench press','Dřep','Mrtvý tah','Přítahy na hrazdě','Tlaky na ramena',
        'Biceps zdvih','Triceps kliky','Výpady','Leg press','Veslování',
        'Kettlebell swing','Plank',
    ]
    return jsonify({'ok': True, 'exercises': catalog})


@api_bp.route('/export/csv', methods=['GET'])
@login_required
def api_export_csv():
    si = io.StringIO()
    cw = csv.writer(si)
    # Lokalizované hlavičky v češtině
    cw.writerow(['ID','Datum','Poznámka','Cvik','Série','Opakování','Váha (kg)'])
    workouts = Workout.query.filter_by(user_id=current_user.id).all()
    for w in workouts:
        for e in w.exercises:
            # Datum v českém formátu dd.mm.YYYY
            cw.writerow([w.id, w.date.strftime('%d.%m.%Y'), w.note or '', e.name, e.sets, e.reps, e.weight or ''])
    output = si.getvalue()
    return jsonify({'ok': True, 'csv': output})


@api_bp.route('/stats', methods=['GET'])
@login_required
def api_stats():
    recent = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc()).limit(5).all()
    total_workouts = Workout.query.filter_by(user_id=current_user.id).count()
    total_exercises = sum(len(w.exercises) for w in recent)
    return jsonify({'ok': True, 'stats': {'total_workouts': total_workouts, 'recent_exercises': total_exercises}})


@api_bp.route('/quickstart/<level>', methods=['POST'])
@login_required
def api_quickstart_level(level):
    level = level.lower()
    presets = {
        'zacatecnik': {'label': 'Začátečník', 'sets': 3, 'reps': 10},
        'pokracily': {'label': 'Pokročilý', 'sets': 4, 'reps': 10},
        'expert': {'label': 'Expert', 'sets': 5, 'reps': 8},
    }
    cfg = presets.get(level)
    if not cfg:
        return jsonify({'ok': False, 'error': 'invalid level'}), 400
    w = Workout(user_id=current_user.id, date=datetime.date.today(), note=f"Rychlý start – {cfg['label']}")
    db.session.add(w)
    db.session.flush()
    defaults = ['Dřep', 'Bench press', 'Veslování']
    for name in defaults:
        db.session.add(WorkoutExercise(workout_id=w.id, name=name, sets=cfg['sets'], reps=cfg['reps']))
    db.session.commit()
    return jsonify({'ok': True, 'id': w.id})


@api_bp.route('/admin/users', methods=['GET'])
@login_required
def api_admin_users():
    if current_user.username != 'admin':
        return jsonify({'ok': False, 'error': 'unauthorized'}), 403
    users = User.query.order_by(User.id.asc()).all()
    data = []
    for u in users:
        data.append({
            'id': u.id,
            'username': u.username,
            'email': u.email or '',
            'oauth_provider': u.oauth_provider or '',
            'created_at': u.created_at.isoformat() if u.created_at else '',
            'workout_count': Workout.query.filter_by(user_id=u.id).count()
        })
    return jsonify({'ok': True, 'users': data})


@api_bp.route('/google/login', methods=['GET'])
def api_google_login():
    """Return Google OAuth URL for frontend redirect"""
    try:
        from oauth import oauth
        redirect_uri = url_for('api.api_google_callback', _external=True)
        auth_url = oauth.google.create_authorization_url(redirect_uri)
        return jsonify({'ok': True, 'auth_url': auth_url[0], 'state': auth_url[1]})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@api_bp.route('/google/callback', methods=['GET'])
def api_google_callback():
    """Handle Google OAuth callback"""
    try:
        from oauth import oauth
        token = oauth.google.authorize_access_token()
        userinfo = token.get('userinfo')
        if not userinfo:
            try:
                userinfo = oauth.google.parse_id_token(token)
            except Exception:
                pass
        
        if not userinfo:
            return jsonify({'ok': False, 'error': 'Failed to get user info'}), 400
        
        sub = userinfo.get('sub')
        email = userinfo.get('email')
        name = userinfo.get('name') or (email.split('@')[0] if email else None)
        
        user = User.query.filter((User.oauth_provider=='google') & (User.oauth_sub==sub)).first()
        if not user and email:
            user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                username=name or f'user_{sub[:6]}',
                email=email,
                oauth_provider='google',
                oauth_sub=sub,
                password=generate_password_hash(os.urandom(16).hex())
            )
            db.session.add(user)
            db.session.commit()
        
        login_user(user)
        # Redirect to streamlit with success
        return redirect('http://localhost:8501/?auth=success')
    except Exception as e:
        return redirect(f'http://localhost:8501/?auth=error&msg={str(e)}')
