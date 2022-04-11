# -*- coding: utf-8 -*-

import xlrd
import xlwt
import re
import time


def main():
    semester = "2022-FALL"  # Fall:"FALL", Summer:"SUMM", Spring:"SPRG"
    scorPath = "./BU Teachers Scores.xls"
    courPath = "./Semesters/" + semester + "/" + "BU Courses " + semester + ".xls"
    prefPath = "./My Preference F22.xls"

    prefSheetName = "My Preference"
    prefData = readData(prefPath, prefSheetName)
    print("Got preference data!")

    # courSheetName = "BU Courses " + semester
    # courData = readCourData(courPath, courSheetName, prefData) #暂时用不到

    scorSheetName = "BU Teachers Scores"
    scorData = readData(scorPath, scorSheetName)
    print("Got scores data!")

    sectData = []
    typeList = []
    for course in prefData:
        types = course[1].split(",")
        typeList.append(types)
        courCode = course[0]
        sectPath = "./Semesters" + semester + "/" + semester + " Sections/" + courCode + ".xls"
        sections = readSectData(sectPath, courCode, scorData)
        sections = clearErrors(sections)
        sectData.append(sections)
    print("Got sections data!\n")

    sortedSectData = sortSections(sectData, typeList)
    subPlans = getSubPlans(sortedSectData, prefData)
    plans = getPlans(subPlans, prefData)
    print(len(plans))
    # for i in range(len(plans)):
    #     schedule = plans[i]
    #     saveName = "Schedule" + i
    #     saveData(schedule, "./", saveName, "")


def clearErrors(sections):
    newSections = []
    for section in sections:
        a = "ARR"
        b = "0: am"
        c = str(section[5])
        if ((not a in c) and (not b in c)):
            newSections.append(section)
    return newSections


def sortSections(sectData, typeList):
    sortedSectData = []
    for i in range(len(sectData)):
        tempTypeList = typeList[i]
        courSections = []
        for type in tempTypeList:
            courSections.append([])
        for section in sectData[i]:
            type = section[3]
            if(type in tempTypeList):
                index = tempTypeList.index(type)
                courSections[index].append(section)
        sortedSectData.append(courSections)
    return sortedSectData


def getSubPlans(sortedSectData, prefData):
    print("Start getting subplans...")
    subPlans = []
    for course in sortedSectData:
        n = 0
        print(course[0][0][len(course[0][0])-1] + ": ", end="")
        courSubPlans = []
        # Get all applicable subplans of one course
        length = len(course)
        partLen = []
        currInd = []
        for part in course:
            partLen.append(len(part)-1)
            currInd.append(0)
        currInd[0] -= 1
        while(currInd != partLen):
            # increment currInd 任意进制进位器*
            currInd[0] += 1
            for i in range(len(currInd)):
                if(currInd[i] > partLen[i]):
                    currInd[i] = 0
                    if((i+1) < len(currInd)):
                        currInd[i+1] += 1
            oneSubPlan = []
            for i in range(length):
                oneSubPlan.append(course[i][currInd[i]])
            # Now we get one subplan

            # Check this subplan, add more checks below
            checkList = []
            checkList.append(
                bool(checkSameTeacher(oneSubPlan, ["LEC", "DIS"])))
            checkList.append(bool(getAndCheckSchedule(oneSubPlan, "")))

            # Evaluate checks
            checkResult = True
            for check in checkList:
                if(check == False):
                    checkResult = False
            if(checkResult):
                n += 1
                print("\r" + course[0][0][len(course[0][0]) -
                      1] + ": %d plans" % (n), end="")
                oneSubPlan.append(getAndCheckSchedule(oneSubPlan, ""))
                courSubPlans.append(oneSubPlan)

        # Got all subplans of this course
        print(" Done")
        subPlans.append(courSubPlans)

    # Got all subplans of selected courses
    print("Got Subplans!\n")
    return subPlans


def getPlans(subPlans, prefData):
    def getPartPlans(subPlans, prefData):
        partPlans = []
        length = len(subPlans)
        if(length <= 1):
            print("Error")
            return subPlans
        partLen = []
        currInd = []
        n = 0
        totaln = 1
        nDone = 0
        for part in subPlans:
            partLen.append(len(part)-1)
            totaln *= len(part)
            currInd.append(0)
        # partLen = [10, 0, 0, 0, 0]
        currInd[0] -= 1
        while(currInd != partLen):
            # increment currInd
            currInd[0] += 1
            n += 1
            for i in range(len(currInd)):
                if(currInd[i] > partLen[i]):
                    currInd[i] = 0
                    if((i+1) < len(currInd)):
                        currInd[i+1] += 1
            onePlan = []
            for i in range(length):
                onePlan.append(subPlans[i][currInd[i]])

            # Checks this one plan
            checkList = []
            p1 = onePlan[0]
            for i in range(1, len(onePlan)):
                p2 = onePlan[i]
                sch1 = p1[len(p1) - 1]
                sch2 = p2[len(p2) - 1]
                r = compareSchedule(sch1, sch2)
                checkList.append(r)
                p1 = p2

            # Evaluate checks
            checkResult = True
            for check in checkList:
                if(check == False):
                    checkResult = False
            if(checkResult):
                sections = []
                for subPlan in onePlan:
                    for i in range(0, len(subPlan) - 1):
                        sections.append(subPlan[i])
                nDone += 1
                schedule = getAndCheckSchedule(sections, "")
                sections.append(schedule)
                partPlans.append(sections)
            print("\r%d / %d: %d plans" % (n, totaln, nDone), end="")

        print(" Done")
        return partPlans

    # if(len(subPlans) <= 1):
    #     return subPlans
    # else:
    #     print("Start getting plans... " + str(len(subPlans)))
    #     temp = []
    #     part1 = subPlans[0]
    #     for i in range(1, len(subPlans)):
    #         part2 = subPlans[i]
    #         onePartPlans = [part1, part2]
    #         print(str(len(part1)) + "x" + str(len(part2)) + " > ")
    #         temp.append(getPartPlans(onePartPlans, prefData))
    #         part1 = part2
    #     print("Got Plans!\n")
    #     return getPlans(temp, prefData)

    print("Start getting plans... ")
    part1 = subPlans[0]
    for i in range(1, len(subPlans)):
        part2 = subPlans[i]
        onePartPlans = [part1, part2]
        print(str(len(part1)) + "x" + str(len(part2)) + " > ")
        part1 = getPartPlans(onePartPlans, prefData)
    print("Got Plans!\n")
    return part1


def newSchedule():
    timeRange = 24*12
    weekRange = 7
    schedule = []
    oneWeek = ["Time", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hours = 0
    minutes = 0
    for i in range(0, timeRange + 1):
        schedule.append([])
        for j in range(0, weekRange + 1):
            if(i == 0):
                schedule[i].append(oneWeek[j])
            else:
                if(j == 0):
                    time = "%2d" % hours + ":" + "%2d" % minutes
                    schedule[i].append(time)
                    minutes += 5
                    if(minutes >= 60):
                        minutes = 0
                        hours += 1
                    if(hours >= 24):
                        hours = 0
                else:
                    schedule[i].append("")
    return schedule
# Checks:


def compareSchedule(sch1, sch2):
    for r in range(1, len(sch1)):
        for c in range(1, len(sch1[0])):
            hasSect1 = bool(sch1[r][c])
            hasSect2 = bool(sch2[r][c])
            if(hasSect1 & hasSect2):
                return False
    return True


def checkScore():
    pass


def checkSameTeacher(sections, types):
    teachers = []
    for type in types:
        for section in sections:
            if(section[3] == type):
                teachers.append(section[2])
    if(len(teachers) <= 1):
        return True
    elif(teachers[1:] == teachers[:-1]):
        return True
    else:
        return False


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
                        for i in range(srow + 1, erow):
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


def readSectData(filePath, sheetName, scorData):
    dataList = []
    teachers = [x[0] for x in scorData]
    book = xlrd.open_workbook(filePath)
    sheet = book.sheet_by_name(sheetName)
    rows = sheet.nrows
    cols = sheet.ncols
    for r in range(1, rows):  # 从1开始，去掉标题
        data = []
        for c in range(cols):
            data.append(sheet.cell_value(r, c))
        teacher = data[2]
        if(teacher in teachers):
            i = teachers.index(teacher)
            scores = scorData[i][3]
            data.append(scores)
        else:
            data.append("NS")
        data.append(sheetName)
        dataList.append(data)
    return dataList


def readData(filePath, sheetName):
    dataList = []
    book = xlrd.open_workbook(filePath)
    sheet = book.sheet_by_name(sheetName)
    rows = sheet.nrows
    cols = sheet.ncols
    for r in range(1, rows):  # 从1开始，去掉标题
        data = []
        for c in range(cols):
            data.append(sheet.cell_value(r, c))
        dataList.append(data)
    return dataList


def readCourData(filePath, sheetName, prefData):  # 暂时用不到
    dataList = []
    book = xlrd.open_workbook(filePath)
    sheet = book.sheet_by_name(sheetName)
    rows = sheet.nrows
    cols = sheet.ncols
    for pref in prefData:
        prefCode = pref[0].upper()
        for r in range(1, rows):  # 从1开始，去掉标题
            code = sheet.cell_value(r, 0).upper()
            if(code == prefCode):
                data = []
                for c in range(cols):
                    data.append(sheet.cell_value(r, c))
                dataList.append(data)
            else:
                continue
    return dataList

# Save Data


def saveData(dataList, savePath, saveName, firstRow):
    book = xlwt.Workbook(encoding="utf-8")  # 创建workbook对象
    # 创建表单对象，cell_overwrite_ok允许单元格被覆盖
    sheet = book.add_sheet(saveName, cell_overwrite_ok=True)
    if(firstRow):
        for i in range(0, len(firstRow)):
            sheet.write(0, i, firstRow[i])
        n = 1
    else:
        n = 0

    if(len(dataList) != 0):
        for i in range(0, len(dataList)):
            data = dataList[i]
            for j in range(0, len(data)):
                sheet.write(i+n, j, data[j])  # i+n是因为第一行已经有了标题
            # print("已保存到第%d条" % (i+1))
    savePath = savePath + saveName + ".xls"
    book.save(savePath)
    print("Data Saved!")


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
