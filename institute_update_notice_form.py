from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Optional, Length

class UpdateNoticeSearchForm(FlaskForm):

    notice_number = StringField(
        'Notice Number',
        validators=[
            Optional(),
            Length(max=50)
        ],
        render_kw={"placeholder": "Enter Notice Number (e.g. KMBB/2026/001)"}
    )

    submit = SubmitField('Search')