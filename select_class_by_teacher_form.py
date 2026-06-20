# forms.py
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

class SelectClassForm(FlaskForm):
    year = SelectField(
        "Select Year", 
        choices=[('','Select Year'),('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')],
        validators=[DataRequired()]
    )
    
    branch = SelectField(
        "Select Branch", 
        choices=[('','Select Branch'),('CSE', 'CSE'), ('ECE', 'ECE'),('ME', 'ME'),('CE','CE'),('EE','EE')],
        validators=[DataRequired()]
    )
    
    submit = SubmitField("Show Subjects")