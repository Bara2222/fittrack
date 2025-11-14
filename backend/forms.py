from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp, EqualTo, ValidationError

class RegisterForm(FlaskForm):
    username = StringField('U\u017eivatelske jmeno', validators=[DataRequired(), Length(min=3, max=150), Regexp(r'^[A-Za-z0-9]+$', message='Pou\u017eij pouze p\u00edsmena a \u010d\u00edsla')])
    password = PasswordField('Heslo', validators=[DataRequired(), Length(min=8, message='Minimalne 8 znaku')])
    confirm_password = PasswordField('Potvrdit heslo', validators=[DataRequired(), EqualTo('password', message='Hesla se neshoduji')])
    submit = SubmitField('Registrovat')

    def validate_password(self, field):
        pw = field.data or ''
        if not any(c.islower() for c in pw) or not any(c.isupper() for c in pw) or not any(c.isdigit() for c in pw) or not any(c in '!@#$%^&*()-_=+[]{};:,.<>/\\?|`~' for c in pw):
            raise ValidationError('Heslo musi mit male i velke pismeno, cislo a specialni znak')

class LoginForm(FlaskForm):
    username = StringField('U\u017eivatelske jmeno', validators=[DataRequired(), Regexp(r'^[A-Za-z0-9]+$', message='Pou\u017eij pouze p\u00edsmena a \u010d\u00edsla')])
    password = PasswordField('Heslo', validators=[DataRequired()])
    submit = SubmitField('Prihlasit')

class WorkoutForm(FlaskForm):
    date = DateField('Datum', validators=[DataRequired()], format='%Y-%m-%d')
    note = TextAreaField('Poznamka')
    submit = SubmitField('Ulozit trenink')

class ExerciseForm(FlaskForm):
    name = StringField('Nazev cviku', validators=[DataRequired(), Length(min=2, max=120)])
    sets = IntegerField('Serie', validators=[DataRequired(), NumberRange(min=1, max=20)])
    reps = IntegerField('Opakovani', validators=[DataRequired(), NumberRange(min=1, max=100)])
    weight = FloatField('Vaha (kg)')
    submit = SubmitField('Pridat cvik')
