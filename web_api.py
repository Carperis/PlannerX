import requests
from flask_mail import Message
from flask import url_for
from web_init import mail, app
import os
import xlwt
import xlrd
from datetime import datetime
import shutil
from threading import Thread

# The following are custom modules
import AutoSelection
import AddPlanDetails
import AutoRanking
import GetSeats
import GetSchedulePic


def allow_access(user, other):
    if (hasattr(other, "user_id") and user.id != other.user_id):
        return False
    else:
        return True


def get_google_redirect_uri():
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
    # go https://console.cloud.google.com to set up redirect_uri
    if (get_public_ip() == "158.101.17.48"):
        # google_redirect_uri = "https://buplannerx.my.to/google_callback"
        google_redirect_uri = "https://www.plannerx.app/google_callback"
    else:
        # google_redirect_uri="http://localhost:5000/google_callback"
        google_redirect_uri = "http://127.0.0.1:5000/google_callback"
    return google_redirect_uri

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_reset_email(user):
    token = user.get_token()
    msg = Message('Password Reset Request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email])
    msg.body = f'''To reset your password, please visit the following link. The link will be expired in 5 minutes.  
{url_for('reset_password_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    # mail.send(msg)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    print(f"{user.email} (ID:{user.id}) Reset password requested!")


def send_verification_email(user):
    token = user.get_token()
    msg = Message('Email Verification Request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email])
    msg.body = f'''To confirm your email, please visit the following link. The link will be expired in 5 minutes.
{url_for('email_verification_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    # mail.send(msg)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    print(f"{user.email} (ID:{user.id}) Email verification requested!")


def getPreference(userID, planID, prefDict, semesterNew):
    def dict2List(prefDict):
        def createMatrix(nrow, ncol):
            matrix = []
            for r in range(0, nrow):
                matrix.append([])
                for c in range(0, ncol):
                    matrix[r].append("")
            return matrix

        keys = list(prefDict.keys())
        nrow = len(prefDict[keys[0]])
        ncol = len(keys)
        prefList = createMatrix(nrow, ncol)

        for c in range(0, ncol):
            for r in range(0, len(prefDict[keys[c]])):
                prefList[r][c] = prefDict[keys[c]][r]
        return prefList

    def saveData(dataList, savePath, saveName, firstRow):
        book = xlwt.Workbook(encoding="utf-8")  # 创建workbook对象
        sheetName = "Preferences"
        sheet = book.add_sheet(sheetName, cell_overwrite_ok=True)
        for i in range(0, len(firstRow)):
            sheet.write(0, i, firstRow[i])

        if (len(dataList) != 0):
            for i in range(0, len(dataList)):
                data = dataList[i]
                for j in range(0, len(data)):
                    sheet.write(i+1, j, data[j])  # i+1是因为第一行已经有了标题
                # print("已保存到第%d条" % (i+1))
        savePath = savePath + saveName + ".xls"
        book.save(savePath)
        print("Preferences Data Saved!")
        # 3.保存数据

    savePath = "./Users/" + userID + "/" + planID + "/"
    checkFolder(savePath)
    saveName = semesterNew + " Preferences"
    firstRow = list(prefDict.keys())
    prefList = dict2List(prefDict)
    saveData(prefList, savePath, saveName, firstRow)


def checkCourses(courses, semester):
    def getAllCourses(filePath, semester):
        dataList = []
        sheetName = "BU Courses " + semester
        book = xlrd.open_workbook(filePath)
        sheet = book.sheet_by_name(sheetName)
        rows = sheet.nrows
        cols = sheet.ncols
        for c in range(cols):
            if (str(sheet.cell_value(0, c)) == "Code"):
                codeIndex = c
        for r in range(1, rows):
            dataList.append(sheet.cell_value(r, codeIndex))
        return dataList

    filePath = "./Semesters/" + semester + "/BU Courses " + semester + ".xls"
    try:
        allCourses = getAllCourses(filePath, semester)
        for course in courses:
            if (course not in allCourses):
                return False
        return True
    except:
        return False


def checkFolder(savePath):
    folders = savePath.split("/")
    newPath = folders[0] + "/"
    for i in range(1, len(folders)):
        pathNotExist = bool(1 - (os.path.exists(newPath)))
        if (pathNotExist):
            os.mkdir(newPath)
        newPath = newPath + folders[i] + "/"


def getAllCourseNames(semester):
    filePath = "./Semesters/" + semester + "/BU Courses " + semester + ".xls"
    dataList = []
    sheetName = "BU Courses " + semester
    book = xlrd.open_workbook(filePath)
    sheet = book.sheet_by_name(sheetName)
    rows = sheet.nrows
    cols = sheet.ncols
    codeIndex = None
    nameIndex = None
    for c in range(cols):
        if str(sheet.cell_value(0, c)) == "Code":
            codeIndex = c
        elif str(sheet.cell_value(0, c)) == "Name":  # 假设课程名称在名为"Name"的列中
            nameIndex = c

    if codeIndex is None or nameIndex is None:
        return []  # 如果找不到代码或名称列，则返回空列表

    for r in range(1, rows):
        code = sheet.cell_value(r, codeIndex)
        name = sheet.cell_value(r, nameIndex)
        dataList.append({"code": code, "name": name})  # 以字典格式存储代码和名称

    return dataList


def getYears():
    years = []
    for year in os.listdir("./Semesters"):
        if year.startswith("20"):
            y = year.split("-")[0]
            if y is not None and y not in years:
                years.append(y)
    return years


def getAllTermNames(year):
    semesters = []
    for semester in os.listdir("./Semesters"):
        if semester.startswith(year):
            if (semester.split("-")[1] == "SUMM"):
                semesters.append("SUMM_1")
                semesters.append("SUMM_2")
            else:
                semesters.append(semester.split("-")[1])
    return semesters


def checkSubmitSuccess(userID, planID, semester):
    path = "./Users/" + str(userID) + "/" + str(planID) + \
        "/" + semester + " Preferences.xls"
    if (os.path.exists(path)):
        return True
    else:
        return False


def checkPlanSuccess(userID, planID, semester):
    path = "./Users/" + str(userID) + "/" + str(planID) + \
        "/" + semester + " Info.xls"
    if (os.path.exists(path)):
        return True
    else:
        return False


def checkRankSuccess(userID, planID, semester):
    path = "./Users/" + str(userID) + "/" + str(planID) + \
        "/" + semester + " Ranking.xls"
    if (os.path.exists(path)):
        return True
    else:
        return False


def getScheduleDetails(userID, planID, semester, planName):
    prefSheetName = "Preferences"
    prefPath = "./Users/" + str(userID) + "/" + \
        str(planID) + "/" + semester + " Preferences.xls"
    from AutoRanking import readPrefData
    prefDict = readPrefData(prefPath, prefSheetName)
    # print(prefDict)
    scheduleDetails = {}
    try:
        path = "./Users/" + str(userID) + "/" + str(planID) + \
            "/" + semester + " InfoDetails.xls"
        book = xlrd.open_workbook(path)
        sheet = book.sheet_by_name(planName)
        header_row = sheet.row_values(0)
        rows = sheet.nrows
        cols = sheet.ncols
        keys = ["Average Score", "Earliest Time", "Latest Time"]
        name = {"Average Score": "Average Score",
                "Earliest Time": "Starting Time", "Latest Time": "Ending Time"}
        min_value = {"Average Score": 0, "Earliest Time": 0, "Latest Time": 0}
        max_value = {"Average Score": 5,
                     "Earliest Time": 24, "Latest Time": 24}

        for key in keys:
            scheduleDetails[key] = {"name": None, "value": None,
                                    "check": None, "min_value": None, "max_value": None}
            key_index = header_row.index(key)
            for r in range(1, rows):
                if sheet.cell_value(r, key_index) != "":
                    scheduleDetails[key]["name"] = name[key]
                    scheduleDetails[key]["value"] = sheet.cell_value(
                        r, key_index)
                    scheduleDetails[key]["min_value"] = min_value[key]
                    scheduleDetails[key]["max_value"] = max_value[key]
                    break
            if (key == "Average Score" and scheduleDetails[key]["value"] >= prefDict[key]):
                scheduleDetails[key]["check"] = True
            elif (key == "Earliest Time" and scheduleDetails[key]["value"] >= prefDict[key]):
                scheduleDetails[key]["check"] = True
            elif (key == "Latest Time" and scheduleDetails[key]["value"] <= prefDict[key]):
                scheduleDetails[key]["check"] = True
            else:
                scheduleDetails[key]["check"] = False
    except:
        pass
    return scheduleDetails


def getEditDate(userID, planID, semester):
    editDate = {}
    file_path1 = "./Users/" + str(userID) + "/" + \
        str(planID) + "/" + semester + " Info.xls"
    file_path2 = "./Users/" + str(userID) + "/" + \
        str(planID) + "/" + semester + " Ranking.xls"
    try:
        creation_time1 = os.path.getmtime(file_path1)
        editDate1 = datetime.fromtimestamp(creation_time1)
        editDate1 = editDate1.strftime("%Y-%m-%d %H:%M:%S")
        editDate["Last Plan"] = editDate1
    except FileNotFoundError:
        pass
    try:
        creation_time2 = os.path.getmtime(file_path2)
        editDate2 = datetime.fromtimestamp(creation_time2)
        editDate2 = editDate2.strftime("%Y-%m-%d %H:%M:%S")
        editDate["Last Rank"] = editDate2
    except FileNotFoundError:
        pass
    return editDate


def get_all_schedules(semester, userID, planID, limit=500):
    return AutoSelection.AutoSelection(semester, userID, planID, limit)


def rank_all_schedules(semester, userID, planID, ignoreSeats=False):
    msg = []
    if not ignoreSeats:
        GetSeats.GetSeats(semester, userID, planID)
        msg.append("Seats are checked.")
    AddPlanDetails.AddPlanDetails(semester, userID, planID, ignoreSeats)
    msg.append("Plan details are added.")
    AutoRanking.AutoRanking(semester, userID, planID)
    msg.append("Your plans are ranked! You can see them below.")
    msg.append("No. 1 schedule should be the best one!")
    return msg


def get_ranked_plan_name(semester, userID, planID, newNum):
    rankPath = "./Users/" + userID + "/" + planID + "/"
    rankName = semester + " Ranking"
    book = xlrd.open_workbook(rankPath + rankName + ".xls")
    sheet = book.sheet_by_name(rankName)
    maxNum = sheet.nrows
    if (newNum > maxNum):
        newNum = maxNum-1
    planName = sheet.cell_value(newNum, 0)
    return planName, newNum


def create_schedule_pic(semester, userID, planID, planName):
    check = GetSchedulePic.GetSchedulePic(semester, userID, planID, planName)
    return check


def delete_user_files(userID):
    path1 = "./Users/"+str(userID)+"/"
    path2 = "./static/Users/"+str(userID)+"/"
    try:
        shutil.rmtree(path1)
    except:
        pass
    try:
        shutil.rmtree(path2)
    except:
        pass
    
def delete_plan_files(planID):
    path1 = "./Users/"+str(planID)+"/"+str(planID)+"/"
    path2 = "./static/Users/"+str(planID)+"/"+str(planID)+"/"
    try:
        shutil.rmtree(path1)
    except:
        pass
    try:
        shutil.rmtree(path2)
    except:
        pass
    