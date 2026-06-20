from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import Optional

class InstituteViewStudent(FlaskForm):

    year = SelectField(
        "Search by Year",
        choices=[
            ("", "-- Select Year --"),
            ("1", "1st Year"),
            ("2", "2nd Year"),
            ("3", "3rd Year"),
            ("4", "4th Year")
        ],
        validators=[Optional()]
    )

    branch = SelectField(
        "Search by Branch",
        choices=[
            ("", "-- Select Branch --"),
            ("CSE", "CSE"),
            ("ECE", "ECE"),
            ("ME", "ME"),
            ("CE", "CE"),
            ("EE", "EE")
        ],
        validators=[Optional()]
    )

    regd_no = StringField("Search by Registration No", validators=[Optional()])
    name = StringField("Search by Student Name", validators=[Optional()])

    submit = SubmitField("Search")
