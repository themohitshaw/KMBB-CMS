from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class DeleteNoticeSearchForm(FlaskForm):
    notice_number = StringField("Notice Number", validators=[DataRequired()])
    submit = SubmitField("Search")


class ConfirmDeleteForm(FlaskForm):
    confirm = SubmitField("Delete")