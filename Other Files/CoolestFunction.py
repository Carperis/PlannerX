import xlwt
import xlrd


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
            a = sheet.cell_value(i, 0)
            b = scores[sheet.cell_value(i, 0)]
            scores[sheet.cell_value(i, 0)] = sheet.cell_value(i, 3)

    # Use the dict to find the average of the teacher's scores
    # Doesn't count repeat teacher's names for the same class
    # Doesn't count scores of teachers with no scores
    avgscores = [-1]*len(book2.sheets())
    i = 0
    for cursheet in book2.sheets():
        sum = 0
        num = 0
        a = cursheet.nrows
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


GetAverageScores("Sam", "2022", "FALL")
