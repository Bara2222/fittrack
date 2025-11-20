from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp, EqualTo, ValidationError

class RegisterForm(FlaskForm):
    username = StringField('Uživatelské jméno', validators=[DataRequired(), Length(min=3, max=150), Regexp(r'^[A-Za-z0-9]+$', message='Použij pouze písmena a čísla')])
    password = PasswordField('Heslo', validators=[DataRequired(), Length(min=8, message='Minimálně 8 znaků')])
    confirm_password = PasswordField('Potvrdit heslo', validators=[DataRequired(), EqualTo('password', message='Hesla se neshodují')])
    submit = SubmitField('Registrovat')

    def validate_password(self, field):
        pw = field.data or ''
        if not any(c.islower() for c in pw) or not any(c.isupper() for c in pw) or not any(c.isdigit() for c in pw) or not any(c in '!@#$%^&*()-_=+[]{};:,.<>/\\?|`~' for c in pw):
            raise ValidationError('Heslo musí mít malé i velké písmeno, číslo a speciální znak')

class LoginForm(FlaskForm):
    username = StringField('Uživatelské jméno', validators=[DataRequired(), Regexp(r'^[A-Za-z0-9]+$', message='Použij pouze písmena a čísla')])
    password = PasswordField('Heslo', validators=[DataRequired()])
    submit = SubmitField('Přihlásit')

class WorkoutForm(FlaskForm):
    date = DateField('Datum', validators=[DataRequired()], format='%Y-%m-%d')
    note = TextAreaField('Poznámka')
    submit = SubmitField('Uložit trénink')

class ExerciseForm(FlaskForm):
    name = StringField('Název cviku', validators=[DataRequired(), Length(min=2, max=120)])
    sets = IntegerField('Série', validators=[DataRequired(), NumberRange(min=1, max=20)])
    reps = IntegerField('Opakování', validators=[DataRequired(), NumberRange(min=1, max=100)])
    weight = FloatField('Váha (kg)')
    submit = SubmitField('Přidat cvik')
