
import xlrd
import xlwt


def AutoRanking(semesterNew, username):
    prefSheetName = "Preferences"
    prefPath = "./User/" + username + "/" + \
        semesterNew + " Preferences " + username + ".xls"
    prefDict = readPrefData(prefPath, prefSheetName)

    prefRank = {  # key: a certain preference, value: weight(importance) of this preference (1 is lowest)
        "Average Score": 1,
        "Earliest Time": 1,
        "Latest Time": 1
    }
    keys = list(prefRank.keys())
    InfoDetail_bookName = semesterNew + " " + username + " " + "InfoDetails"
    allPlansInfoDetailPath = "./User/" + username + "/"
    allPlansInfoDetailDict = readPlanDetailData(
        allPlansInfoDetailPath, InfoDetail_bookName, keys)
    planScoreDict = getPlanScore(allPlansInfoDetailDict, prefRank, prefDict)

    rankPath = "./User/" + username + "/"
    rankName = semesterNew + " " + username + " Ranking"
    # planRankList = getRankList(planScoreDict)
    rankDict = {k: v for k, v in sorted(
        planScoreDict.items(), key=lambda item: item[1], reverse=True)}
    saveRankDict(rankDict, rankPath, rankName)


def saveRankDict(dataDict, savePath, saveName):
    keys = list(dataDict.keys())
    book = xlwt.Workbook(encoding="utf-8")  # 创建workbook对象
    # 创建表单对象，cell_overwrite_ok允许单元格被覆盖
    sheet = book.add_sheet(saveName, cell_overwrite_ok=True)
    if(len(keys) != 0):
        for i in range(0, len(keys)):
            sheet.write(i, 0, keys[i])
            sheet.write(i, 1, dataDict[keys[i]])
    savePath = savePath + saveName + ".xls"
    book.save(savePath)
    print("Data Ranking Saved!")


def getPlanScore(allPlansInfoDetailDict, prefRank, prefDict):
    def checkOpenSeats(seatList):
        if (0 in seatList):
            return False
        else:
            return True

    def checkAverageScore(avgScore):
        userValue = prefDict["Average Score"]
        if (avgScore >= userValue):
            return 1
        else:
            return 0

    def checkEarliestTime(earlyTime):
        userValue = prefDict["Earliest Time"]
        if (earlyTime >= userValue):
            return 1
        else:
            return 0

    def checkLastestTime(lateTime):
        userValue = prefDict["Latest Time"]
        if (lateTime <= userValue):
            return 1
        else:
            return 0

    keys = list(prefRank.keys())
    scoreDict = {}
    for planKey in list(allPlansInfoDetailDict.keys()):
        planScore = 0
        plan = allPlansInfoDetailDict[planKey]
        seatList = plan["Open Seats"]
        NoCheckSeats = True
        if (NoCheckSeats or checkOpenSeats(seatList)):
            for prefKey in list(plan.keys()):
                if (prefKey == keys[0]):
                    avgScore = plan[prefKey]
                    planScore += checkAverageScore(avgScore) * \
                        prefRank[prefKey]
                elif (prefKey == keys[1]):
                    earlyTime = plan[prefKey]
                    planScore += checkEarliestTime(earlyTime) * \
                        prefRank[prefKey]
                elif (prefKey == keys[2]):
                    lateTime = plan[prefKey]
                    planScore += checkLastestTime(lateTime) * prefRank[prefKey]
        else:
            planScore = -1
        scoreDict[planKey] = planScore
    return scoreDict


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
        if (noValue):
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
            if (sheet.cell_value(0, c) == "Open Seats"):
                data = []
                for r in range(1, rows):  # 从1开始，去掉标题
                    if (sheet.cell_value(r, c) == ""):
                        data.append(0)
                    else:
                        data.append(int(sheet.cell_value(r, c)))

                planData[sheet.cell_value(0, c)] = data
            elif (sheet.cell_value(0, c) in keys):
                planData[sheet.cell_value(0, c)] = sheet.cell_value(1, c)
        dataList[sheetName] = planData
    return dataList


if __name__ == "__main__":
    semesterNew = "2022-FALL"  # Fall:"FALL", Summer:"SUMM", Spring:"SPRG"
    username = "Sam"
    AutoRanking(semesterNew, username)
