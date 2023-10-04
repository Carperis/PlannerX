from collections import defaultdict
import xlrd
import xlwt


def AutoRanking(semesterNew, userID, planID):
    prefSheetName = "Preferences"
    prefPath = (
        "./Users/" + userID + "/" + planID + "/" + semesterNew + " Preferences" + ".xls"
    )
    prefDict = readPrefData(prefPath, prefSheetName)

    prefRank = {  # key: a certain preference, value: weight(importance) of this preference (1 is lowest)
        "Average Score": 1,
        "Earliest Time": 1,
        "Latest Time": 1,
        "X Coordinate": 1,
    }
    keys = list(prefRank.keys())
    InfoDetail_bookName = semesterNew + " InfoDetails"
    allPlansInfoDetailPath = "./Users/" + userID + "/" + planID + "/"
    allPlansInfoDetailDict = readPlanDetailData(
        allPlansInfoDetailPath, InfoDetail_bookName, keys
    )
    allPlansDistancesDict = readTimeCoordinatesData(
        allPlansInfoDetailPath, InfoDetail_bookName
    )
    planScoreDict = getPlanScore(
        allPlansInfoDetailDict, allPlansDistancesDict, prefRank, prefDict
    )

    rankPath = "./Users/" + userID + "/" + planID + "/"
    rankName = semesterNew + " Ranking"
    # planRankList = getRankList(planScoreDict)
    rankDict = {
        k: v
        for k, v in sorted(
            planScoreDict.items(), key=lambda item: item[1], reverse=True
        )
    }
    saveRankDict(rankDict, rankPath, rankName)


def saveRankDict(dataDict, savePath, saveName):
    keys = list(dataDict.keys())
    book = xlwt.Workbook(encoding="utf-8")  # 创建workbook对象
    # 创建表单对象，cell_overwrite_ok允许单元格被覆盖
    sheet = book.add_sheet(saveName, cell_overwrite_ok=True)
    if len(keys) != 0:
        for i in range(0, len(keys)):
            sheet.write(i, 0, keys[i])
            sheet.write(i, 1, dataDict[keys[i]])
    savePath = savePath + saveName + ".xls"
    book.save(savePath)
    print("Data Ranking Saved!")


def getPlanScore(allPlansInfoDetailDict, allPlansDistancesDict, prefRank, prefDict):
    def checkOpenSeats(seatList):
        if 0 in seatList:
            return False
        else:
            return True

    def checkAverageScore(avgScore):
        userValue = prefDict["Average Score"]
        if avgScore >= userValue:
            return 1
        else:
            return 0

    def checkEarliestTime(earlyTime):
        userValue = prefDict["Earliest Time"]
        if earlyTime >= userValue:
            return 1
        else:
            return 0

    def checkLastestTime(lateTime):
        userValue = prefDict["Latest Time"]
        if lateTime <= userValue:
            return 1
        else:
            return 0

    keys = list(prefRank.keys())
    scoreDict = {}
    plan_num = -1
    for planKey in list(allPlansInfoDetailDict.keys()):
        planScore = 0
        plan_num += 1
        plan = allPlansInfoDetailDict[planKey]
        seatList = plan["Open Seats"]
        NoCheckSeats = True
        if NoCheckSeats or checkOpenSeats(seatList):
            for prefKey in list(plan.keys()):
                if prefKey == keys[0]:
                    avgScore = plan[prefKey]
                    planScore += checkAverageScore(avgScore) * prefRank[prefKey]
                elif prefKey == keys[1]:
                    earlyTime = plan[prefKey]
                    planScore += checkEarliestTime(earlyTime) * prefRank[prefKey]
                elif prefKey == keys[2]:
                    lateTime = plan[prefKey]
                    planScore += checkLastestTime(lateTime) * prefRank[prefKey]
                elif prefKey == keys[3]:
                    print(planKey)
                    coordinates = zip(
                        allPlansDistancesDict[prefKey][plan_num],
                        allPlansDistancesDict["Y Coordinate"][plan_num],
                    )
                    schedules = allPlansDistancesDict["Schedule"][plan_num]
                    planScore += (
                        checkBuildingDistance(coordinates, schedules.copy())
                        * prefRank[prefKey]
                    )
        else:
            planScore = -1
        scoreDict[planKey] = planScore

    return scoreDict


# 可以加一个parameter = user_pref_class_spread, 表示用户是否希望课程集中（课程间隔小）
# 现在default是希望课程集中
def checkBuildingDistance(coordinates, schedule, user_pref_class_spread=True):
    DAYS = ["M", "T", "W", "R", "F"]
    score = 0
    coordinates = tuple(coordinates)
    # print(schedule)

    def timeToMinutes(time, am_or_pm):
        # time is in the form 12:20
        hour, minute = time.split(":")
        if am_or_pm == "pm" and int(hour) < 12:
            hour = int(hour) + 12
        return int(hour) * 60 + int(minute)

    # schedule is in the form MW 12:20 pm-2:05 pm
    for i in range(len(schedule)):
        s = schedule[i].split("-")
        # s = (MW, 12:20, pm, 2:05, pm)
        s = s[0].split() + s[1].split()
        s = (s[0], timeToMinutes(s[1], s[2]), timeToMinutes(s[3], s[4]))
        schedule[i] = s

    day_schedule = {day: [] for day in DAYS}
    day_coordinates = {day: [] for day in DAYS}
    for i, s in enumerate(schedule):
        for day in DAYS:
            if day in s[0]:
                day_schedule[day].append((s[1], s[2]))
                day_coordinates[day].append(coordinates[i])

    for day, daily_schedule in day_schedule.items():
        score += calculate_gap_penalty(daily_schedule, user_pref_class_spread)
        score += calculate_distance_penalty(coordinates, daily_schedule)

    return score


def calculate_distance_penalty(coordinates, schedule):
    coordinates = [(float(x), float(y)) for x, y in coordinates]
    plan = sorted(zip(schedule, coordinates))
    # 17 minutes between CGS and HAR
    CGS = (42.3513682, -71.114637)
    HAR = (42.3495923, -71.0997861)

    def calc_dist(a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    COORD_PER_MINUTE = calc_dist(CGS, HAR) / 17
    penalties = 0
    for i in range(len(plan) - 1):
        distance = calc_dist(plan[i][1], plan[i + 1][1])
        dist_avail_time = COORD_PER_MINUTE * (
            # -5 because 5 minutes for getting down a building and going up to another building
            plan[i + 1][0][0]
            - plan[i][0][1]
            - 5
        )
        # if unable to make it to the next class, penalty is 3 points
        if distance > dist_avail_time:
            return -3
        else:
            # assume a maximum of 25 minutes travel per day,
            penalties += distance / (COORD_PER_MINUTE * 30)
    return -penalties


# score is gap in minutes per week divided by 1500, +- based on user pref
def calculate_gap_penalty(time_intervals, user_pref_class_spread):
    # Sort the time intervals for the day based on start times
    sorted_intervals = sorted(time_intervals, key=lambda x: x[0])

    total_gap_duration = 0
    courses_per_day = len(time_intervals) // 2

    for i in range(0, len(time_intervals) - 1):
        # Compute gap between consecutive classes
        gap = sorted_intervals[i + 1][0] - sorted_intervals[i][1]
        total_gap_duration += gap

    if len(time_intervals) > 1:
        avg_gap_duration = total_gap_duration // courses_per_day
    else:
        avg_gap_duration = 0

    # 比较差情况是每天课间差3小时，180分钟
    score = avg_gap_duration / 180

    if time_intervals:
        # to have least amount of days having class
        score += 0.5
    # user prefer classes to be together
    if user_pref_class_spread:
        return -score  # Penalty for spreading out
    else:
        return score  # Bonus for spreading out


def readPrefData(filePath, sheetName):
    dataList = {}
    book = xlrd.open_workbook(filePath)
    sheet = book.sheet_by_name(sheetName)
    rows = sheet.nrows
    cols = len(sheet.row_slice(0))
    for c in range(cols):
        try:
            noValue = bool(sheet.cell_value(2, c) == "")
        except:
            noValue = True
        if noValue:
            try:
                value = float(sheet.cell_value(1, c))
            except:
                value = sheet.cell_value(1, c)
            dataList[sheet.cell_value(0, c)] = value
        else:
            data = []
            for r in range(1, rows):
                data.append(sheet.cell_value(r, c))
            dataList[sheet.cell_value(0, c)] = data
    return dataList


def readTimeCoordinatesData(path, bookName):
    filePath = path + bookName + ".xls"
    dataList = defaultdict(list)
    book = xlrd.open_workbook(filePath)
    sheetNames = book.sheet_names()
    for sheetName in sheetNames:
        planData = {}
        sheet = book.sheet_by_name(sheetName)
        rows = sheet.nrows
        cols = sheet.ncols
        for c in range(cols):
            if sheet.cell_value(0, c) == "X Coordinate":
                dataList["X Coordinate"].append(
                    [sheet.cell_value(r, c) for r in range(1, rows)]
                )
            elif sheet.cell_value(0, c) == "Y Coordinate":
                dataList["Y Coordinate"].append(
                    [sheet.cell_value(r, c) for r in range(1, rows)]
                )
            elif sheet.cell_value(0, c) == "Schedule":
                dataList["Schedule"].append(
                    [sheet.cell_value(r, c) for r in range(1, rows)]
                )
        dataList[sheetName] = planData
    return dataList


def readPlanDetailData(path, bookName, keys):
    filePath = path + bookName + ".xls"
    dataList = {}
    book = xlrd.open_workbook(filePath)
    sheetNames = book.sheet_names()
    for sheetName in sheetNames:
        planData = {}
        sheet = book.sheet_by_name(sheetName)
        rows = sheet.nrows
        cols = sheet.ncols
        for c in range(cols):
            if sheet.cell_value(0, c) == "Open Seats":
                data = []
                for r in range(1, rows):  # 从1开始，去掉标题
                    if sheet.cell_value(r, c) == "":
                        data.append(0)
                    else:
                        data.append(int(sheet.cell_value(r, c)))

                planData[sheet.cell_value(0, c)] = data
            elif sheet.cell_value(0, c) in keys:
                planData[sheet.cell_value(0, c)] = sheet.cell_value(1, c)
        dataList[sheetName] = planData

    return dataList


if __name__ == "__main__":
    # semesterNew = "2022-FALL"  # Fall:"FALL", Summer:"SUMM", Spring:"SPRG"
    # username = "Sam"
    # AutoRanking(semesterNew, username)
    pass
