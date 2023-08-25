import requests
import pathlib
import google.auth.transport.requests
from pip._vendor import cachecontrol
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from datetime import datetime
from flask import Flask, redirect, render_template, request, flash, session, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import xlrd
import shutil
import os
import json

# The following are custom modules
import GetPreferenceWeb
import AutoSelection
import AddPlanDetails
import AutoRanking
import GetSeats
import GetSchedulePic


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///web.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'

db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    # password = db.Column(db.String(80), nullable=False)
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


# make sure this matches with that's in client_secret.json
app.secret_key = "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"
# to allow Http traffic for local dev
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = "697687543481-stsr0foi21nlt6abfc2cvls4266ofskv.apps.googleusercontent.com"
client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "client_secret.json")


def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        if response.status_code == 200:
            data = response.json()
            return data["ip"]
        else:
            print("Request failed with status code:", response.status_code)
            return None
    except Exception as e:
        print("Error:", e)
        return None


if (get_public_ip() == "158.101.17.48"):
    google_redirect_uri = "https://buplannerx.my.to/google_callback"
else:
    # google_redirect_uri="http://localhost:5000/google_callback"
    google_redirect_uri = "http://127.0.0.1:5000/google_callback"

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email", "openid"],

    # go https://console.cloud.google.com to set up redirect_uri
    redirect_uri=google_redirect_uri
)


@app.route("/google_login")
def google_login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/google_callback")
def google_callback():
    flow.fetch_token(authorization_response=request.url)

    # if not session["state"] == request.args["state"]:
    #     abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(
        session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    sub = id_info.get("sub")
    username = id_info.get("name")
    email = id_info.get("email")
    session["google_id"] = sub
    session["name"] = username

    if (User.query.filter_by(username=email).first()):
        user = User.query.filter_by(username=email).first()
        login_user(user)
    else:
        # hashed_password = bcrypt.generate_password_hash(form.password.data)
        # new_user = User(username=form.username.data, password=hashed_password)
        new_user = User(username=email)
        db.session.add(new_user)
        db.session.commit()
        userID = new_user.id
        path = "./Users/" + str(userID) + "/"
        GetPreferenceWeb.checkFolder(path)
        login_user(new_user)

    return redirect(url_for('dashboard'))


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def user_loader(id):
    return User.query.get(id)

# class RegisterForm(FlaskForm):
#     username = StringField(validators=[
#                            InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

#     password = PasswordField(validators=[
#                              InputRequired(), Length(min=6, max=20)], render_kw={"placeholder": "Password"})

#     submit = SubmitField('Register')

#     def validate_username(self, username):
#         existing_user_username = User.query.filter_by(
#             username=username.data).first()
#         if existing_user_username:
#             raise ValidationError(
#                 'That username already exists. Please choose a different one.')

# class LoginForm(FlaskForm):
#     username = StringField(validators=[
#                            InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

#     password = PasswordField(validators=[
#                              InputRequired(), Length(min=6, max=20)], render_kw={"placeholder": "Password"})

#     submit = SubmitField('Login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = []

    # form = LoginForm()
    # if request.method == 'POST':
    #     msg.append("Invalid login!")
    #     if form.validate_on_submit():
    #         user = User.query.filter_by(username=form.username.data).first()
    #         if user:
    #             if bcrypt.check_password_hash(user.password, form.password.data):
    #                 login_user(user)
    #                 return redirect(url_for('dashboard'))
    # return render_template('login.html', form=form, msg=msg)

    return render_template('login.html', msg=msg)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('index'))


# @ app.route('/register', methods=['GET', 'POST'])
# def register():
#     msg = []

#     form = RegisterForm()

#     if request.method == 'POST':
#         msg.append("Invalid registration!")
#         if form.validate_on_submit():
#             hashed_password = bcrypt.generate_password_hash(form.password.data)
#             new_user = User(username=form.username.data,
#                             password=hashed_password)
#             db.session.add(new_user)
#             db.session.commit()
#             userID = new_user.id
#             path = "./Users/" + str(userID) + "/"
#             GetPreferenceWeb.checkFolder(path)
#             return redirect(url_for('login'))

#     return render_template('register.html', form=form, msg=msg)

def allowAccess(user, other):
    if (hasattr(other, "user_id") and user.id != other.user_id):
        return False
    else:
        return True


@app.route('/')
def index():
    msg = ["WARNING:", "The current version of the website is for TEST ONLY!",
           "Any of your data might be DELETED at any time!", "Our team is not responsible for any loss of your data!"]
    return render_template('index.html', msg=msg)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user = User.query.get(current_user.get_id())
    plans = Plan.query.filter_by(user_id=user.id)
    return render_template('dashboard.html', user=user, plans=plans)


@app.route('/plan/fetch_course_names/<semester>', methods=['POST', 'GET'])
def fetch_course_names(semester):
    courses = GetPreferenceWeb.getAllCourseNames(semester.split("_")[0])
    name_list = []
    for course in courses:
        name_list.append(course["code"] + ": " + course["name"])
    print("Success!")
    return jsonify(name_list)


@app.route('/plan/fetch_term_names/<year>', methods=['POST', 'GET'])
def fetch_term_names(year):
    semesters = GetPreferenceWeb.getAllTermNames(year)
    print("Success!")
    return jsonify(semesters)

controls = [False, False]
@app.route('/plan/<int:planID>', methods=['POST', 'GET'])
@login_required
def plan(planID):
    global controls
    try:
        msg = session['messages']
    except:
        session['messages'] = []
        msg = session['messages']
    session['messages'] = []

    prefDict = {}
    user = User.query.get(current_user.get_id())
    plan = Plan.query.get(planID)

    classFullCodes = []
    try:
        courses = plan.courses
        classFullNames = courses.split("||")
        for name in classFullNames:
            classFullCodes.append(name.split(":")[0])
    except:
        classFullNames = []

    years = GetPreferenceWeb.getYears()
    years = sorted(years, reverse=True)

    if (allowAccess(user, plan)):
        if (request.method == 'POST'):
            try:
                classFullNames = request.form.getlist('courses')
                planname = request.form['planname']
                AvgScore = request.form['AvgScore']
                EarlyTime = request.form['EarlyTime']
                LateTime = request.form['LateTime']
                semester = request.form['years'] + '-' + request.form['term']
                if classFullNames == []:
                    msg.append("Missing Courses")
                if (planname == ""):
                    msg.append("Missing Plan Name")
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
                courses = ""
                classes = []
                for i in range(len(classFullNames)):
                    oneClass = classFullNames[i]
                    if (i == len(classFullNames)-1):
                        courses += oneClass
                    else:
                        courses += oneClass + "||"
                    classes.append(oneClass.split(":")[0].strip())
                print(courses)
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
                        plan.courses = courses
                        plan.AvgScore = float(AvgScore)
                        plan.EarlyTime = EarlyTime
                        plan.LateTime = LateTime
                        plan.planNum = -1
                        db.session.commit()
                    else:
                        new_plan = Plan(user_id=user.id, semester=semester, planname=planname, courses=courses, AvgScore=float(
                            AvgScore), EarlyTime=EarlyTime, LateTime=LateTime)
                        db.session.add(new_plan)
                        db.session.commit()
                        plan = new_plan
                    path = "./Users/"+str(user.id)+"/"+str(plan.id)+"/"
                    if (os.path.exists(path)):
                        shutil.rmtree(path)
                    GetPreferenceWeb.GetPreference(
                        str(user.id), str(plan.id), prefDict, semester)
                    msg.append("Your prefereces is saved!")
                    controls = [True, False]
                    print(controls)
                    session['messages'] = msg
                    return redirect("/plan/" + str(plan.id))
            except:
                if (msg == []):
                    msg.append("Something goes wrong.")
        else:
            pass
    else:
        return redirect(url_for('index'))

    guidance = {
        "planName": ["Plan Name", "Give a name for your course plan."],
        "AvgScore": ["Average Professor Score", "Enter a average RateMyProfessor score (0~5) of your professors. When you rank your plans, the plans with higher average score will be ranked higher."],
        "EarlyTime": ["Preferred Starting Time", "Enter a time you prefer to start your first class in a day. When you rank your plans, the plans with later starting time will be ranked higher."],
        "LateTime": ["Preferred Ending Time", "Enter a time you prefer to end your last class in a day. When you rank your plans, the plans with earlier finishing time will be ranked higher."],
        "courses": ["Courses", "Select courses you want to take. You can type the course code or the course name to search for the course. Multiple courses selection is available."],
        "semester": ["Semester", "Choose a school year and a term of the semester you want to take courses in."]
    }
    return render_template('plan.html', msg=msg, plan=plan, user=user, classFullCodes=classFullCodes, years=years, guidance=guidance, controls=controls)


@app.route('/deleteplan/<int:planID>', methods=['POST', 'GET'])
@login_required
def deletePlan(planID):
    user = User.query.get(current_user.get_id())
    plan = Plan.query.get(planID)
    if (allowAccess(user, plan)):
        try:
            path1 = "./Users/"+str(user.id)+"/"+str(plan.id)+"/"
            path2 = "./static/Users/"+str(user.id)+"/"+str(plan.id)+"/"
            db.session.delete(plan)
            db.session.commit()
            shutil.rmtree(path1)
            shutil.rmtree(path2)
        except:
            pass
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('index'))


@app.route('/deleteuser', methods=['POST', 'GET'])
@login_required
def deleteUser():
    user = User.query.get(current_user.get_id())
    plans = Plan.query.filter_by(user_id=user.id)
    # logout_user()
    session.clear()
    try:
        path1 = "./Users/"+str(user.id)+"/"
        path2 = "./static/Users/"+str(user.id)+"/"
        db.session.delete(user)
        for plan in plans:
            db.session.delete(plan)
        db.session.commit()
        shutil.rmtree(path1)
        shutil.rmtree(path2)
    except:
        pass
    return redirect(url_for('index'))


@app.route('/getplans/<int:planID>')
@login_required
def getPlans(planID):
    msg = []
    user = User.query.get(current_user.get_id())
    plan = Plan.query.get(planID)

    userID = str(user.id)
    planID = str(planID)
    semester = plan.semester
    result = AutoSelection.AutoSelection(semester, userID, planID)
    if (result == 0):
        msg.append("Can't find your plans")
    else:
        msg.append("Got your plans!")
        global controls
        controls = [True, True]

    session['messages'] = msg
    return redirect('/plan/' + planID)


@app.route('/rankplans/<int:planID>')
@login_required
def rankPlans(planID):
    msg = []
    user = User.query.get(current_user.get_id())
    plan = Plan.query.get(planID)

    userID = str(user.id)
    planID = str(planID)
    semester = plan.semester
    try:
        GetSeats.GetSeats(semester, userID, planID)
        msg.append("Seats are checked.")
        AddPlanDetails.AddPlanDetails(semester, userID, planID)
        msg.append("Plan details are added.")
        AutoRanking.AutoRanking(semester, userID, planID)
        msg.append("Your plans are ranked!")
    except:
        msg.append("Fail to rank your plans")

    showSchedule(planID, 1)
    session['messages'] = msg
    return redirect('/plan/' + planID)


@app.route('/plan/showschedule/<int:planID>/<string:n>', methods=['POST'])
@login_required
def showSchedule(planID, n):
    n = int(n)
    msg = []
    user = User.query.get(current_user.get_id())
    plan = Plan.query.get(planID)
    planID = str(planID)
    userID = str(user.id)
    semester = plan.semester
    if (n == -2 or n == -4):  # -2: previous plan; -4: next plan
        newNum = plan.planNum + (3+n)
    else:
        newNum = n-1
    try:
        if (newNum < 0):
            newNum = 0
        try:
            rankPath = "./Users/" + userID + "/" + planID + "/"
            rankName = semester + " Ranking"
            book = xlrd.open_workbook(rankPath + rankName + ".xls")
            sheet = book.sheet_by_name(rankName)
            maxNum = sheet.nrows
            if (newNum > maxNum):
                newNum = maxNum-1
            planName = sheet.cell_value(newNum, 0)
        except:
            planName = "Plan " + str(newNum+1)
        GetSchedulePic.GetSchedulePic(semester, userID, planID, planName)
        plan.planNum = newNum
        db.session.commit()
        print("Plan " + str(plan.planNum + 1))
        # msg.append("See your schedules below")
    except:
        msg.append("Can't create your schedules")
    session['messages'] = msg
    return jsonify(num=plan.planNum+1)


@app.teardown_request
def teardown_request(exception):
    if exception:
        db.session.rollback()
    db.session.remove()


if __name__ == "__main__":
    app.run(debug=True, port="5000")
