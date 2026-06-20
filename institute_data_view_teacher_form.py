from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Optional

class InstituteViewTeacher(FlaskForm):

    regd_no = StringField(
        "Search by Registration No",
        validators=[Optional()]
    )

    name = StringField(
        "Search by Faculty Name",
        validators=[Optional()]
    )

    submit = SubmitField("Search")
    search_all = SubmitField("Search All")