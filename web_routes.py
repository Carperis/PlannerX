import pathlib
from flask import redirect, render_template, request, session, url_for, jsonify, abort, flash
from flask_login import login_user, login_required, logout_user, current_user
import shutil
import os
import json

from web_init import app, db, bcrypt, oauth
from web_models import User, Plan
from web_forms import LoginForm, RegisterForm, RequestResetForm, ResetPasswordForm, RequestVerificationForm
import web_api as wapi
client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "client_secret.json")
client_secrer_json = json.loads(open(client_secrets_file, "r").read())
oauth.register(
    name='google',
    client_id=client_secrer_json['web']['client_id'],
    client_secret=client_secrer_json['web']['client_secret'],
    # access_token_url='https://accounts.google.com/o/oauth2/token',
    # access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params={'access_type': 'offline', 'prompt': 'consent'}, # this is required to get a refresh token
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration"
)


@app.teardown_request
def teardown_request(exception):
    if exception:
        db.session.rollback()
    db.session.remove()


@app.route("/google_login")
def google_login():
    redirect_uri = wapi.get_google_redirect_uri()
    return oauth.google.authorize_redirect(redirect_uri=redirect_uri)


@app.route("/google_callback")
def google_callback():
    token = oauth.google.authorize_access_token()
    session["user"] = token

    sub = token["userinfo"]["sub"]
    username = token["userinfo"]["name"]
    email = token["userinfo"]["email"]
    session["google_id"] = sub
    session["name"] = username

    if (User.query.filter_by(email=email).first()):
        user = User.query.filter_by(email=email).first()
        if (user.google):
            if (user.verify):
                userID = user.id
                path = "./Users/" + str(userID) + "/"
                wapi.checkFolder(path)
                print(f"{user.email} Google login success!")
                login_user(user, remember=True)
                return redirect(url_for('dashboard'))
            else:
                return redirect(f'/email_verification?email={email}')
        else:
            warning = "Please login with your email and password."
            return redirect(f'/login?warning={warning}')
    else:
        if email.split("@")[1] != "bu.edu":
            warning = "Please login with your BU email."
            return redirect(f'/login?warning={warning}')
        hashed_password = bcrypt.generate_password_hash(email)  # not secure
        new_user = User(username=username, email=email,
                        password=hashed_password, google=True, verify=False)
        db.session.add(new_user)
        db.session.commit()
        return redirect(f'/email_verification?email={email}')


@ app.route('/register', methods=['GET', 'POST'])
def register():
    msg = []

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegisterForm()
    if request.method == 'POST':
        msg.append("Invalid registration!")
        if form.validate_on_submit():
            if form.email.data.split("@")[1] != "bu.edu":
                warning = "Please login with your BU email."
                return redirect(f'/login?warning={warning}')
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, email=form.email.data,
                            password=hashed_password, google=False)
            db.session.add(new_user)
            db.session.commit()
            return redirect(f'/email_verification?email={form.email.data}')
        else:
            msg.append(
                "That email may already exist. Please choose a different one.")

    return render_template('register.html', form=form, msg=msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    warning = request.args.get('warning')
    if (warning):
        msg = [warning]
    else:
        msg = []

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if request.method == 'POST':
        msg.append("Invalid email or password!")
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                if (user.google):
                    msg = []
                    msg.append("Please login with your Google account.")
                elif (user.verify):
                    if bcrypt.check_password_hash(user.password, form.password.data):
                        userID = user.id
                        path = "./Users/" + str(userID) + "/"
                        wapi.checkFolder(path)
                        print(f"{user.email} Login success!")
                        login_user(user, remember=form.remember.data)
                        return redirect(url_for('dashboard'))
                else:
                    email = user.email
                    return redirect(f'/email_verification?email={email}')
    return render_template('login.html', form=form, msg=msg)

    # return render_template('login.html', msg=msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_password_request():
    warning = request.args.get('warning')
    if (warning):
        msg = [warning]
    else:
        msg = []

    # if current_user.is_authenticated:
    #     return redirect(url_for('dashboard'))
    form = RequestResetForm()
    if request.method == 'POST':
        msg.append(
            "There is no account with that email. You must register first.")
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                if user.google:
                    warning = "Please login with your Google account."
                    return redirect(f'/login?warning={warning}')
                print(f"{user.email} Reset password requested!")
                wapi.send_reset_email(user)
                msg = []
                msg.append(
                    "An email has been sent with instructions to reset your password.")
                # warning = "An email has been sent with instructions to reset your password."
                # return redirect(f'/login?warning={warning}')
    return render_template('reset_password_request.html', form=form, msg=msg)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password_token(token):
    msg = []

    if current_user.is_authenticated:
        msg.append("Update your password below and then re-login")
        session.clear()
        logout_user()
        # return redirect(url_for('dashboard'))
    user = User.verify_token(token)
    if user is None:
        warning = "That is an invalid or expired token."
        return redirect(f'/reset_password?warning={warning}')
    form = ResetPasswordForm()
    if request.method == 'POST':
        msg.append("Two passwords are not the same!")
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(
                form.password.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            print(f"{user.email} Reset password success!")
            warning = "Your password has been updated! You are now able to login."
            return redirect(f'/login?warning={warning}')
    return render_template('reset_password_token.html', form=form, msg=msg)


@app.route("/email_verification", methods=['GET', 'POST'])
def email_verification_request():
    email = request.args.get('email')
    warning = request.args.get('warning')
    if (warning):
        msg = [warning]
    else:
        msg = []

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RequestVerificationForm()
    if request.method == 'POST':
        msg.append(
            "There is no account with that email. You must register first.")
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                if user.verify:
                    warning = "Your email has been verified. Please login with your email and password."
                    return redirect(f'/login?warning={warning}')
                print(f"{user.email} Email verification requested!")
                wapi.send_verification_email(user)
                msg = []
                msg.append(
                    "An email has been sent with instructions to verify your email.")
                # warning = "An email has been sent with instructions to verify your email."
                # return redirect(f'/login?warning={warning}')
    return render_template('email_verification_request.html', form=form, msg=msg, email=email)


@app.route("/email_verification/<token>", methods=['GET', 'POST'])
def email_verification_token(token):
    msg = []

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    user = User.verify_token(token)
    if user is None:
        warning = "That is an invalid or expired token."
        return redirect(f'/email_verification?warning={warning}&email={""}')
    user.verify = True
    email = user.email
    db.session.commit()
    print(f"{user.email} Email verification success!")
    return render_template('email_verification_token.html', msg=msg, email=email)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('index'))


@app.route('/')
def index():
    msg = ["Our database is NOW updated to Spring 2024. Let's plan it out!",]
    return render_template('index.html', msg=msg)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user = User.query.get(current_user.get_id())
    plans = Plan.query.filter_by(user_id=user.id)
    return render_template('dashboard.html', user=user, plans=plans)


@app.route('/plan/fetch_course_names/<semester>')
def fetch_course_names(semester):
    courses = wapi.getAllCourseNames(semester.split("_")[0])
    name_list = []
    for course in courses:
        shortcode = course["code"].replace(" ", "")
        name_list.append(course["code"] + ": " + course["name"] + " (" + shortcode + ")")
    # print("fetch course names success!")
    return jsonify(name_list)


@app.route('/plan/fetch_term_names/<year>')
def fetch_term_names(year):
    semesters = wapi.getAllTermNames(year)
    # print("fetch term names success!")
    return jsonify(semesters)


@app.route('/plan/<int:planID>', methods=['POST', 'GET'])
@login_required
def plan(planID):
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

    years = wapi.getYears()
    years = sorted(years, reverse=True)

    controls = [False, False, False]
    editDate = {}

    if (wapi.allow_access(user, plan)):
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
                # print(courses)
                prefDict["Courses"] = classes
                prefDict["Average Score"] = [float(AvgScore)]
                prefDict["Earliest Time"] = [EarlyT]
                prefDict["Latest Time"] = [LateT]
                rightCourses = wapi.checkCourses(
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
                    wapi.getPreference(
                        str(user.id), str(plan.id), prefDict, semester)
                    msg.append("Your prefereces is saved!")

                    session['messages'] = msg
                    return redirect("/plan/" + str(plan.id))
            except Exception as e:
                if (msg == []):
                    print("Error in submittion: " + str(e))
                    msg.append("Error in submittion: " + str(e))
        else:
            pass
        if (plan):
            check1 = wapi.checkSubmitSuccess(
                user.id, plan.id, plan.semester)
            check2 = wapi.checkPlanSuccess(
                user.id, plan.id, plan.semester)
            check3 = wapi.checkRankSuccess(
                user.id, plan.id, plan.semester)
            controls = [check1, check2, check3]
            editDate = wapi.getEditDate(
                user.id, plan.id, plan.semester)

    else:
        return redirect(url_for('index'))

    guidance = {
        "planname": ["Plan Name", "Give a name for your course plan."],
        "AvgScore": ["Average Professor Score", "Enter a average RateMyProfessor score (0~5) of your professors. When you rank your plans, the plans with higher average score will be ranked higher."],
        "EarlyTime": ["Preferred Starting Time", "Enter a time you prefer to start your first class in a day. When you rank your plans, the plans with later starting time will be ranked higher."],
        "LateTime": ["Preferred Ending Time", "Enter a time you prefer to end your last class in a day. When you rank your plans, the plans with earlier finishing time will be ranked higher."],
        "courses": ["Courses", "Select courses you want to take. You can type the course code or the course name to search for the course. Multiple courses selection is available."],
        "semester": ["Semester", "Choose a school year and a term of the semester you want to take courses in."],
        "getschedules": ["Get Schedules", "Click this button to get your schedules. You can get your schedules only after you submit your preferences. The schedules below are shown in default order."],
        "rankschedules": ["Rank Schedules", "Click this button to rank your schedules. You can rank your schedules only after you get your schedules. The schedules below are shown in ranked order. The first one should be your best schedule."],
        "deleteplan": ["Delete Plan", "Click this button to delete this plan. WARNING: This action cannot be undone!"]
    }

    quickTips = {
        "Don't know what you should enter in boxes?": "Click the question mark (?) beside each input box to learn more. ",
        "No schedule is available?": "There might be some inevitable time conflicts in your courses. If you believe it is not a course problem, it may because of the special structure of your courses (e.g. ENG EK 100). Our current algorithm can't process them correctly.  TO SOLVE IT, please try to drop some courses from your preferences and submit again.",
        "Can't find your courses?": "Please check if you have chosen the correct semester and entered the correct course code or course name. If you still can't find it, please contact us so that we can update our database."
    }

    return render_template('plan.html', msg=msg, plan=plan, user=user, classFullCodes=classFullCodes, years=years, guidance=guidance, controls=controls, editDate=editDate, quickTips=quickTips)


@app.route('/deleteplan/<int:planID>')
@login_required
def deletePlan(planID):
    user = User.query.get(current_user.get_id())
    plan = Plan.query.get(planID)
    if (wapi.allow_access(user, plan)):
        try:
            db.session.delete(plan)
            db.session.commit()
            wapi.delete_user_files(planID)
        except:
            pass
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('index'))


@app.route('/deleteuser')
@login_required
def deleteUser():
    user = User.query.get(current_user.get_id())
    session.clear()
    logout_user()
    plans = Plan.query.filter_by(user_id=user.id)
    try:
        userID = user.id
        db.session.delete(user)
        for plan in plans:
            db.session.delete(plan)
        db.session.commit()
        wapi.delete_user_files(userID)
    except Exception as e:
        print("Error in deleting user: " + str(e))
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

    xlsNames = ["InfoDetails", "Ranking", "Seats"]
    for name in xlsNames:
        path = "./Users/" + userID + "/" + planID + "/" + semester + " " + name + ".xls"
        if (os.path.exists(path)):
            os.remove(path)

    result = wapi.get_all_schedules(semester, userID, planID)
    if (result == 0):
        msg.append("Sorry, no schedule is available. There might be some inevitable time conflicts in your courses. Please try to change your preferences and submit again.")
    else:
        msg.append("Got your schedules! You can see them below.")

    showSchedule(planID, 1)
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
        msg += wapi.rank_all_schedules(semester,
                                       userID, planID, ignoreSeats=True)
    except Exception as e:
        print("Error in ranking plans: " + str(e))
        msg.append("Error in ranking plans: " + str(e))

    showSchedule(planID, 1)
    session['messages'] = msg
    return redirect('/plan/' + planID)


@app.route('/plan/showschedule/<int:planID>/<string:n>')
@login_required
def showSchedule(planID, n):
    n = int(n)
    msg = []
    details = {}
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
            result = wapi.get_ranked_plan_name(
                semester, userID, planID, newNum)
            planName = result[0]
            newNum = result[1]
        except:
            planName = "Plan " + str(newNum+1)

        validSche = wapi.create_schedule_pic(
            semester, userID, planID, planName)
        if (not validSche):
            return jsonify(num=plan.planNum+1, details=details)

        details = wapi.getScheduleDetails(
            userID, planID, semester, planName)
        plan.planNum = newNum
        db.session.commit()
        # print("Showing Plan " + str(plan.planNum + 1))
        # msg.append("See your schedules below")
    except Exception as e:
        print("Error in showing schedules: " + str(e))
        msg.append("Error in showing schedules: " + str(e))
    session['messages'] = msg
    return jsonify(num=plan.planNum+1, details=details)
