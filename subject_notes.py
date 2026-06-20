from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    StringField,
    TextAreaField,
    IntegerField,
    SubmitField
)
from wtforms.validators import DataRequired, Length, URL, NumberRange


class SubjectNotesForm(FlaskForm):

    year = SelectField(
        "Year",
        choices=[
            ("","Select Year"),
            ("1st Year", "1st Year"),
            ("2nd Year", "2nd Year"),
            ("3rd Year", "3rd Year"),
            ("4th Year", "4th Year")
        ],
        validators=[DataRequired()]
    )

    branch = SelectField(
        "Branch",
        choices=[
            ("","Select Branch"),
            ("CSE", "CSE"),
            ("ECE", "ECE"),
            ("MECH", "MECH"),
            ("CIVIL", "CIVIL"),
            ("EE", "EE")
        ],
        validators=[DataRequired()]
    )

    subject_name = StringField(
        "Subject Name",
        validators=[DataRequired(), Length(min=2, max=100)]
    )

    chapter_name = StringField(
        "Chapter Name",
        validators=[DataRequired(), Length(min=2, max=150)]
    )

    summary = TextAreaField(
        "Summary",
        validators=[DataRequired(), Length(min=5)]
    )

    notes_link = StringField(
        "Notes Link",
        validators=[DataRequired(), URL()]
    )

    submit = SubmitField("Add Subject Notes")