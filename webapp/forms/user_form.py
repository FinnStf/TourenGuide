from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo


class UserForm(FlaskForm):
    first_name = StringField('Vorname', description='Vorname',
                             validators=[DataRequired()])
    last_name = StringField('Nachname', description='Name',
                            validators=[DataRequired()])
    email = StringField('E-Mail', description='Email-Adresse',
                        validators=[DataRequired(), Email()])
    password = PasswordField("Passwort", validators=[DataRequired()])
    password_repeat = PasswordField("Passwort wiederholen",
                                    validators=[DataRequired(),
                                                EqualTo("password", "Passwörter stimmen nicht überein")])


class UserUpdateForm(UserForm):
    submit = SubmitField("Update")


class UserInsertForm(UserForm):
    submit = SubmitField("Erstellen")
