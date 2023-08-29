from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, Email, EqualTo

from web_models import User

password_min = 6
password_max = 20
username_min = 1
username_max = 20

class RegisterForm(FlaskForm):
    username = StringField(validators=[
        InputRequired(), Length(min=username_min, max=username_max)], render_kw={"placeholder": "Username"})

    email = EmailField(validators=[
        InputRequired()], render_kw={"placeholder": "Email"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=password_min, max=password_max)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_email(self, email):
        existing_user_email = User.query.filter_by(
            email=email.data).first()
        if existing_user_email:
            print("Email already exists")
            raise ValidationError(
                'That email already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    email = EmailField(validators=[
        InputRequired()], render_kw={"placeholder": "Email"})

    password = PasswordField(validators=[
                             InputRequired()], render_kw={"placeholder": "Password"})

    remember = BooleanField('Remember Me')

    submit = SubmitField('Login')


class RequestResetForm(FlaskForm):
    email = EmailField('Email',
                       validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})

    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        existing_user_email = User.query.filter_by(email=email.data).first()
        if existing_user_email is None:
            print("Email does not exist")
            raise ValidationError(
                'There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=password_min, max=password_max)], render_kw={
                             "placeholder": "New Password"})

    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password'), Length(min=password_min, max=password_max)], render_kw={"placeholder": "Confirm Password"})

    submit = SubmitField('Reset Password')


class RequestVerificationForm(FlaskForm):
    email = EmailField('Email',
                       validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})

    submit = SubmitField('Verify Email')

    def validate_email(self, email):
        existing_user_email = User.query.filter_by(email=email.data).first()
        if existing_user_email is None:
            print("Email does not exist")
            raise ValidationError(
                'There is no account with that email. You must register first.')
