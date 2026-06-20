from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, FileField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp ,Optional


class InstituteAddStudent(FlaskForm):

    student_name = StringField(
        "Student Name",
        validators=[DataRequired(), Length(max=100)]
    )

    regd_no = StringField(
        "Registration Number",
        validators=[DataRequired(), Length(max=50)]
    )

    aadhaar = StringField(
        "Aadhaar Number",
        validators=[
            DataRequired(),
            Length(min=12, max=12),
            Regexp("^[0-9]{12}$", message="Aadhaar must be 12 digits")
        ]
    )

    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=100)]
    )

    phone = StringField(
        "Phone Number",
        validators=[
            DataRequired(),
            Length(min=10, max=15),
            Regexp("^[0-9]+$", message="Only digits allowed")
        ]
    )

    
    address = StringField(
        "Address",
        validators=[DataRequired(), Length(max=200)]
    )

    gender = SelectField(
        "Gender",
        choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")],
        validators=[DataRequired()]
    )

    dob = DateField(
        "Date of Birth",
        format="%Y-%m-%d",
        validators=[DataRequired()]
    )
    blood_group = SelectField(
        "Blood Group",
        choices=[
            ("", "Select Blood Group"),
            ("A+", "A+"), ("A-", "A-"),
            ("B+", "B+"), ("B-", "B-"),
            ("O+", "O+"), ("O-", "O-"),
            ("AB+", "AB+"), ("AB-", "AB-")
        ],
        validators=[Optional()]
    )

    branch = SelectField(
        "Branch",
        choices=[("CSE", "CSE"), ("ECE", "ECE"), ("ME", "ME"), ("CE", "CE"), ("EE", "EE")],
        validators=[DataRequired()]
    )

    year = SelectField(
        "Year",
        choices=[("1", "1st Year"), ("2", "2nd Year"), ("3", "3rd Year"), ("4", "4th Year")],
        validators=[DataRequired()]
    )

    photo = FileField(
        "Student Photo",
        validators=[DataRequired()]
    )

    submit = SubmitField("Add Student")
