import xlwt
import xlrd


def AddPlanDetails(semesterNew, userID, planID):
    Info_bookName = semesterNew + " Info"
    allPlansInfoPath = "./Users/" + userID + "/" + planID + "/"
    allPlansInfoDict = readPlanData(allPlansInfoPath, Info_bookName)

    seatName = semesterNew + " Seats"
    seatPath = "./Users/" + userID + "/" + planID + "/"
    seatDict = readSeatData(seatPath, seatName)

    firstRow = ("Section", "Open Seats", "Instructor", "Type", "Location", "Schedule",
                "Dates", "Notes", "Semester", "Code", "RMP Score", "Average Score", "Earliest Time", "Latest Time")
    preAllocate(allPlansInfoDict, firstRow)

    addAverageScores(allPlansInfoDict)
    addTimeExtrema(allPlansInfoDict)
    addSeats(allPlansInfoDict, seatDict)
    savePlanData(allPlansInfoDict, allPlansInfoPath, Info_bookName, firstRow)

# def addSeats(allPlansInfoDict):


def readPlanData(path, bookName):
    filePath = path + bookName + ".xls"
    dataList = {}
    book = xlrd.open_workbook(filePath)
    sheetNames = book.sheet_names()
    for sheetName in sheetNames:
        planData = []
        sheet = book.sheet_by_name(sheetName)
        rows = sheet.nrows
        cols = sheet.ncols
        for r in range(1, rows):  # 从1开始，去掉标题
            data = []
            for c in range(cols):
                data.append(sheet.cell_value(r, c))
            planData.append(data)
        dataList[sheetName] = planData
    return dataList


def readSeatData(path, bookName):
    filePath = path + bookName + ".xls"
    dataList = {}
    book = xlrd.open_workbook(filePath)
    sheet = book.sheet_by_name(bookName)
    rows = sheet.nrows
    cols = sheet.ncols
    for r in range(rows):  # 从1开始，去掉标题
        dataList[sheet.cell_value(r, 0)] = int(sheet.cell_value(r, 1))
    return dataList


def preAllocate(allPlansInfoDict, firstRow):
    num = len(firstRow)
    keys = list(allPlansInfoDict.keys())
    length = len(allPlansInfoDict[keys[0]])
    for key in keys:
        plan = allPlansInfoDict[key]
        for i in range(0, length):
            section = plan[i]
            for j in range(0, num):
                if (j >= len(section)):
                    section.append("")


def addAverageScores(allPlansInfoDict):
    # Initialize dictionary for teacher scores
    scores = {"Staff": -1}
    keys = list(allPlansInfoDict.keys())
    length = len(allPlansInfoDict[keys[0]])

    # # Set pathway for teachers scores sheet
    sheetName = "BU Teachers Scores"
    path = "./Semesters/" + sheetName + ".xls"
    book = xlrd.open_workbook(path)
    sheet = book.sheet_by_name(sheetName)

    # Fill dictionary with teacher's names initially pointing to -1
    for key in keys:
        plan = allPlansInfoDict[key]
        for row in range(0, length):
            if plan[row][2] not in scores:
                professor = plan[row][2]
                scores[plan[row][2]] = -1

    # Pair the teacher's scores with their scores
    for i in range(1, sheet.nrows):
        if sheet.cell_value(i, 0) in scores and scores[sheet.cell_value(i, 0)] == -1 and sheet.cell_value(i, 3) != "NS":
            scores[sheet.cell_value(i, 0)] = sheet.cell_value(i, 3)

    # store teacher's scores in the dictionary
    for key in keys:
        plan = allPlansInfoDict[key]
        for row in range(0, length):
            section = plan[row]
            professor = section[2]
            score = scores[professor]
            section[10] = score

    # Use the dict to find the average of the teacher's scores
    # Doesn't count repeat teacher's names for the same class
    # Doesn't count scores of teachers with no scores

    courses = {}
    avgscores = []
    for i in range(0, len(keys)):
        for section in allPlansInfoDict[keys[i]]:
            courses[section[9]] = {}
        for section in allPlansInfoDict[keys[i]]:
            courses[section[9]][section[3]] = section[10]
        courseNames = list(courses.keys())
        num = 0
        sum = 0

        # see https://www.bu.edu/reg/registration/abbreviations/
        # rankedTypeList, from left to right, section types are ranked based on their importance in the course.
        # we only consider the score that of the most important section type.
        rankedTypeList = ["LEC", "IND", "EXP", "APP",
                          "DRS", "OTH", "LAB", "PLB", "DIS"]
        for name in courseNames:
            oneCourse = courses[name]
            oneCourseTypes = list(oneCourse.keys())
            for type in rankedTypeList:
                if (type in oneCourseTypes):
                    if (oneCourse[type] != -1):
                        sum += oneCourse[type]
                        num += 1
        if (num != 0):
            avgscores.append(sum / num)
        else:
            avgscores.append(0)
    for i in range(0, len(avgscores)):
        allPlansInfoDict[keys[i]][0][11] = avgscores[i]
    return


def addTimeExtrema(allPlansInfoDict):
    # initialized var
    keys = list(allPlansInfoDict.keys())
    length = len(allPlansInfoDict[keys[0]])

    for key in keys:
        startMax = 24
        endMin = 0
        for i in range(0, length):
            times = allPlansInfoDict[key][i][5].split(",")
            for a in times:
                days, start, mix, when2 = a.split(' ')
                when1, end = mix.split('-')
                hour1, minute1 = start.split(':')
                hour2, minute2 = end.split(':')
                if when1 == "pm" and int(hour1) != 12:
                    start_time = int(hour1)+12+int(minute1)/60
                else:
                    start_time = int(hour1)+int(minute1)/60
                if when2 == "pm" and int(hour2) != 12:
                    end_time = int(hour2)+12+int(minute2)/60
                else:
                    end_time = int(hour2)+int(minute2)/60
                if (start_time < startMax):
                    startMax = start_time
                if (end_time > endMin):
                    endMin = end_time
        if startMax > 12:
            hour1 = int(startMax)-12
            when1 = "pm"
        else:
            hour1 = int(startMax)
            when1 = "am"
        if endMin > 12:
            hour2 = int(endMin)-12
            when2 = "pm"
        else:
            hour2 = int(endMin)
            when2 = "am"
        minute1 = int((startMax - int(startMax))*60)
        minute2 = int((endMin - int(endMin))*60)
        # print("max is: ", hour1, ':', minute1,
        #       when1, " ", hour2, ':', minute2, when2)
        timeExteme = [startMax, endMin]
        allPlansInfoDict[key][0][12] = startMax
        allPlansInfoDict[key][0][13] = endMin
    return


def addSeats(allPlansInfoDict, seatDict):
    planKeys = list(allPlansInfoDict.keys())
    sectLen = len(allPlansInfoDict[planKeys[0]])
    for planKey in planKeys:
        plan = allPlansInfoDict[planKey]
        for section in plan:
            sectionName = section[9] + "-" + section[0]
            section[1] = seatDict[sectionName]
    return


def savePlanData(allPlansInfoDict, allPlansInfoPath, Info_bookName, firstRow):
    book = xlwt.Workbook(encoding="utf-8")  # 创建workbook对象
    plans = list(allPlansInfoDict.keys())
    for plan in plans:
        oneData = allPlansInfoDict[plan]
        # 创建表单对象，cell_overwrite_ok允许单元格被覆盖
        sheet = book.add_sheet(plan, cell_overwrite_ok=True)
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
                    sheet.write(i+n, j, data[j])  # i+n是因为第一行已经有了标题
                # print("已保存到第%d条" % (i+1))
    savePath = allPlansInfoPath + Info_bookName + "Details.xls"
    book.save(savePath)
    print("Data Updated!")


if __name__ == "__main__":
    # semesterNew = "2022-FALL"  # Fall:"FALL", Summer:"SUMM", Spring:"SPRG"
    # username = "Sam"
    # AddPlanDetails(semesterNew, username)
    pass
