import os
import xlrd
import pdfscheduler
from datetime import datetime
# import pdf2image
from reportlab.lib.colors import black
import fitz
import GetPreferenceWeb


def convertTime(time):
    miltime = ""
    if time[-2:] == "am":
        if time[:2] == "12":
            miltime = str('00' + time[2:8])
        else:
            miltime = time[:-2]
    else:
        if time[:2] == "12":
            miltime = time[:-2]
        else:
            miltime = str(
                int(time.split(':')[0]) + 12) + ":" + time.split(":")[1][0:-2]

    return miltime


def convertDays(days):
    newDays = []
    for i in range(0, len(days)):
        if (days[i] == "M"):
            newDays.append("Monday")
        elif (days[i] == "T"):
            newDays.append("Tuesday")
        elif (days[i] == "W"):
            newDays.append("Wednesday")
        elif (days[i] == "R"):
            newDays.append("Thursday")
        elif (days[i] == "F"):
            newDays.append("Friday")
    return newDays


def GetSchedulePic(semesterNew, userID, planID, planName):
    path = "./Users/" + userID + "/" + planID + "/" + semesterNew + " Info.xls"
    book = xlrd.open_workbook(path)
    sheet = book.sheet_by_name(planName)

    schedu = pdfscheduler.Schedule(
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    colors = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0], [0, 1, 1], [1, 0, 1], [1, 0.5, 0.5], [1, 0.5, 0], [0.5, 1, 0], [0.5, 0.5, 1], [
        0.5, 0, 1], [0.5, 1, 0.5], [0, 1, 0.5], [0, 0.5, 1], [1, 0.5, 1], [1, 0, 0.5], [0, 0.5, 0], [0.5, 0, 0], [0, 0, 0.5], [0.5, 0.5, 0.5]]
    for i in range(1, sheet.nrows):
        times = sheet.cell_value(i, 5).split(",")
        for time in times:
            out = time.split()
            out2 = out[2].split('-')
            schedu.add_event(pdfscheduler.Event(datetime.strptime(out[1] + out2[0], '%I:%M%p').time(), datetime.strptime(out2[1] + out[3], '%I:%M%p').time(), [sheet.cell_value(
                i, 9), sheet.cell_value(i, 3) + " " + convertTime(out[1] + out2[0]) + "-" + convertTime(out2[1] + out[3]), sheet.cell_value(i, 0)], colors[i], convertDays(out[0])))

    path = "./static/Users/" + userID + "/" + planID + "/"
    outfile_pdf = "./static/Users/" + userID + "/" + planID + "/schedule.pdf"
    outfile_img = "./static/Users/" + userID + "/" + planID + "/schedule.png"
    GetPreferenceWeb.checkFolder(path)
    c = pdfscheduler.Canvas(outfile_pdf, (800, 600))
    # c.setFillColorRGB(1, 1, 1) # set background color to white
    # c.setStrokeColorRGB(1, 1, 1) # set border color to white
    c.setFont("Helvetica", 20)

    pwidth = 800
    pheight = 600
    inch = 20
    schedu.render(
        c,
        x=inch,
        y=pheight - inch,
        width=pwidth - 2 * inch,
        height=pheight - 2 * inch,
        font_size=14,
        show_times=True
    )

    try:
        os.remove(outfile_pdf)
        os.remove(outfile_img)
    except:
        pass

    c.setFillColor(black)
    c.save()
    doc = fitz.open(outfile_pdf)
    for page in doc:
        pix = page.get_pixmap(alpha=True)
        pix.save(outfile_img)


if __name__ == "__main__":
    # semesterNew = "2022-SPRG"  # Fall:"FALL", Summer:"SUMM", Spring:"SPRG"
    # username = "Sam2"
    # planName = "Plan 1"
    # GetSchedulePic(semesterNew, username, planName)
    userID = '1'
    planID = '1'
    planName = 'Plan 1'
    semester = '2023-FALL'
    GetSchedulePic(semester, userID, planID, planName)
    # pass
