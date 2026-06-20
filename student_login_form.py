from flask_wtf import FlaskForm
from wtforms import StringField , PasswordField , EmailField , SubmitField
from wtforms.validators import DataRequired , Email , ValidationError

class StudentLoginForm(FlaskForm):
    regd = StringField("Regd no" , validators=[DataRequired()])
    password = PasswordField("Password" , validators=[DataRequired()])
    submit = SubmitField("Login")