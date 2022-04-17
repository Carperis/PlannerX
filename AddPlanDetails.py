
import pandas as pd
import xlwt
import xlrd


def AddPlanDetails(semester, prefName):
    Info_bookName = semester + " " + username + " " + "Info"
    allPlansInfoPath = "./User/" + username + "/"
    allPlansInfoDict = readPlanData(allPlansInfoPath)


def readPlanData(path, bookName):
    filePath = path + bookName
    dataList = {}
    book = xlrd.open_workbook(filePath)
    sheet = book.sheet_by_name(sheetName)
    rows = sheet.nrows
    cols = sheet.ncols
    for r in range(1, rows):  # 从1开始，去掉标题
        data = []
        for c in range(cols):
            data.append(sheet.cell_value(r, c))
        data.append(sheetName)
        dataList.append(data)
    return dataList


def GetAverageScores(name, year, semester):

    # Initialize dictionary for teacher scores
    scores = {"Staff": -1}

    #name = "Sam"
    #year = "2022"
    #semester = "FALL"

    # Set pathway for teachers scores sheet
    sheetName = "BU Teachers Scores"
    path = "./Semesters/" + sheetName + ".xls"
    book = xlrd.open_workbook(path)
    sheet = book.sheet_by_name(sheetName)

    # Set pathway for student preference info sheet
    path2 = "./User/" + name + "/" + year + \
        "-" + semester + " " + name + " Info.xls"
    book2 = xlrd.open_workbook(path2)
    sheet2 = book2.sheet_by_name("Plan1")

    # Fill dictionary with teacher's names initially pointing to -1
    for cursheet in book2.sheets():
        for row in range(1, sheet2.nrows):
            if cursheet.cell_value(row, 2) not in scores:
                scores[cursheet.cell_value(row, 2)] = -1

    # Pair the teacher's scores with their scores
    for i in range(1, sheet.nrows):
        if sheet.cell_value(i, 0) in scores and scores[sheet.cell_value(i, 0)] == -1:
            scores[sheet.cell_value(i, 0)] = sheet.cell_value(i, 3)

    # Use the dict to find the average of the teacher's scores
    # Doesn't count repeat teacher's names for the same class
    # Doesn't count scores of teachers with no scores
    avgscores = [-1]*len(book2.sheets())
    i = 0
    for cursheet in book2.sheets():
        sum = 0
        num = 0
        for row in range(1, cursheet.nrows):
            # To be edited: Currently, this only doesn't count repeat teachers of the same class if the PREVIOUS row has the same teacher and class
            # Doesnt work if there are more than 2 sections of a class (Like if it has a lecture, discussion, and lab would count same prof twice if same prof for lec and lab)
            if (cursheet.cell_value(row, 9) != cursheet.cell_value(row - 1, 9)) or (cursheet.cell_value(row, 9) == cursheet.cell_value(row - 1, 9) and cursheet.cell_value(row, 2) != cursheet.cell_value(row-1, 2)):
                if scores[cursheet.cell_value(row, 2)] != -1:
                    sum += scores[cursheet.cell_value(row, 2)]
                    num = num+1
        avgscores[i] = sum / num
        i = i+1

    print(avgscores)
    return avgscores


# GetAverageScores("Sam", "2022", "FALL")


def timeExtrema(filename):
    # read file to get schedule
    df = pd.read_excel(filename, None, usecols=[5])
    # initialized var
    startMax = 24
    endMin = 0
    for j in range(len(df)):
        name = 'Plan' + str(j+1)
        for i in range(df[name].shape[0]):
            a = df[name].loc[i].at["Schedule"]
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
    print("max is: ", hour1, ':', minute1,
          when1, " ", hour2, ':', minute2, when2)
    timeExteme = [startMax, endMin]
    return timeExteme

# test
# name = 'Results/2022-FALL_My Preference F22_v2_Info.xls'
# timeExtrema(name)


if __name__ == "__main__":
    semester = "2022-SPRG"  # Fall:"FALL", Summer:"SUMM", Spring:"SPRG"
    username = "Sam"
    AddPlanDetails(semester, username)
