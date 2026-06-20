from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired


class FinalDeleteTeacher(FlaskForm):

    delete = SubmitField("Delete")
    cancel = SubmitField("Cancel")