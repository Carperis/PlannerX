# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup  # 获取数据
import re  # 正则表达式，文字匹配
import urllib.request
import urllib.error  # 定制url
import xlwt  # excel操作
import json
import os


def GetTeachersScores():
    baseURL = ["https://solr-aws-elb-production.ratemyprofessors.com//solr/rmp/select/?solrformat=true&rows=",
               "&wt=json&json.wrf=noCB&callback=noCB&q=*%3A*+AND+schoolid_s%3A", "&defType=edismax&qf=teacherfirstname_t%5E2000+teacherlastname_t%5E2000+teacherfullname_t%5E2000+autosuggest&bf=pow(total_number_of_ratings_i%2C2.1)&sort=total_number_of_ratings_i+desc&siteName=rmp&rows=20&start=", "&fl=pk_id+teacherfirstname_t+teacherlastname_t+total_number_of_ratings_i+averageratingscore_rf+schoolid_s&fq="]
    dataList = getData(baseURL)
    savePath = "./Semesters/"
    checkFolder(savePath)
    saveData(dataList, savePath)


def checkFolder(savePath):
    folders = savePath.split("/")
    newPath = folders[0] + "/"
    for i in range(1, len(folders)):
        pathNotExist = bool(1 - (os.path.exists(newPath)))
        if(pathNotExist):
            os.mkdir(newPath)
        newPath = newPath + folders[i] + "/"


def getData(baseURL):
    lastPage = False
    dataList = []
    schoolID = 124  # BU school id in RMP
    itemNum = 1000
    itemStart = 0
    while(~lastPage):
        parameter = [itemNum, schoolID, itemStart]
        url = formURL(baseURL, parameter)
        html = askURL(url)
        data = re.findall(r'noCB\((\{.*?\})\)', html)
        jsonObj = json.loads(data[0])
        if(len(jsonObj["response"]["docs"]) == 0):
            lastPage = True
            break
        for item in jsonObj["response"]["docs"]:
            item = dict(item)
            itemData = []

            # 获取老师姓名
            teacherName = item["teacherfirstname_t"] + \
                " " + item["teacherlastname_t"]
            itemData.append(teacherName)

            # 获取老师ID
            itemData.append(item["pk_id"])

            # 获取学校ID
            itemData.append(item["schoolid_s"])

            # 获取老师评分
            if(("averageratingscore_rf" in item.keys()) & (item["total_number_of_ratings_i"] > 0)):
                itemData.append(item["averageratingscore_rf"])
            else:
                itemData.append("NS")  # NS = No Scores

            # 获取评分人数
            itemData.append(item["total_number_of_ratings_i"])

            dataList.append(itemData)
            print(len(dataList), itemData)
        itemStart += itemNum
    return dataList


def formURL(baseURL, parameter):
    url = ""
    lenUrl = len(baseURL)
    lenPara = len(parameter)
    for i in range(0, abs(lenUrl - lenPara)):
        parameter.append("")
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


def saveData(dataList, savePath):
    book = xlwt.Workbook(encoding="utf-8")  # 创建workbook对象
    # 创建表单对象，cell_overwrite_ok允许单元格被覆盖
    saveName = "BU Teachers Scores"
    sheet = book.add_sheet(saveName, cell_overwrite_ok=True)
    firstRow = ("TeacherName", "TeacherID", "SchoolID", "Scores", "Reviews")
    for i in range(0, len(firstRow)):
        sheet.write(0, i, firstRow[i])
    for i in range(0, len(dataList)):
        data = dataList[i]
        for j in range(0, len(data)):
            sheet.write(i+1, j, data[j])  # i+1是因为第一行已经有了标题
        # print("已保存到第%d条" % (i+1))
    savePath = savePath + saveName + ".xls"
    book.save(savePath)
    print("Data saved!")

    # 3.保存数据
if __name__ == "__main__":
    GetTeachersScores()
