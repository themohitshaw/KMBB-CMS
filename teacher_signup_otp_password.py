from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Optional,Length


class TeacherSignupForm(FlaskForm):

    # STEP 1
    regd = StringField(
        "Registration Number",
        validators=[Optional()]   # Optional because not required in every step
    )

    email = EmailField(
        "Email",
        validators=[Optional(), Email()]
    )

    # STEP 2
    otp = StringField(
        "Enter OTP",
        validators=[Optional()]
    )

    # STEP 3
    password = PasswordField(
        "Password",
        validators=[
            Optional(),
            Length(min=8, max=20, message="Password must be between 8 and 20 characters")
        ]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            Optional(),
            EqualTo('password', message="Passwords must match")
        ]
    )


    submit = SubmitField("Submit")

