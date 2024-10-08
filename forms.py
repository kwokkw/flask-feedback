from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField
from wtforms.validators import InputRequired

class UserForm(FlaskForm):

    username = StringField("Username", validators=[InputRequired()]) 
    password = PasswordField("Password", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired()])
    first_name = StringField("First Name", validators=[InputRequired()]) 
    last_name = StringField("Last Name", validators=[InputRequired()]) 


class LoginForm(FlaskForm):

    username = StringField("Username", validators=[InputRequired()]) 
    password = PasswordField("Password", validators=[InputRequired()])


class FeedbackForm(FlaskForm):

    title = StringField("Feedback Title", validators=[InputRequired()])
    content = StringField("Feedback Text", validators=[InputRequired()])

class ResetPasswordRequestForm(FlaskForm):

    email = EmailField("Email", validators=[InputRequired()])

class ResetPasswordForm(FlaskForm):

    password = PasswordField("New Password", validators=[InputRequired()])