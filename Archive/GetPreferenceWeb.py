# -*- coding: utf-8 -*-
import os
import xlwt
import xlrd
from datetime import datetime


def GetPreference(userID, planID, prefDict, semesterNew):
    savePath = "./Users/" + userID + "/" + planID + "/"
    checkFolder(savePath)
    saveName = semesterNew + " Preferences"
    firstRow = list(prefDict.keys())

    prefList = dict2List(prefDict)

    saveData(prefList, savePath, saveName, firstRow)
    print("saved")


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
        print("File not found1.") 
    try:
        creation_time2 = os.path.getmtime(file_path2)
        editDate2 = datetime.fromtimestamp(creation_time2)
        editDate2 = editDate2.strftime("%Y-%m-%d %H:%M:%S")
        editDate["Last Rank"] = editDate2
        print("File Creation Date and Time:", editDate)
    except FileNotFoundError:
        print("File not found2.")
    return editDate


if __name__ == "__main__":
    planname = "Any"
    semester = "2022-FALL"
    prefDict = {}
    prefDict["Courses"] = ['ENG EC 327', 'ENG EC 311', 'ENG ME 305']
    prefDict["AvgScore"] = [3.5]
    prefDict["EarlyTime"] = [8]
    prefDict["LateTime"] = [18]
    GetPreference(planname, prefDict, semester)
