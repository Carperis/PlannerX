# -*- coding: utf-8 -*-
import os
import xlwt
import xlrd


def GetPreference(username, prefDict, semesterNew):
    check = checkCourses(prefDict["Courses"], semesterNew.split("_")[0])
    if (check == False):
        return False
    savePath = "./User/" + username + "/"
    checkFolder(savePath)
    saveName = semesterNew + " Preferences " + username
    firstRow = list(prefDict.keys())

    prefList = dict2List(prefDict)

    saveData(prefList, savePath, saveName, firstRow)
    return True


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
    book = xlwt.Workbook(encoding="utf-8")  # ??????workbook??????
    sheetName = "Preferences"
    sheet = book.add_sheet(sheetName, cell_overwrite_ok=True)
    for i in range(0, len(firstRow)):
        sheet.write(0, i, firstRow[i])

    if(len(dataList) != 0):
        for i in range(0, len(dataList)):
            data = dataList[i]
            for j in range(0, len(data)):
                sheet.write(i+1, j, data[j])  # i+1????????????????????????????????????
            # print("???????????????%d???" % (i+1))
    savePath = savePath + saveName + ".xls"
    book.save(savePath)
    print("Preferences Data Saved!")
    # 3.????????????


if __name__ == "__main__":
    username = "Any"
    semester = "2022-FALL"
    prefDict = {}
    prefDict["Courses"] = ['ENG EC 327', 'ENG EC 311', 'ENG ME 305']
    prefDict["AvgScore"] = [3.5]
    prefDict["EarlyTime"] = [8]
    prefDict["LateTime"] = [18]
    GetPreference(username, prefDict, semester)
