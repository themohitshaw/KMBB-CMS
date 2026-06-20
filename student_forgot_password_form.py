from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import  EqualTo, Optional,Length

class StudentForgotForm(FlaskForm):

    regd = StringField("Registration Number", validators=[Optional()])

    otp = StringField("Enter OTP", validators=[Optional()])

    password = PasswordField(
        "New Password",
        validators=[Optional(), Length(min=8, message="Minimum 8 characters required")]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[Optional(), EqualTo('password', message="Passwords must match")]
    )

    submit = SubmitField("Submit")