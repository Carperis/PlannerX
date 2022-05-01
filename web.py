from datetime import datetime
from email.policy import default
from flask import Flask, redirect, render_template, request, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy

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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///web.db'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
db = SQLAlchemy(app)


class PlannerX(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    courses = db.Column(db.String(100), nullable=False)
    AvgScore = db.Column(db.Float)
    EarlyTime = db.Column(db.String(20), nullable=False)
    LateTime = db.Column(db.String(20), nullable=False)
    planNum = db.Column(db.Integer, default=-1)

    def __repr__(self):
        return '<Task %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    try:
        msg = session['messages']
    except:
        session['messages'] = []
        msg = session['messages']
    session.clear()
    prefDict = {}

    if (request.method == 'POST'):
        try:
            courses = (request.form['courses']).strip()
            username = request.form['username']
            AvgScore = request.form['AvgScore']
            EarlyTime = request.form['EarlyTime']
            LateTime = request.form['LateTime']
            semester = request.form['years'] + '-' + request.form['term']
            if (username == ""):
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
            result = GetPreferenceWeb.GetPreference(
                username, prefDict, semester)
            if (result == False):
                msg.append("Invalid course input.")
            if (float(AvgScore) < 0):
                msg.append("Average score cannot be negative values.")
            if (msg == []):
                msg.append("Your prefereces is saved!")
                if (PlannerX.query.get(1)):
                    user = PlannerX.query.get(1)
                    user.semester = semester
                    user.username = username
                    user.courses = courses
                    user.AvgScore = float(AvgScore)
                    user.EarlyTime = EarlyTime
                    user.LateTime = LateTime
                    user.planNum = -1
                    db.session.commit()
                else:
                    db.session.add(PlannerX(id=1, semester=semester, username=username, courses=courses, AvgScore=float(
                        AvgScore), EarlyTime=EarlyTime, LateTime=LateTime))
                    db.session.commit()
        except:
            if (msg == []):
                msg.append("Something goes wrong.")
    else:
        pass
    users = PlannerX.query.all()
    return render_template('index.html', msg=msg, users=users)


@app.route('/getplans/<int:id>')
def getPlans(id):
    msg = []
    user = PlannerX.query.get(id)
    s = user.semester
    u = user.username
    result = AutoSelection.AutoSelection(s, u)
    if(result == 0):
        msg.append("Can't find your plans")
    else:
        msg.append("Got your plans!")

    session['messages'] = msg
    return redirect('/')


@app.route('/rankplans/<int:id>')
def rankPlans(id):
    msg = []
    user = PlannerX.query.get(id)
    s = user.semester
    u = user.username
    try:
        GetSeats.GetSeats(s, u)
        msg.append("Seats are checked.")
        AddPlanDetails.AddPlanDetails(s, u)
        msg.append("Plan details are added.")
        AutoRanking.AutoRanking(s, u)
        msg.append("Your plans are ranked!")
    except:
        msg.append("Fail to rank your plans")

    session['messages'] = msg
    return redirect('/')


@app.route('/shownext/<int:id>')
def showNext(id):
    msg = []
    try:
        user = PlannerX.query.get(id)
        temp = user.planNum
        user.planNum = user.planNum + 1
        db.session.commit()
        s = user.semester
        u = user.username
        num = user.planNum
        try:
            rankPath = "./User/" + u + "/"
            rankName = s + " " + u + " Ranking"
            book = xlrd.open_workbook(rankPath + rankName + ".xls")
            sheet = book.sheet_by_name(rankName)
            planName = sheet.cell_value(num, 0)
        except:
            planName = "Plan " + str(num+1)
        print(planName)
        try:
            GetSchedulePic.GetSchedulePic(s, u, planName)
        except:
            user.planNum = temp
            db.session.commit()
        # msg.append("See your schedules below")
    except:
        msg.append("Can't create your schedules")

    session['messages'] = msg
    return redirect('/')


@app.route('/showprevious/<int:id>')
def showPrevious(id):
    msg = []
    try:
        user = PlannerX.query.get(id)
        temp = user.planNum
        user.planNum = user.planNum - 1
        db.session.commit()
        s = user.semester
        u = user.username
        num = user.planNum
        try:
            rankPath = "./User/" + u + "/"
            rankName = s + " " + u + " Ranking"
            book = xlrd.open_workbook(rankPath + rankName + ".xls")
            sheet = book.sheet_by_name(rankName)
            planName = sheet.cell_value(num, 0)
        except:
            planName = "Plan " + str(num+1)
        print(planName)
        try:
            GetSchedulePic.GetSchedulePic(s, u, planName)
        except:
            user.planNum = temp
            db.session.commit()
        # msg.append("See your schedules below")
    except:
        msg.append("Can't create your schedules")

    session['messages'] = msg
    return redirect('/')


@app.route('/goto', methods=['POST'])
def goto():
    msg = []
    try:
        num = int(request.form['num'])
        num = num - 1
        user = PlannerX.query.get(1)
        temp = user.planNum
        user.planNum = num
        db.session.commit()
        s = user.semester
        u = user.username
        try:
            rankPath = "./User/" + u + "/"
            rankName = s + " " + u + " Ranking"
            book = xlrd.open_workbook(rankPath + rankName + ".xls")
            sheet = book.sheet_by_name(rankName)
            planName = sheet.cell_value(num, 0)
        except:
            planName = "Plan " + str(num+1)
        try:
            GetSchedulePic.GetSchedulePic(s, u, planName)
        except:
            user.planNum = temp
            db.session.commit()
    except:
        msg.append("Can't create your schedules")
    session['messages'] = msg
    return redirect('/')


@app.route('/delete/<int:id>')
def delete(id):
    msg = []
    try:
        # users = PlannerX.query.all()
        # for user in users:
        #     db.session.delete(user)
        #     db.session.commit()
        user = PlannerX.query.get_or_404(id)
        username = user.username
        path = "./User/"+username+"/"
        db.session.delete(user)
        db.session.commit()
        shutil.rmtree(path)
        os.remove("./static/schedule.pdf")
        os.remove("./static/schedule.png")
        msg.append("Successfully delete your records")
    except:
        msg.append("Fail to delete your records!")
    session['messages'] = msg
    return redirect('/')


if __name__ == "__main__":
    # from web import db
    # db.create_all()
    app.run(debug=True, port="1234")
