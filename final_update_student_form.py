from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SelectField, DateField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed

class FinalUpdateStudent(FlaskForm):

    name = StringField("Name", validators=[DataRequired()])
    aadhaar = StringField("Aadhaar", validators=[DataRequired(), Length(min=12, max=12)])
    email = EmailField("Email", validators=[DataRequired()])
    phone = StringField("Phone", validators=[DataRequired(), Length(min=10, max=10)])

    gender = SelectField(
        "Gender",
        choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")],
        validators=[DataRequired()]
    )

    dob = DateField("Date of Birth", format='%Y-%m-%d', validators=[DataRequired()])
    branch = StringField("Branch", validators=[DataRequired()])
    year = IntegerField("Year", validators=[DataRequired()])

    photo = FileField("Update Photo",
                      validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])

    submit = SubmitField("Update Student")
