# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup  # 获取数据
import urllib.request
import urllib.error
import xlrd
import xlwt


def GetSeats(semesterNew,  userID, planID):
    prefSheetName = "Preferences"
    prefPath = "./Users/" + userID + "/" + planID + \
        "/" + semesterNew + " Preferences" + ".xls"
    courseData = readPrefData(prefPath, prefSheetName)
    sectionData = getAllSections(semesterNew.split("_")[0], courseData)
    courseScoreList = findCourseScore(sectionData, semesterNew)
    saveName = semesterNew + " Seats"
    savePath = "./Users/" + userID + "/" + planID + "/"
    saveSeatData(courseScoreList, savePath, saveName)


def getAllSections(semester, courseData):
    def readSectData(filePath, sheetName):
        dataList = []
        book = xlrd.open_workbook(filePath)
        sheet = book.sheet_by_name(sheetName)
        rows = sheet.nrows
        cols = sheet.ncols
        for r in range(1, rows):  # 从1开始，去掉标题
            course = sheetName
            section = sheet.cell_value(r, 0)
            fullName = course + " " + section
            dataList.append(fullName)
        return dataList

    sections = []
    for courCode in courseData:
        sectPath = "./Semesters/" + semester + "/" + \
            semester + " Sections/" + courCode + ".xls"
        sections += readSectData(sectPath, courCode)
    return sections


def findCourseScore(sectionData, semesterNew):
    year = int(semesterNew.split("-")[0])
    sem = semesterNew.split("-")[1]
    if (sem == "FALL"):
        sem = "Fall"
        y = str(year + 1)
        num = "3"
    elif (sem == "SPRG"):
        sem = "Spring"
        y = str(year)
        num = "4"
    elif (sem == "SUMM_1"):
        sem = "Summer"
        y = str(year+1)
        num = "1"
    elif (sem == "SUMM_2"):
        sem = "Summer"
        y = str(year+1)
        num = "2"

    courseScoreList = []
    for section in sectionData:
        A = section.split(" ")[0]
        B = section.split(" ")[1]
        C = section.split(" ")[2]
        D = section.split(" ")[3]
        url = "https://www.bu.edu/link/bin/uiscgi_studentlink.pl/1650761430?College=" + A + \
            "&Dept="+B+"&Course="+C+"&Section="+D+"&ModuleName=univschr.pl&KeySem="+y+num+"&ViewSem=" + \
            sem+"+" + \
                str(year)+"&SearchOptionCd=S&SearchOptionDesc=Class+Number&MainCampusInd="
        html = askURL(url)
        soup = BeautifulSoup(html, "html.parser")
        alltd = soup.find_all("td")  # 44,29
        result = 0
        try:
            td29 = alltd[29].find_all("font")[0].contents[0]
            try:
                td29 = int(td29.strip())
            except:
                td29 = "can't be int"
        except:
            td29 = "can't find"
        try:
            td44 = alltd[44].find_all("font")[0].contents[0]
            try:
                td44 = int(td44.strip())
            except:
                td44 = "can't be int"
        except:
            td44 = "can't find"
        if (td29 != "can't find" and td29 != "can't be int"):
            result = td29
        elif (td44 != "can't find" and td44 != "can't be int"):
            result = td44
        else:
            result = 0
        keyName = A + " " + B + " " + C + "-" + D
        data = [keyName, result]
        courseScoreList.append(data)
    return courseScoreList


def saveSeatData(dataList, savePath, saveName):
    book = xlwt.Workbook(encoding="utf-8")  # 创建workbook对象
    # 创建表单对象，cell_overwrite_ok允许单元格被覆盖
    sheet = book.add_sheet(saveName, cell_overwrite_ok=True)
    if(len(dataList) != 0):
        for i in range(0, len(dataList)):
            data = dataList[i]
            for j in range(0, len(data)):
                sheet.write(i, j, data[j])  # i+1是因为第一行已经有了标题
            # print("已保存到第%d条" % (i+1))
    savePath = savePath + saveName + ".xls"
    book.save(savePath)
    print("Data Seats Saved!")


def readPrefData(filePath, sheetName):
    dataList = []
    book = xlrd.open_workbook(filePath)
    sheet = book.sheet_by_name(sheetName)
    rows = sheet.nrows
    cols = len(sheet.row_slice(0))
    for r in range(1, rows):  # 从1开始，去掉标题
        dataList.append(sheet.cell_value(r, 0))
    return dataList


def askURL(url):  # 得到指定一个URL的网页内容
    head = {  # 模拟浏览器头部信息
        # 用户代理：表示告诉服务器我们是什么类型的机器和浏览器
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request, timeout=5)
        html = response.read().decode("utf-8")
    except Exception as e:
        print(e)
    return html


if __name__ == "__main__":
    GetSeats("2023-SPRG","1","1")
    pass
