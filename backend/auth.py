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

from backend import app, db
from backend.models import User, Workout, WorkoutExercise
from backend.forms import RegisterForm, LoginForm, WorkoutForm, ExerciseForm
from backend.oauth import oauth

BRAND = "FitTrack"

def get_serializer():
    return URLSafeTimedSerializer(app.config['SECRET_KEY'])

def encrypt_exercise_id(exercise_id):
    serializer = get_serializer()
    return serializer.dumps({'eid': exercise_id}, salt='exercise-delete')

def decrypt_exercise_id(encrypted_data):
    serializer = get_serializer()
    try:
        data = serializer.loads(encrypted_data, salt='exercise-delete', max_age=3600)
        return data['eid']
    except BadSignature:
        return None

@app.context_processor
def inject_crypto_functions():
    return {'encrypt_exercise_id': encrypt_exercise_id}

# The rest of routes are intentionally not copied here to keep backend auth module small.
