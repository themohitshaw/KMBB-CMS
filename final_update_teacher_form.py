from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    DateField,
    SelectField,
    IntegerField,
    DecimalField,
    SubmitField,
    FileField
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    Optional,
    NumberRange,
    Regexp
)
from flask_wtf.file import FileField, FileAllowed


class FinalUpdateTeacher(FlaskForm):


    regd_no = StringField(
        "Registration Number",
        validators=[
            DataRequired(),
            Length(max=20)
        ]
    )

    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    aadhaar = StringField(
        "Aadhaar Number",
        validators=[
            DataRequired(),
            Regexp(r'^\d{12}$', message="Aadhaar must be exactly 12 digits")
        ]
    )

    gender = SelectField(
        "Gender",
        choices=[
            ("Male", "Male"),
            ("Female", "Female"),
            ("Other", "Other")
        ],
        validators=[DataRequired()]
    )

    date_of_birth = DateField(
        "Date of Birth",
        format="%Y-%m-%d",
        validators=[DataRequired()]
    )

    address = StringField(
        "Address",
        validators=[
            DataRequired(),
            Length(max=200)
        ]
    )

    blood_group = SelectField(
        "Blood Group",
        choices=[
            ("A+", "A+"), ("A-", "A-"),
            ("B+", "B+"), ("B-", "B-"),
            ("O+", "O+"), ("O-", "O-"),
            ("AB+", "AB+"), ("AB-", "AB-")
        ],
        validators=[Optional()]
    )

    phone = StringField(
        "Phone Number",
        validators=[
            DataRequired(),
            Length(max=15)
        ]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
            Length(max=100)
        ]
    )


    designation = SelectField(
    "Designation",
        choices=[
            ("", "Select Designation"),
            ("Assistant Professor", "Assistant Professor"),
            ("Associate Professor", "Associate Professor"),
            ("Professor", "Professor"),
            ("Head of Department", "Head of Department"),
            ("Principal", "Principal"),
            ("Lab Instructor", "Lab Instructor"),
            ("Lecturer", "Lecturer"),
            ("Visiting Faculty", "Visiting Faculty"),
            ("Other", "Other")
        ],
    validators=[Optional()]
    )


    qualification = SelectField(
    "Qualification",
        choices=[
            ("", "Select Qualification"),
            ("B.Tech", "B.Tech"),
            ("M.Tech", "M.Tech"),
            ("B.Sc", "B.Sc"),
            ("M.Sc", "M.Sc"),
            ("PhD", "PhD"),
            ("MBA", "MBA"),
            ("B.Ed", "B.Ed"),
            ("M.Ed", "M.Ed"),
            ("Other", "Other")
        ],
    validators=[DataRequired()]
    )
    department = SelectField(
    "Department",
        choices=[
            ("", "Select Department"),
            ("CSE", "CSE"),
            ("CE", "CE"),
            ("ME", "ME"),
            ("ECE", "ECE"),
            ("EE", "EE"),
            ("Other", "Other")
        ],
    validators=[DataRequired()]
    )

    experience_years = IntegerField(
        "Experience (Years)",
        validators=[
            Optional(),
            NumberRange(min=0, message="Experience cannot be negative")
        ]
    )

    date_of_joining = DateField(
        "Date of Joining",
        format="%Y-%m-%d",
        validators=[DataRequired()]
    )

    photo = FileField("Update Photo",
                      validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])

    salary = DecimalField(
        "Salary",
        places=2,
        validators=[
            DataRequired(),
            NumberRange(min=0, message="Salary cannot be negative")
        ]
    )

    submit = SubmitField("Submit")
