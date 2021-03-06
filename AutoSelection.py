# -*- coding: utf-8 -*-
import re
import time
import xlrd
import xlwt
import AlgorithmV2
import AlgorithmV2_1


def AutoSelection(semesterNew, username):
    semester = semesterNew.split("_")[0]
    prefSheetName = "Preferences"
    prefPath = "./User/" + username + "/" + \
        semesterNew + " Preferences " + username + ".xls"
    schedulesPath = "./User/" + username + "/"
    allPlansInfoPath = "./User/" + username + "/"

    prefData = readPrefData(prefPath, prefSheetName)
    print("Got preference data!")
    sectData = []
    typeList = []
    SameTeacherDict = {}
    for course in prefData:
        courCode = course[0]  # get course code

        sectPath = "./Semesters/" + semester + "/" + \
            semester + " Sections/" + courCode + ".xls"
        sections = readSectData(sectPath, courCode)
        sections = clearErrors(sections)
        sectData.append(sections)

        types = getTypes(sections)
        typeList.append(types)

        SameTeacherTypes = getSameTeacherTypes(types, sections)
        SameTeacherDict[courCode] = SameTeacherTypes

    print("Got sections data!\n")

    prepData = data2Dict(sectData, typeList, prefData)

    # choose one of the following algorithms
    # allPlans = AlgorithmV2_1.autoMatchCourses(prepData, SameTeacherDict)
    allPlans = AlgorithmV2.autoMatchCourses(prepData, SameTeacherDict, 1000)
    # 3rd Arg: set max num of plans, "-1" means get all plans

    if(len(allPlans) == 0):
        print("NO SCHEDULE IS AVAILABLE")
        return 0
    allPlansList = allPlan2List(allPlans, list(allPlans[0].keys()))
    allPlansInfo = [plan2Sections(plan, prepData) for plan in allPlansList]

    firstRow = ("Section", "Open Seats", "Instructor", "Type",
                "Location", "Schedule", "Dates", "Notes", "Semester", "Code")
    Info_bookName = semesterNew + " " + username + " " + "Info"
    saveMultiData(allPlansInfo, allPlansInfoPath,
                  Info_bookName, "Plan", firstRow)  # Save Plans

    # schedules = []
    # for plan in allPlansInfo:
    #     schedules.append(getAndCheckSchedule(plan, ""))
    # Schedules_bookName = semesterNew + " " + username + " " + "Schedules"
    # saveMultiData(schedules, schedulesPath,
    #               Schedules_bookName, "Schedule", [])  # Save Schedules
    return len(allPlansList)
# Operate Data


def getTypes(sections):
    types = []
    for i in range(0, len(sections)):
        type = sections[i][3]
        if (type not in types):
            types.append(type)
    return types


def getSameTeacherTypes(types, sections):
    result = []
    professors = {}
    for type in types:
        subprofessors = []
        noStaff = True
        for i in range(0, len(sections)):
            if(sections[i][3] == type):
                subprofessors.append(sections[i][2])
                if (sections[i][2] == "Staff"):
                    noStaff = False
        if (noStaff):
            professors[type] = subprofessors
    for type1 in list(professors.keys()):
        isSame = False
        for name1 in professors[type1]:
            for type2 in list(professors.keys()):
                if (type2 != type1):
                    for name2 in professors[type2]:
                        if (name1 == name2):
                            isSame = True
                            result.append(type1)
                            break
                if (isSame):
                    break
            if (isSame):
                break
    if (len(result) == 0):
        result = [""]
    return result


def clearErrors(sections):
    newSections = []
    for section in sections:
        a = "ARR"
        b = "0: am"
        c = str(section[5])
        if ((not a in c) and (not b in c)):
            newSections.append(section)
    return newSections


def plan2Sections(plan, prepData):
    planSections = []
    for sectName in plan:
        course = sectName.split("-")[1].split(",")[0]
        type = sectName.split("-")[1].split(",")[1]
        id = sectName.split("-")[0]
        for section in prepData[course][type]:
            if (section[0] == id):
                planSections.append(section)
    return planSections


def allPlan2List(allPlans, sectList):
    allPlanList = []
    for plan in allPlans:
        onePlanList = []
        for sectName in sectList:
            onePlanList.append(plan[sectName])
        allPlanList.append(onePlanList)
    return allPlanList


def data2Dict(sectData, typeList, prefData):
    prepData = {}
    for i in range(len(sectData)):
        tempTypeList = typeList[i]
        courSections = {}
        for type in tempTypeList:
            courSections[type] = []
        for section in sectData[i]:
            secType = section[3]
            if (secType in tempTypeList):
                courSections[secType].append(section)
        for key in list(courSections.keys()):
            if (any(courSections[key]) == False):
                courSections.pop(key)
        prepData[prefData[i][0]] = courSections
    return prepData


def getAndCheckSchedule(sections, sch):
    if(not sch):
        sch = [['Time', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], [' 0: 0', '', '', '', '', '', '', ''], [' 0: 5', '', '', '', '', '', '', ''], [' 0:10', '', '', '', '', '', '', ''], [' 0:15', '', '', '', '', '', '', ''], [' 0:20', '', '', '', '', '', '', ''], [' 0:25', '', '', '', '', '', '', ''], [' 0:30', '', '', '', '', '', '', ''], [' 0:35', '', '', '', '', '', '', ''], [' 0:40', '', '', '', '', '', '', ''], [' 0:45', '', '', '', '', '', '', ''], [' 0:50', '', '', '', '', '', '', ''], [' 0:55', '', '', '', '', '', '', ''], [' 1: 0', '', '', '', '', '', '', ''], [' 1: 5', '', '', '', '', '', '', ''], [' 1:10', '', '', '', '', '', '', ''], [' 1:15', '', '', '', '', '', '', ''], [' 1:20', '', '', '', '', '', '', ''], [' 1:25', '', '', '', '', '', '', ''], [' 1:30', '', '', '', '', '', '', ''], [' 1:35', '', '', '', '', '', '', ''], [' 1:40', '', '', '', '', '', '', ''], [' 1:45', '', '', '', '', '', '', ''], [' 1:50', '', '', '', '', '', '', ''], [' 1:55', '', '', '', '', '', '', ''], [' 2: 0', '', '', '', '', '', '', ''], [' 2: 5', '', '', '', '', '', '', ''], [' 2:10', '', '', '', '', '', '', ''], [' 2:15', '', '', '', '', '', '', ''], [' 2:20', '', '', '', '', '', '', ''], [' 2:25', '', '', '', '', '', '', ''], [' 2:30', '', '', '', '', '', '', ''], [' 2:35', '', '', '', '', '', '', ''], [' 2:40', '', '', '', '', '', '', ''], [' 2:45', '', '', '', '', '', '', ''], [' 2:50', '', '', '', '', '', '', ''], [' 2:55', '', '', '', '', '', '', ''], [' 3: 0', '', '', '', '', '', '', ''], [' 3: 5', '', '', '', '', '', '', ''], [' 3:10', '', '', '', '', '', '', ''], [' 3:15', '', '', '', '', '', '', ''], [' 3:20', '', '', '', '', '', '', ''], [' 3:25', '', '', '', '', '', '', ''], [' 3:30', '', '', '', '', '', '', ''], [' 3:35', '', '', '', '', '', '', ''], [' 3:40', '', '', '', '', '', '', ''], [' 3:45', '', '', '', '', '', '', ''], [' 3:50', '', '', '', '', '', '', ''], [' 3:55', '', '', '', '', '', '', ''], [' 4: 0', '', '', '', '', '', '', ''], [' 4: 5', '', '', '', '', '', '', ''], [' 4:10', '', '', '', '', '', '', ''], [' 4:15', '', '', '', '', '', '', ''], [' 4:20', '', '', '', '', '', '', ''], [' 4:25', '', '', '', '', '', '', ''], [' 4:30', '', '', '', '', '', '', ''], [' 4:35', '', '', '', '', '', '', ''], [' 4:40', '', '', '', '', '', '', ''], [' 4:45', '', '', '', '', '', '', ''], [' 4:50', '', '', '', '', '', '', ''], [' 4:55', '', '', '', '', '', '', ''], [' 5: 0', '', '', '', '', '', '', ''], [' 5: 5', '', '', '', '', '', '', ''], [' 5:10', '', '', '', '', '', '', ''], [' 5:15', '', '', '', '', '', '', ''], [' 5:20', '', '', '', '', '', '', ''], [' 5:25', '', '', '', '', '', '', ''], [' 5:30', '', '', '', '', '', '', ''], [' 5:35', '', '', '', '', '', '', ''], [' 5:40', '', '', '', '', '', '', ''], [' 5:45', '', '', '', '', '', '', ''], [' 5:50', '', '', '', '', '', '', ''], [' 5:55', '', '', '', '', '', '', ''], [' 6: 0', '', '', '', '', '', '', ''], [' 6: 5', '', '', '', '', '', '', ''], [' 6:10', '', '', '', '', '', '', ''], [' 6:15', '', '', '', '', '', '', ''], [' 6:20', '', '', '', '', '', '', ''], [' 6:25', '', '', '', '', '', '', ''], [' 6:30', '', '', '', '', '', '', ''], [' 6:35', '', '', '', '', '', '', ''], [' 6:40', '', '', '', '', '', '', ''], [' 6:45', '', '', '', '', '', '', ''], [' 6:50', '', '', '', '', '', '', ''], [' 6:55', '', '', '', '', '', '', ''], [' 7: 0', '', '', '', '', '', '', ''], [' 7: 5', '', '', '', '', '', '', ''], [' 7:10', '', '', '', '', '', '', ''], [' 7:15', '', '', '', '', '', '', ''], [' 7:20', '', '', '', '', '', '', ''], [' 7:25', '', '', '', '', '', '', ''], [' 7:30', '', '', '', '', '', '', ''], [' 7:35', '', '', '', '', '', '', ''], [' 7:40', '', '', '', '', '', '', ''], [' 7:45', '', '', '', '', '', '', ''], [' 7:50', '', '', '', '', '', '', ''], [' 7:55', '', '', '', '', '', '', ''], [' 8: 0', '', '', '', '', '', '', ''], [' 8: 5', '', '', '', '', '', '', ''], [' 8:10', '', '', '', '', '', '', ''], [' 8:15', '', '', '', '', '', '', ''], [' 8:20', '', '', '', '', '', '', ''], [' 8:25', '', '', '', '', '', '', ''], [' 8:30', '', '', '', '', '', '', ''], [' 8:35', '', '', '', '', '', '', ''], [' 8:40', '', '', '', '', '', '', ''], [' 8:45', '', '', '', '', '', '', ''], [' 8:50', '', '', '', '', '', '', ''], [' 8:55', '', '', '', '', '', '', ''], [' 9: 0', '', '', '', '', '', '', ''], [' 9: 5', '', '', '', '', '', '', ''], [' 9:10', '', '', '', '', '', '', ''], [' 9:15', '', '', '', '', '', '', ''], [' 9:20', '', '', '', '', '', '', ''], [' 9:25', '', '', '', '', '', '', ''], [' 9:30', '', '', '', '', '', '', ''], [' 9:35', '', '', '', '', '', '', ''], [' 9:40', '', '', '', '', '', '', ''], [' 9:45', '', '', '', '', '', '', ''], [' 9:50', '', '', '', '', '', '', ''], [' 9:55', '', '', '', '', '', '', ''], ['10: 0', '', '', '', '', '', '', ''], ['10: 5', '', '', '', '', '', '', ''], ['10:10', '', '', '', '', '', '', ''], ['10:15', '', '', '', '', '', '', ''], ['10:20', '', '', '', '', '', '', ''], ['10:25', '', '', '', '', '', '', ''], ['10:30', '', '', '', '', '', '', ''], ['10:35', '', '', '', '', '', '', ''], ['10:40', '', '', '', '', '', '', ''], ['10:45', '', '', '', '', '', '', ''], ['10:50', '', '', '', '', '', '', ''], ['10:55', '', '', '', '', '', '', ''], ['11: 0', '', '', '', '', '', '', ''], ['11: 5', '', '', '', '', '', '', ''], ['11:10', '', '', '', '', '', '', ''], ['11:15', '', '', '', '', '', '', ''], ['11:20', '', '', '', '', '', '', ''], ['11:25', '', '', '', '', '', '', ''], ['11:30', '', '', '', '', '', '', ''], ['11:35', '', '', '', '', '', '', ''], ['11:40', '', '', '', '', '', '', ''], ['11:45', '', '', '', '', '', '', ''], ['11:50', '', '', '', '', '', '', ''], [
            '11:55', '', '', '', '', '', '', ''], ['12: 0', '', '', '', '', '', '', ''], ['12: 5', '', '', '', '', '', '', ''], ['12:10', '', '', '', '', '', '', ''], ['12:15', '', '', '', '', '', '', ''], ['12:20', '', '', '', '', '', '', ''], ['12:25', '', '', '', '', '', '', ''], ['12:30', '', '', '', '', '', '', ''], ['12:35', '', '', '', '', '', '', ''], ['12:40', '', '', '', '', '', '', ''], ['12:45', '', '', '', '', '', '', ''], ['12:50', '', '', '', '', '', '', ''], ['12:55', '', '', '', '', '', '', ''], ['13: 0', '', '', '', '', '', '', ''], ['13: 5', '', '', '', '', '', '', ''], ['13:10', '', '', '', '', '', '', ''], ['13:15', '', '', '', '', '', '', ''], ['13:20', '', '', '', '', '', '', ''], ['13:25', '', '', '', '', '', '', ''], ['13:30', '', '', '', '', '', '', ''], ['13:35', '', '', '', '', '', '', ''], ['13:40', '', '', '', '', '', '', ''], ['13:45', '', '', '', '', '', '', ''], ['13:50', '', '', '', '', '', '', ''], ['13:55', '', '', '', '', '', '', ''], ['14: 0', '', '', '', '', '', '', ''], ['14: 5', '', '', '', '', '', '', ''], ['14:10', '', '', '', '', '', '', ''], ['14:15', '', '', '', '', '', '', ''], ['14:20', '', '', '', '', '', '', ''], ['14:25', '', '', '', '', '', '', ''], ['14:30', '', '', '', '', '', '', ''], ['14:35', '', '', '', '', '', '', ''], ['14:40', '', '', '', '', '', '', ''], ['14:45', '', '', '', '', '', '', ''], ['14:50', '', '', '', '', '', '', ''], ['14:55', '', '', '', '', '', '', ''], ['15: 0', '', '', '', '', '', '', ''], ['15: 5', '', '', '', '', '', '', ''], ['15:10', '', '', '', '', '', '', ''], ['15:15', '', '', '', '', '', '', ''], ['15:20', '', '', '', '', '', '', ''], ['15:25', '', '', '', '', '', '', ''], ['15:30', '', '', '', '', '', '', ''], ['15:35', '', '', '', '', '', '', ''], ['15:40', '', '', '', '', '', '', ''], ['15:45', '', '', '', '', '', '', ''], ['15:50', '', '', '', '', '', '', ''], ['15:55', '', '', '', '', '', '', ''], ['16: 0', '', '', '', '', '', '', ''], ['16: 5', '', '', '', '', '', '', ''], ['16:10', '', '', '', '', '', '', ''], ['16:15', '', '', '', '', '', '', ''], ['16:20', '', '', '', '', '', '', ''], ['16:25', '', '', '', '', '', '', ''], ['16:30', '', '', '', '', '', '', ''], ['16:35', '', '', '', '', '', '', ''], ['16:40', '', '', '', '', '', '', ''], ['16:45', '', '', '', '', '', '', ''], ['16:50', '', '', '', '', '', '', ''], ['16:55', '', '', '', '', '', '', ''], ['17: 0', '', '', '', '', '', '', ''], ['17: 5', '', '', '', '', '', '', ''], ['17:10', '', '', '', '', '', '', ''], ['17:15', '', '', '', '', '', '', ''], ['17:20', '', '', '', '', '', '', ''], ['17:25', '', '', '', '', '', '', ''], ['17:30', '', '', '', '', '', '', ''], ['17:35', '', '', '', '', '', '', ''], ['17:40', '', '', '', '', '', '', ''], ['17:45', '', '', '', '', '', '', ''], ['17:50', '', '', '', '', '', '', ''], ['17:55', '', '', '', '', '', '', ''], ['18: 0', '', '', '', '', '', '', ''], ['18: 5', '', '', '', '', '', '', ''], ['18:10', '', '', '', '', '', '', ''], ['18:15', '', '', '', '', '', '', ''], ['18:20', '', '', '', '', '', '', ''], ['18:25', '', '', '', '', '', '', ''], ['18:30', '', '', '', '', '', '', ''], ['18:35', '', '', '', '', '', '', ''], ['18:40', '', '', '', '', '', '', ''], ['18:45', '', '', '', '', '', '', ''], ['18:50', '', '', '', '', '', '', ''], ['18:55', '', '', '', '', '', '', ''], ['19: 0', '', '', '', '', '', '', ''], ['19: 5', '', '', '', '', '', '', ''], ['19:10', '', '', '', '', '', '', ''], ['19:15', '', '', '', '', '', '', ''], ['19:20', '', '', '', '', '', '', ''], ['19:25', '', '', '', '', '', '', ''], ['19:30', '', '', '', '', '', '', ''], ['19:35', '', '', '', '', '', '', ''], ['19:40', '', '', '', '', '', '', ''], ['19:45', '', '', '', '', '', '', ''], ['19:50', '', '', '', '', '', '', ''], ['19:55', '', '', '', '', '', '', ''], ['20: 0', '', '', '', '', '', '', ''], ['20: 5', '', '', '', '', '', '', ''], ['20:10', '', '', '', '', '', '', ''], ['20:15', '', '', '', '', '', '', ''], ['20:20', '', '', '', '', '', '', ''], ['20:25', '', '', '', '', '', '', ''], ['20:30', '', '', '', '', '', '', ''], ['20:35', '', '', '', '', '', '', ''], ['20:40', '', '', '', '', '', '', ''], ['20:45', '', '', '', '', '', '', ''], ['20:50', '', '', '', '', '', '', ''], ['20:55', '', '', '', '', '', '', ''], ['21: 0', '', '', '', '', '', '', ''], ['21: 5', '', '', '', '', '', '', ''], ['21:10', '', '', '', '', '', '', ''], ['21:15', '', '', '', '', '', '', ''], ['21:20', '', '', '', '', '', '', ''], ['21:25', '', '', '', '', '', '', ''], ['21:30', '', '', '', '', '', '', ''], ['21:35', '', '', '', '', '', '', ''], ['21:40', '', '', '', '', '', '', ''], ['21:45', '', '', '', '', '', '', ''], ['21:50', '', '', '', '', '', '', ''], ['21:55', '', '', '', '', '', '', ''], ['22: 0', '', '', '', '', '', '', ''], ['22: 5', '', '', '', '', '', '', ''], ['22:10', '', '', '', '', '', '', ''], ['22:15', '', '', '', '', '', '', ''], ['22:20', '', '', '', '', '', '', ''], ['22:25', '', '', '', '', '', '', ''], ['22:30', '', '', '', '', '', '', ''], ['22:35', '', '', '', '', '', '', ''], ['22:40', '', '', '', '', '', '', ''], ['22:45', '', '', '', '', '', '', ''], ['22:50', '', '', '', '', '', '', ''], ['22:55', '', '', '', '', '', '', ''], ['23: 0', '', '', '', '', '', '', ''], ['23: 5', '', '', '', '', '', '', ''], ['23:10', '', '', '', '', '', '', ''], ['23:15', '', '', '', '', '', '', ''], ['23:20', '', '', '', '', '', '', ''], ['23:25', '', '', '', '', '', '', ''], ['23:30', '', '', '', '', '', '', ''], ['23:35', '', '', '', '', '', '', ''], ['23:40', '', '', '', '', '', '', ''], ['23:45', '', '', '', '', '', '', ''], ['23:50', '', '', '', '', '', '', ''], ['23:55', '', '', '', '', '', '', '']]

    def findIndex(day, hours, minutes):
        if(day == "M"):
            col = 1
        elif(day == "T"):
            col = 2
        elif(day == "W"):
            col = 3
        elif(day == "R"):
            col = 4
        elif(day == "F"):
            col = 5
        # elif(day == "Sa"):
        #     col = 6
        # elif(day == "Su"):
        #     col = 7
        row = int(1 + (12*hours) + (minutes/5))
        return [row, col]

    def timeConvertion(time):
        timeDict = {"hours": 0, "minutes": 0}
        hrMin = time[0].split(":")
        AmPm = time[1]
        if((AmPm == "pm") & (int(hrMin[0]) < 12)):
            timeDict["hours"] = int(hrMin[0]) + 12
        else:
            timeDict["hours"] = int(hrMin[0])
        timeDict["minutes"] = int(hrMin[1])
        return timeDict

    for section in sections:
        # Creat display title
        ID = section[0]
        code = section[len(section) - 1]
        type = section[3]
        title = ID + "-" + code + "-" + type

        # Extract time information
        timeRawData = section[5].split(",")
        timeNewData = []
        for oneRawtime in timeRawData:
            days = re.findall(r'[A-Z]', oneRawtime)
            time = re.findall(
                r'([0-9]?[0-9]:[0-9][0-9]) ([a-z]{2})', oneRawtime)
            if(len(time) < 2):
                return False
            start = timeConvertion(time[0])
            end = timeConvertion(time[1])
            onetime = [days, start, end]
            timeNewData.append(onetime)

        # Put section in schedule
        for oneNewtime in timeNewData:
            startHr = oneNewtime[1]["hours"]
            startMin = oneNewtime[1]["minutes"]
            endHr = oneNewtime[2]["hours"]
            endMin = oneNewtime[2]["minutes"]
            for day in oneNewtime[0]:
                [srow, scol] = findIndex(day, startHr, startMin)
                [erow, ecol] = findIndex(day, endHr, endMin)
                if(not sch[srow][scol]):
                    sch[srow][scol] = title
                    if(not sch[erow][ecol]):
                        sch[erow][ecol] = title
                        for i in range(srow+1, erow):
                            if (not sch[i][ecol]):
                                sch[i][ecol] = title
                            else:
                                return False
                    else:
                        return False
                else:
                    return False

    return sch

# Get Data:


def readSectData(filePath, sheetName):
    dataList = []
    book = xlrd.open_workbook(filePath)
    sheet = book.sheet_by_name(sheetName)
    rows = sheet.nrows
    cols = sheet.ncols
    for r in range(1, rows):  # ???1?????????????????????
        data = []
        for c in range(cols):
            data.append(sheet.cell_value(r, c))
        data.append(sheetName)
        dataList.append(data)
    return dataList


def readPrefData(filePath, sheetName):
    dataList = []
    book = xlrd.open_workbook(filePath)
    sheet = book.sheet_by_name(sheetName)
    rows = sheet.nrows
    cols = len(sheet.row_slice(0))
    for r in range(1, rows):  # ???1?????????????????????
        data = []
        for c in range(cols):
            data.append(sheet.cell_value(r, c))
        dataList.append(data)
    return dataList

# Save Data


def saveMultiData(multiData, savePath, bookName, sheetName, firstRow):
    book = xlwt.Workbook(encoding="utf-8")  # ??????workbook??????
    num = 1
    for oneData in multiData:
        # ?????????????????????cell_overwrite_ok????????????????????????
        sheet = book.add_sheet(
            sheetName + " " + str(num), cell_overwrite_ok=True)
        if(firstRow):
            for i in range(0, len(firstRow)):
                sheet.write(0, i, firstRow[i])
            n = 1
        else:
            n = 0
        if(len(oneData) != 0):
            for i in range(0, len(oneData)):
                data = oneData[i]
                for j in range(0, len(data)):
                    sheet.write(i+n, j, data[j])  # i+n????????????????????????????????????
                # print("???????????????%d???" % (i+1))
        num += 1
    savePath = savePath + bookName + ".xls"
    book.save(savePath)
    print("Data Saved!")


if __name__ == "__main__":
    start_time = time.time()
    semesterNew = "2022-SUMM_1"  # Fall:"FALL", Summer:"SUMM", Spring:"SPRG"
    username = "sam"
    AutoSelection(semesterNew, username)
    print("--- %s seconds ---" % (time.time() - start_time))
