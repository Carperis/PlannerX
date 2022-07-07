from datetime import datetime
from email.policy import default
from click import style
from flask import Flask, redirect, render_template, request, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

import GetPreferenceWeb
import AutoSelection
import AddPlanDetails
import AutoRanking
import GetSeats
import GetSchedulePic
import xlrd
import shutil
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///web.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    # def __repr__(self):
    #     return '<User %r>' % self.id


class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    planname = db.Column(db.String(20), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    courses = db.Column(db.String(100), nullable=False)
    AvgScore = db.Column(db.Float)
    EarlyTime = db.Column(db.String(20), nullable=False)
    LateTime = db.Column(db.String(20), nullable=False)
    planNum = db.Column(db.Integer, default=-1)
    # def __repr__(self):
    #     return '<Plan %r>' % self.id


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


def allowAccess(user, other):
    if(hasattr(other, "user_id") and user.id != other.user_id):
        return False
    else:
        return True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = []

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    # else:
    #     msg.append("Invalid login!")
    return render_template('login.html', form=form, msg=msg)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    msg = []

    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        userID = new_user.id
        path = "./Users/" + str(userID) + "/"
        GetPreferenceWeb.checkFolder(path)
        return redirect(url_for('login'))
    # else:
    #     msg.append("Invalid registration!")
    return render_template('register.html', form=form, msg=msg)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user = User.query.get(current_user.get_id())
    plans = Plan.query.filter_by(user_id=user.id)
    return render_template('dashboard.html', user=user, plans=plans)


@app.route('/plan/<int:planID>', methods=['POST', 'GET'])
@login_required
def plan(planID):
    msg = []
    prefDict = {}
    user = User.query.get(current_user.get_id())
    plan = Plan.query.get(planID)
    if (allowAccess(user, plan)):
        if (request.method == 'POST'):
            try:
                courses = (request.form['courses']).strip()
                planname = request.form['planname']
                AvgScore = request.form['AvgScore']
                EarlyTime = request.form['EarlyTime']
                LateTime = request.form['LateTime']
                semester = request.form['years'] + '-' + request.form['term']
                if (planname == ""):
                    msg.append("Missing Username")
                if (AvgScore == ""):
                    msg.append("Missing Average Professor Score")
                if (EarlyTime == ""):
                    msg.append("Missing Starting Time")
                if (LateTime == ""):
                    msg.append("Missing Finishing Time")
                EarlyT = float(str(EarlyTime).split(
                    ":")[0])+(float(str(EarlyTime).split(":")[1]))/60
                LateT = float(str(LateTime).split(
                    ":")[0])+(float(str(LateTime).split(":")[1]))/60
                classes = str(courses).split(",")
                for i in range(len(classes)):
                    classes[i] = classes[i].strip()
                prefDict["Courses"] = classes
                prefDict["Average Score"] = [float(AvgScore)]
                prefDict["Earliest Time"] = [EarlyT]
                prefDict["Latest Time"] = [LateT]
                rightCourses = GetPreferenceWeb.checkCourses(
                    prefDict["Courses"], semester.split("_")[0])
                if (not rightCourses):
                    msg.append("Invalid course input.")
                if (float(AvgScore) < 0):
                    msg.append("Average score cannot be negative values.")
                if (msg == []):
                    if (plan):
                        plan.semester = semester
                        plan.planname = planname
                        user.courses = courses
                        plan.AvgScore = float(AvgScore)
                        plan.EarlyTime = EarlyTime
                        plan.LateTime = LateTime
                        plan.planNum = -1
                        db.session.commit()
                        GetPreferenceWeb.GetPreference(
                            str(user.id), str(plan.id), prefDict, semester)
                    else:
                        new_plan = Plan(user_id=user.id, semester=semester, planname=planname, courses=courses, AvgScore=float(
                            AvgScore), EarlyTime=EarlyTime, LateTime=LateTime)
                        db.session.add(new_plan)
                        db.session.commit()
                        plan = new_plan
                        GetPreferenceWeb.GetPreference(
                            str(user.id), str(new_plan.id), prefDict, semester)
                    msg.append("Your prefereces is saved!")
            except:
                if (msg == []):
                    msg.append("Something goes wrong.")
        else:
            pass
    else:
        return redirect(url_for('index'))

    return render_template('plan.html', msg=msg, plan=plan, user=user)


if __name__ == "__main__":
    # from web2 import db
    # db.create_all()
    app.run(debug=True, port="1234")
    # app.run(debug=True, port="5000", host="0.0.0.0")
