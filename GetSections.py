# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup  # 获取数据
import re  # 正则表达式，文字匹配
import urllib.request
import urllib.error  # 定制url
import xlwt
import xlrd  # excel操作
import os
import sqlite3  # SQL数据库操作


def GetSections(semester):
    filePath = "./" + semester + "/BU Courses " + semester + ".xls"
    dataList = readData(filePath, semester)
    start = 0
    end = len(dataList)
    for i in range(start, end):
        data = dataList[i]
        code = data[0]
        secURL = data[1]
        print("No.%4d / %4d: %s" % (i, end-1, code))
        print(secURL)
        getAndSaveSections(secURL, code, semester)


def readData(filePath, semester):
    dataList = []
    sheetName = "BU Courses " + semester
    book = xlrd.open_workbook(filePath)
    sheet = book.sheet_by_name(sheetName)
    rows = sheet.nrows
    cols = sheet.ncols
    for c in range(cols):
        if(str(sheet.cell_value(0, c)) == "Code"):
            codeIndex = c
        if(str(sheet.cell_value(0, c)) == "Link"):
            URLIndex = c
    for r in range(1, rows):
        data = []
        data.append(sheet.cell_value(r, codeIndex))
        data.append(sheet.cell_value(r, URLIndex))
        dataList.append(data)
    return dataList


def getAndSaveSections(secURL, code, semester):
    dataList = []
    try:
        html = askURL(secURL)
    except Exception as e:
        html = askURL(secURL)
    soup = BeautifulSoup(html, "html.parser")
    soup = soup.find_all('div', class_="coursearch-course-section")
    if(not soup):
        return ""
    for item in soup:
        str1 = str(item.find_all('h4')[0]).lower()
        str2 = semester.lower().split("-")[1]
        str2 = str2[0:3]
        if(str2 in str1):
            itemList = item.find_all('tr')
            if(len(itemList) != 0):
                for i in range(1, len(itemList)):
                    # for i in range(1, 3):
                    data = []
                    itemStr = str(itemList[i])
                    info1 = re.findall(
                        r'<td rowspan="[\d]">(.*?)</td>', itemStr)
                    info2 = re.findall(r'<td>(.*?)</td>', itemStr)
                    if(len(info1) == 0):
                        info1 = ["", "", ""]
                    print(info1)
                    print(info2)
                    # 获取SectionID
                    secID = info1[0].strip()
                    data.append(secID)
                    # 获取开放人数
                    secNum = re.findall(
                        r'<span class="open-seats">(.*?)</span>', itemStr)
                    if(len(secNum) == 0):
                        secNum = [""]
                    data.append(secNum[0])
                    # 获取老师名称
                    teachter = info1[1].strip()
                    data.append(teachter)
                    # 获取Section类型
                    secType = info2[0].strip()
                    data.append(secType)
                    # 获取上课地点
                    location = info2[1].strip()
                    data.append(location)
                    # 获取上课时间
                    secTime = info2[2].strip()
                    data.append(secTime)
                    # 获取上课日期
                    secDate = info2[3].strip()
                    data.append(secDate)
                    # 获取备注
                    secNotes = info1[2].strip()
                    secNotes = secNotes.replace("<br/>", " ")
                    secNotes = secNotes.replace(" &amp", "")
                    data.append(secNotes)
                    # 获取学期
                    secSemester = str1.replace("<h4>", "")
                    secSemester = secSemester.replace("</h4>", "")
                    data.append(secSemester)

                    dataList.append(data)

    dataList = fixSections(dataList)

    savePath = "./" + semester + "/" + semester + " Sections/"
    saveName = code
    firstRow = ("Section", "Open Seats", "Instructor", "Type", "Location",
                "Schedule", "Dates", "Notes", "Semester")
    pathNotExist = bool(1 - (os.path.exists(savePath)))
    if(pathNotExist):
        os.mkdir(savePath)
    saveData(dataList, savePath, saveName, firstRow)
    print("")


def fixSections(dataList):
    temp = []
    for i in range(len(dataList)):
        if(dataList[i][3] == ""):
            newSchedule = "," + dataList[i][5]
            temp[temp.index(realSection)][5] += newSchedule
        elif(~(dataList[i][3] == "") & (dataList[i][0] == "")):
            realSection = dataList[i]
            section = dataList[i]
            section[0] = dataList[i-1][0]
            temp.append(section)
        else:
            realSection = dataList[i]
            temp.append(dataList[i])
    return temp


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
    # except urllib.error.URLError as e:
    #     if hasattr(e, "code"):
    #         print(e.code)
    #     if hasattr(e, "reason"):
    #         print(e.reason)
    except Exception as e:
        print(e)
    return html


def saveData(dataList, savePath, saveName, firstRow):
    book = xlwt.Workbook(encoding="utf-8")  # 创建workbook对象
    # 创建表单对象，cell_overwrite_ok允许单元格被覆盖
    sheet = book.add_sheet(saveName, cell_overwrite_ok=True)
    for i in range(0, len(firstRow)):
        sheet.write(0, i, firstRow[i])

    if(len(dataList) != 0):
        for i in range(0, len(dataList)):
            data = dataList[i]
            for j in range(0, len(data)):
                sheet.write(i+1, j, data[j])  # i+1是因为第一行已经有了标题
            # print("已保存到第%d条" % (i+1))
    savePath = savePath + saveName + ".xls"
    book.save(savePath)
    print("Data Saved!")
    # 3.保存数据


if __name__ == "__main__":
    semester = "2022-SPRG"  # Fall:"FALL", Summer:"SUMM", Spring:"SPRG"
    GetSections(semester)
    # semester = "2021-SUMM"
    # secURL = "https://www.bu.edu/phpbin/course-search/section/?t=eopbs011&amp;semester=" + semester + \
    #     "&amp;return=%2Fphpbin%2Fcourse-search%2Fsearch.php%3Fpage%3D0%26pagesize%3D100%26adv%3D1%26nolog%3D%26search_adv_all%3D%26yearsem_adv%3D2021-SUMM%26credits%3D%2A%26hub_match%3Dall%26pagesize%3D100%22"
    # code = "EOP BS 011"
    # getAndSaveSections(secURL, code, semester)
