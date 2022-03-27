# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup  # 获取数据
import re  # 正则表达式，文字匹配
import urllib.request
import urllib.error  # 定制url
import xlwt  # excel操作
import os
import sqlite3  # SQL数据库操作


def GetCourses(semester):
    baseURL = ["https://www.bu.edu/phpbin/course-search/search.php?page=", "&pagesize=", "&adv=",
               "&nolog=", "&search_adv_all=", "&yearsem_adv=", "&credits=", "&hub_match=", "&pagesize="]
    dataList = getData(baseURL, semester)

    savePath = "./" + semester + "/"
    pathNotExist = bool(1 - (os.path.exists(savePath)))
    if(pathNotExist):
        os.mkdir(savePath)
    saveName = "BU Courses " + semester
    firstRow = ("Code", "Name", "Prerequisite", "Corequisite", "Intro", "Credits", "Hub Unit 1",
                "Hub Unit 2", "Hub Unit 3", "Hub Unit 4", "Link")
    saveData(dataList, savePath, saveName, firstRow)


findCode = re.compile(r'<h6>(.*?)</h6>')
findName = re.compile(r'<h2>(.*?)</h2>')
findInfoList = re.compile(r'<p>.*?</p>')
findInfo = re.compile(r'<p>(.*?)</p>')
findCred = re.compile(r'<p>\[(.*?)cr.\]</p>')
findUnit = re.compile(r'<li>(.*?)</li>')
findSec = re.compile(
    r'<a class="coursearch-result-sections-link" href="(.*?)>')


def getData(baseURL, semester):
    lastPage = False
    page = 0
    pagesize = 100
    adv = 1
    nolog = ""
    search_adv_all = ""
    yearsem_adv = semester
    credits = "*"
    hub_match = "all"
    dataList = []
    while(~lastPage):
        parameter = [page, pagesize, adv, nolog, search_adv_all,
                     yearsem_adv, credits, hub_match, pagesize]
        url = formURL(baseURL, parameter)
        # print(url)
        html = askURL(url)
        soup = BeautifulSoup(html, "html.parser")
        itemList = soup.find_all('li', class_="coursearch-result")
        if(len(itemList) == 0):
            lastPage = True
            break
        print("Page: %3d Item: %4d " % (page + 1, len(itemList)), end="")
        for item in itemList:
            data = []
            itemStr = str(item)

            # 获得课程代码
            code = re.findall(findCode, itemStr)[0]
            data.append(code)

            # 获得课程名称
            name = re.findall(findName, itemStr)[0]
            data.append(name)

            infoList = re.findall(findInfoList, itemStr)
            # 获取Prerequisite
            prereq = re.findall(findInfo, str(infoList[0]))[0]
            prereq = re.sub(r"<a href=\"(.*?)\">", " ", prereq)
            prereq = prereq.replace("Prereq: ", "")
            prereq = prereq.replace("</a>", "")
            prereq = prereq.replace("<br>", "")
            prereq = prereq.replace("<br/>", "")
            data.append(prereq.strip())
            # 获取Corequisite
            coreq = re.findall(findInfo, str(infoList[2]))[0]
            coreq = re.sub(r"<a href=\"(.*?)\">", "", coreq)
            coreq = coreq.replace("Coreq: ", "")
            coreq = coreq.replace("</a>", "")
            coreq = coreq.replace("<br>", "")
            coreq = coreq.replace("<br/>", "")
            data.append(coreq.strip())
            # 获得课程介绍
            intro = re.findall(findInfo, str(infoList[4]))[0]
            data.append(intro.strip())

            # 获得课程学分
            cred = re.findall(findCred, itemStr)[0]
            data.append(cred.strip())

            # 获得课程Hub Units
            unit = re.findall(findUnit, itemStr)
            maxUnit = 4
            for i in range(len(unit)):
                data.append(unit[i])
            for i in range(maxUnit-len(unit)):
                data.append("")

            # 获得课程Sections
            if(len(re.findall(findSec, itemStr)) > 0):
                secURL = re.findall(findSec, itemStr)[0]
                secURL = "https://www.bu.edu" + secURL
            else:
                secURL = ""
            data.append(secURL.strip())

            dataList.append(data)
            print(">", end="")
        page += 1
        print("")
    return dataList


def formURL(baseURL, parameter):
    url = ""
    for i in range(0, len(parameter)):
        url += baseURL[i] + str(parameter[i])
    return url


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
    GetCourses(semester)
    # getAndSaveSections("https://www.bu.edu/phpbin/course-search/section/?t=casaa103&amp;semester=2021-SUMM&amp;return=%2Fphpbin%2Fcourse-search%2Fsearch.php%3Fpage%3D0%26pagesize%3D100%26adv%3D1%26nolog%3D%26search_adv_all%3D%26yearsem_adv%3D2021-SUMM%26credits%3D%2A%26hub_match%3Dall%26pagesize%3D100", "CAS AA 103", "2021-SUMM")
