from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Optional

class InstituteDeleteStudent(FlaskForm):
    regd_no = StringField("Search by Registration Number", validators=[Optional()])
    name = StringField("Search by Name", validators=[Optional()])
    submit = SubmitField("Search")


