from flask import render_template, request, redirect, url_for, flash, Response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature
import os
import io
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import date

from app import app, db
from models import User, Workout, WorkoutExercise
from forms import RegisterForm, LoginForm, WorkoutForm, ExerciseForm
from oauth import oauth

BRAND = "FitTrack"

# URL encryption functions
def get_serializer():
    """Get URL serializer for encrypting/decrypting URLs"""
    return URLSafeTimedSerializer(app.config['SECRET_KEY'])

def encrypt_exercise_id(exercise_id):
    """Encrypt exercise ID for secure URL"""
    serializer = get_serializer()
    return serializer.dumps({'eid': exercise_id}, salt='exercise-delete')

def decrypt_exercise_id(encrypted_data):
    """Decrypt exercise ID from secure URL"""
    serializer = get_serializer()
    try:
        data = serializer.loads(encrypted_data, salt='exercise-delete', max_age=3600)  # 1 hour expiry
        return data['eid']
    except BadSignature:
        return None

@app.context_processor
def inject_crypto_functions():
    """Make encryption functions available in templates"""
    return {
        'encrypt_exercise_id': encrypt_exercise_id
    }

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('workouts'))
    return render_template("index.html")

@app.route("/welcome")
@login_required
def welcome():
    # Simple dashboard data
    recent = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc()).limit(5).all()
    total_workouts = Workout.query.filter_by(user_id=current_user.id).count()
    total_exercises = sum(len(w.exercises) for w in recent)
    stats = {"total_workouts": total_workouts, "recent_exercises": total_exercises}
    return render_template("welcome.html", brand=BRAND, last_workouts=recent, stats=stats)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if User.query.filter_by(username=username).first():
            flash("Uživatelské jméno již existuje.", "error")
            return redirect(url_for("register"))

        new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        flash("Registrace byla úspěšná! Nyní se přihlaste.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # Speciální admin účet podle požadavku
        admin_password = os.getenv('ADMIN_PASSWORD', 'Admin&4')
        if username.lower() == 'admin' and password == admin_password:
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin', password=generate_password_hash(password, method='pbkdf2:sha256'))
                db.session.add(admin)
                db.session.commit()
            login_user(admin)
            flash('Úspěšné přihlášení (admin).', 'success')
            return redirect(url_for('admin'))
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Přihlášení proběhlo úspěšně.', 'success')
            return redirect(url_for("welcome"))
        flash("Špatné přihlašovací jméno nebo heslo.", "error")
    return render_template("login.html", form=form)

@app.route('/login/google')
def login_google():
    redirect_uri = url_for('auth_google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/auth/google/callback')
def auth_google_callback():
    token = oauth.google.authorize_access_token()
    userinfo = token.get('userinfo')
    if not userinfo:
        try:
            # Fallback for some providers that return id_token but not userinfo
            userinfo = oauth.google.parse_id_token(token)
        except Exception as e:
            flash(f'Přihlášení přes Google selhalo: {e}', 'error')
            return redirect(url_for('login'))
    
    if not userinfo:
        flash('Přihlášení přes Google selhalo: Nepodařilo se získat informace o uživateli.', 'error')
        return redirect(url_for('login'))
    sub = userinfo.get('sub')
    email = userinfo.get('email')
    name = userinfo.get('name') or (email.split('@')[0] if email else None)

    user = User.query.filter((User.oauth_provider=='google') & (User.oauth_sub==sub)).first()
    if not user and email:
        user = User.query.filter_by(email=email).first()
    if not user:
        user = User(username=name or f'user_{sub[:6]}', email=email, oauth_provider='google', oauth_sub=sub, password=generate_password_hash(os.urandom(16).hex()))
        db.session.add(user)
        db.session.commit()
    login_user(user)
    flash('Přihlášení přes Google úspěšné.', 'success')
    return redirect(url_for('welcome'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/protected")
@login_required
def protected():
    return render_template("protected.html")

@app.route('/admin')
@login_required
def admin():
    if current_user.username != 'admin':
        flash('Nemáte oprávnění.', 'error')
        return redirect(url_for('index'))
    # Jednoduchá admin stránka
    users = User.query.order_by(User.id.asc()).all()
    return render_template('admin.html', users=users)

@app.route('/workouts')
@login_required
def workouts():
    items = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc()).all()
    # Data pro graf: počet cviků v tréninku
    labels = [w.date.strftime('%Y-%m-%d') for w in items]
    values = [len(w.exercises) for w in items]
    return render_template('workouts.html', workouts=items, chart_labels=labels, chart_values=values)

@app.route('/workouts/new', methods=['GET', 'POST'])
@login_required
def workout_new():
    form = WorkoutForm()
    if form.validate_on_submit():
        w = Workout(user_id=current_user.id, date=form.date.data, note=form.note.data)
        db.session.add(w)
        db.session.commit()
        flash('Trénink vytvořen.', 'success')
        return redirect(url_for('workouts'))
    return render_template('workout_form.html', form=form)

@app.route('/workouts/<int:wid>', methods=['GET', 'POST'])
@login_required
def workout_detail(wid):
    w = Workout.query.filter_by(id=wid, user_id=current_user.id).first_or_404()
    form = ExerciseForm()
    if form.validate_on_submit():
        ex = WorkoutExercise(workout_id=w.id, name=form.name.data, sets=form.sets.data, reps=form.reps.data, weight=form.weight.data)
        db.session.add(ex)
        db.session.commit()
        flash('Cvik přidán.', 'success')
        return redirect(url_for('workout_detail', wid=w.id))
    exercises = WorkoutExercise.query.filter_by(workout_id=w.id).all()
    return render_template('workout_detail.html', workout=w, exercises=exercises, form=form)

@app.route('/workouts/quickadd', methods=['POST'])
@login_required
def workouts_quickadd():
    names = request.form.getlist('exercises')
    if not names:
        flash('Nevybral jsi žádné cviky.', 'error')
        return redirect(url_for('exercise_catalog'))
    w = Workout(user_id=current_user.id)
    db.session.add(w)
    db.session.flush()
    for n in names:
        ex = WorkoutExercise(workout_id=w.id, name=n, sets=3, reps=10)
        db.session.add(ex)
    db.session.commit()
    flash('Trénink a vybrané cviky byly vytvořeny.', 'success')
    return redirect(url_for('workout_detail', wid=w.id))

@app.route('/exercises/catalog', methods=['GET'])
@login_required
def exercise_catalog():
    catalog = [
        'Bench press','Dřep','Mrtvý tah','Přítahy na hrazdě','Tlaky na ramena',
        'Biceps zdvih','Triceps kliky','Výpady','Leg press','Veslování',
        'Kettlebell swing','Plank',
    ]
    return render_template('exercise_catalog.html', catalog=catalog)

@app.route('/workouts/<int:wid>/delete')
@login_required
def workout_delete(wid):
    w = Workout.query.filter_by(id=wid, user_id=current_user.id).first_or_404()
    db.session.delete(w)
    db.session.commit()
    flash('Trénink smazán.', 'success')
    return redirect(url_for('workouts'))

@app.route('/exercises/<int:eid>/delete')
@login_required
def exercise_delete(eid):
    ex = WorkoutExercise.query.join(Workout).filter(Workout.user_id==current_user.id, WorkoutExercise.id==eid).first_or_404()
    wid = ex.workout_id
    db.session.delete(ex)
    db.session.commit()
    flash('Cvik smazán.', 'success')
    return redirect(url_for('workout_detail', wid=wid))

@app.route('/exercises/delete/<encrypted_id>')
@login_required 
def exercise_delete_encrypted(encrypted_id):
    """Delete exercise with encrypted ID"""
    eid = decrypt_exercise_id(encrypted_id)
    if not eid:
        flash('Neplatný nebo vypršený odkaz.', 'error')
        return redirect(url_for('workouts'))
    
    ex = WorkoutExercise.query.join(Workout).filter(Workout.user_id==current_user.id, WorkoutExercise.id==eid).first_or_404()
    wid = ex.workout_id
    db.session.delete(ex)
    db.session.commit()
    flash('Cvik smazán.', 'success')
    return redirect(url_for('workout_detail', wid=wid))

@app.route('/export/csv')
@login_required
def export_csv():
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
    return Response(output, mimetype='text/csv', headers={'Content-Disposition':'attachment;filename=fittrack.csv'})

@app.route('/export/pdf')
@login_required
def export_pdf():
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    # Nastavení fontu s podporou češtiny
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        # Try common paths for DejaVu font
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            'C:/Windows/Fonts/DejaVuSans.ttf', # Windows path
            'DejaVuSans.ttf' # Relative path
        ]
        font_path_found = None
        for path in font_paths:
            if os.path.exists(path):
                font_path_found = path
                break
        
        if font_path_found:
            pdfmetrics.registerFont(TTFont('DejaVu', font_path_found))
            p.setFont('DejaVu', 12)
        else:
            # Fallback if font is not found
            p.setFont('Helvetica', 12)
    except ImportError:
        # Fallback if reportlab is not fully installed or font modules are missing
        p.setFont('Helvetica', 12)
    
    text = p.beginText(40, 800)
    try:
        text.setFont('DejaVu', 12)
    except:
        text.setFont('Helvetica', 12)
    text.textLine(f"{BRAND} – Přehled tréninků")
    y = 780
    workouts = Workout.query.filter_by(user_id=current_user.id).all()
    for w in workouts:
        line = f"{w.date.strftime('%d.%m.%Y')} – {w.note or ''}"
        text.textLine(line)
        for e in w.exercises:
            text.textLine(f"  • {e.name} {e.sets}x{e.reps} {e.weight or ''}kg")
        y -= 14
        if y < 80:
            p.drawText(text)
            p.showPage()
            text = p.beginText(40, 800)
            try:
                text.setFont('DejaVu', 12)
            except:
                text.setFont('Helvetica', 12)
            y = 780
    p.drawText(text)
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    return Response(pdf, mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=fittrack.pdf'})

@app.route('/timer')
@login_required
def timer():
    return render_template('timer.html', mode='basic')

@app.route('/timer/hiit')
@login_required
def timer_hiit():
    return render_template('timer.html', mode='hiit')

@app.route('/timer/circuit')
@login_required
def timer_circuit():
    return render_template('timer.html', mode='circuit')

@app.route('/quickstart/<level>')
@login_required
def quickstart_level(level: str):
    level = level.lower()
    presets = {
        'zacatecnik': {'label': 'Začátečník', 'sets': 3, 'reps': 10, 'rest': 90},
        'pokracily': {'label': 'Pokročilý', 'sets': 4, 'reps': 10, 'rest': 60},
        'expert': {'label': 'Expert', 'sets': 5, 'reps': 8, 'rest': 45},
        'beginner': {'label': 'Začátečník', 'sets': 3, 'reps': 10, 'rest': 90},
        'intermediate': {'label': 'Pokročilý', 'sets': 4, 'reps': 10, 'rest': 60},
        'advanced': {'label': 'Expert', 'sets': 5, 'reps': 8, 'rest': 45},
    }
    cfg = presets.get(level)
    if not cfg:
        flash('Neplatná úroveň rychlého startu.', 'error')
        return redirect(url_for('welcome'))
    w = Workout(user_id=current_user.id, date=date.today(), note=f"Rychlý start – {cfg['label']}")
    db.session.add(w)
    db.session.flush()
    defaults = ['Dřep', 'Bench press', 'Veslování']
    for name in defaults:
        db.session.add(WorkoutExercise(workout_id=w.id, name=name, sets=cfg['sets'], reps=cfg['reps']))
    db.session.commit()
    flash(f"Vytvořen trénink ({cfg['label']}).", 'success')
    return redirect(url_for('workout_detail', wid=w.id))

@app.route('/quickstart/template/<slug>')
@login_required
def quickstart_template(slug: str):
    slug = slug.lower()
    templates = {
        'cele-telo': ['Dřep', 'Bench press', 'Přítahy na hrazdě', 'Tlaky na ramena'],
        'domaci-hiit': ['Burpees', 'Horolezci', 'Skákací dřepy', 'Plank'],
        'protazeni-po-behu': ['Hamstring stretch', 'Quadriceps stretch', 'Calf stretch', 'Hip flexor stretch'],
        'full-body': ['Dřep', 'Bench press', 'Veslování'],
        'hiit-home': ['Burpees', 'Horolezci', 'Skákací dřepy'],
        'stretch-after-run': ['Hamstring stretch', 'Quadriceps stretch', 'Calf stretch'],
    }
    exs = templates.get(slug)
    if not exs:
        flash('Šablona nenalezena.', 'error')
        return redirect(url_for('welcome'))
    w = Workout(user_id=current_user.id, date=date.today(), note=f"Šablona – {slug}")
    db.session.add(w)
    db.session.flush()
    for name in exs:
        db.session.add(WorkoutExercise(workout_id=w.id, name=name, sets=3, reps=12))
    db.session.commit()
    flash('Trénink ze šablony vytvořen.', 'success')
    return redirect(url_for('workout_detail', wid=w.id))
