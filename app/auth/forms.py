from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('使用者名稱', validators=[DataRequired()])
    password = PasswordField('密碼', validators=[DataRequired()])
    remember_me = BooleanField('記住我')
    submit = SubmitField('登入')

class RegistrationForm(FlaskForm):
    username = StringField('使用者名稱', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('電子信箱', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('密碼', validators=[DataRequired()])
    confirm_password = PasswordField('確認密碼', validators=[DataRequired(), EqualTo('password', message='密碼必須相符')])
    submit = SubmitField('註冊')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('此使用者名稱已被使用。')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('此電子信箱已被註冊。')
