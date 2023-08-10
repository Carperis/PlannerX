# -*- coding: utf-8 -*-
import os
import xlwt
import xlrd


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
            if(str(sheet.cell_value(0, c)) == "Code"):
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
        if(pathNotExist):
            os.mkdir(newPath)
        newPath = newPath + folders[i] + "/"


def saveData(dataList, savePath, saveName, firstRow):
    book = xlwt.Workbook(encoding="utf-8")  # 创建workbook对象
    sheetName = "Preferences"
    sheet = book.add_sheet(sheetName, cell_overwrite_ok=True)
    for i in range(0, len(firstRow)):
        sheet.write(0, i, firstRow[i])

    if(len(dataList) != 0):
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

if __name__ == "__main__":
    planname = "Any"
    semester = "2022-FALL"
    prefDict = {}
    prefDict["Courses"] = ['ENG EC 327', 'ENG EC 311', 'ENG ME 305']
    prefDict["AvgScore"] = [3.5]
    prefDict["EarlyTime"] = [8]
    prefDict["LateTime"] = [18]
    GetPreference(planname, prefDict, semester)
