from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, URL

class FinalUpdateNoticeForm(FlaskForm):

    title = StringField('Title', validators=[DataRequired()])
    subject = StringField('Subject', validators=[Optional()])

    purpose = SelectField(
        'Purpose',
        choices=[
            ('Exam', 'Exam'),
            ('Holiday', 'Holiday'),
            ('Event', 'Event'),
            ('Meeting', 'Meeting'),
            ('Assignment', 'Assignment'),
            ('General', 'General Notice'),
            ('Other', 'Other')
        ],
        coerce=str
    )

    declared_by = SelectField(
        'Declared By',
        choices=[
            ('Principal', 'Principal'),
            ('HOD', 'HOD'),
            ('Exam Cell', 'Exam Cell'),
            ('Administration', 'Administration'),
            ('Faculty', 'Faculty'),
            ('Other', 'Other')
        ],
        coerce=str
    )

    department = SelectField(
        'Department',
        choices=[
            ('CSE', 'CSE'),
            ('ECE', 'ECE'),
            ('ME', 'ME'),
            ('CE', 'CE'),
            ('EE', 'EE')
        ],
        coerce=str
    )

    description = TextAreaField('Description', validators=[DataRequired()])
    drive_link = StringField('Drive Link', validators=[Optional(), URL()])

    submit = SubmitField("Update Notice")