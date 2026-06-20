from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, URL

class InstituteAddNotice(FlaskForm):
    notice_number = StringField('Notice Number', validators=[
        DataRequired(), Length(max=50)
    ])

    title = StringField('Title', validators=[
        DataRequired(), Length(max=255)
    ])

    subject = StringField('Subject', validators=[
        Optional(), Length(max=255)
    ])

    purpose = SelectField('Purpose', choices=[
        ('', 'Select Purpose'),
        ('Exam', 'Exam'),
        ('Holiday', 'Holiday'),
        ('Event', 'Event'),
        ('Meeting', 'Meeting'),
        ('Assignment', 'Assignment'),
        ('General', 'General Notice'),
        ('Other','Other')
    ], validators=[Optional()])

    description = TextAreaField('Description', validators=[
        DataRequired()
    ])

    drive_link = StringField('Drive Link', validators=[
        Optional(), URL()
    ])

    declared_by = SelectField('Declared By', choices=[
        ('', 'Select Authority'),
        ('Principal', 'Principal'),
        ('HOD', 'HOD'),
        ('Exam Cell', 'Exam Cell'),
        ('Administration', 'Administration'),
        ('Faculty', 'Faculty'),
        ('Other','Other')
    ], validators=[Optional()])

    department = SelectField('Department', choices=[
        ('CSE', 'CSE'),
        ('ECE', 'ECE'),
        ('ME', 'ME'),
        ('CE', 'CE'),
        ('EE', 'EE')
    ])

    is_active = BooleanField('Active', default=True)

    submit = SubmitField('Create Notice')