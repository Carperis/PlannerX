# -*- coding: utf-8 -*-
import requests
import re  # 正则表达式，文字匹配
import xlwt  # excel操作
import json
import os


def GetTeachersScores():
    url = "https://www.ratemyprofessors.com/graphql"
    dataList = getData(url)
    print(len(dataList))
    cleanData(dataList)
    print(len(dataList))
    savePath = "./Semesters/"
    checkFolder(savePath)
    saveData(dataList, savePath)

def cleanData(dataList):
    indices_to_delete = []
    for i in range(len(dataList) - 1, 0, -1):
        current_id = dataList[i][1]
        prior_id = dataList[i - 1][1]
        if current_id == prior_id:
            indices_to_delete.append(i)

    # Iterate through indices_to_delete in reverse order and delete elements
    for index in indices_to_delete:
        del dataList[index]


def checkFolder(savePath):
    folders = savePath.split("/")
    newPath = folders[0] + "/"
    for i in range(1, len(folders)):
        pathNotExist = bool(1 - (os.path.exists(newPath)))
        if (pathNotExist):
            os.mkdir(newPath)
        newPath = newPath + folders[i] + "/"


def getData(url):
    dataList = []
    itemNum = 1999
    cursor = "" # initial cursor
    while (True):
        response = askURL(url, itemNum, cursor)
        jsonObj = json.loads(response)
        numTeachers = len(jsonObj["data"]["search"]["teachers"]["edges"])
        for item in jsonObj["data"]["search"]["teachers"]["edges"]:
            cursor = item["cursor"]
            item = dict(item)["node"]
            itemData = []

            # 获取老师姓名
            teacherName = item["firstName"] + \
                " " + item["lastName"]
            itemData.append(teacherName)

            # 获取老师ID
            itemData.append(item["id"])

            # 获取学校ID
            itemData.append(item["school"]["id"])

            # 获取老师评分
            if (("avgRating" in item.keys()) & (item["numRatings"] > 0)):
                itemData.append(item["avgRating"])
            else:
                itemData.append("NS")  # NS = No Scores

            # 获取评分人数
            itemData.append(item["numRatings"])

            dataList.append(itemData)
            print(len(dataList), itemData)
        if (numTeachers < itemNum):
            print("All teachers' scores have been collected!")
            break
    return dataList


def askURL(url, itemNum, cursor):

    request_body = {
        "query": "query TeacherSearchPaginationQuery(\n  $count: Int!\n  $cursor: String\n  $query: TeacherSearchQuery!\n) {\n  search: newSearch {\n    ...TeacherSearchPagination_search_1jWD3d\n  }\n}\n\nfragment TeacherSearchPagination_search_1jWD3d on newSearch {\n  teachers(query: $query, first: $count, after: $cursor) {\n    didFallback\n    edges {\n      cursor\n      node {\n        ...TeacherCard_teacher\n        id\n        __typename\n      }\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n    resultCount\n    filters {\n      field\n      options {\n        value\n        id\n      }\n    }\n  }\n}\n\nfragment TeacherCard_teacher on Teacher {\n  id\n  legacyId\n  avgRating\n  numRatings\n  ...CardFeedback_teacher\n  ...CardSchool_teacher\n  ...CardName_teacher\n  ...TeacherBookmark_teacher\n}\n\nfragment CardFeedback_teacher on Teacher {\n  wouldTakeAgainPercent\n  avgDifficulty\n}\n\nfragment CardSchool_teacher on Teacher {\n  department\n  school {\n    name\n    id\n  }\n}\n\nfragment CardName_teacher on Teacher {\n  firstName\n  lastName\n}\n\nfragment TeacherBookmark_teacher on Teacher {\n  id\n  isSaved\n}\n",
        "variables": {
            "count": itemNum,
            "cursor": cursor,
            "query": {
                "text": "",
                "schoolID": "U2Nob29sLTEyNA==",
                "fallback": True,
                "departmentID": None
            }
        }
    }
    
    if cursor == "":
        del request_body["variables"]["cursor"]
    
    request_body_string = json.dumps(request_body)
    request_body_string = request_body_string.replace("\": ", "\":")
    request_body_string = request_body_string.replace(", \"", ",\"")
    body_length = len(request_body_string)
    
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh,en;q=0.9,zh-CN;q=0.8",
        "Authorization": "Basic dGVzdDp0ZXN0",
        "Connection": "keep-alive",
        "Content-Length": str(body_length),
        "Content-Type": "application/json",
        "Cookie": "ccpa-notice-viewed-02=true; userSchoolId=U2Nob29sLTEyNA==; userSchoolLegacyId=124; userSchoolName=Boston%20University; cid=FIPBWsE7uE-20230830",
        "Host": "www.ratemyprofessors.com",
        "Origin": "https://www.ratemyprofessors.com",
        "Referer": "https://www.ratemyprofessors.com/search/professors/124?q=",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"'
    }

    response = requests.post(url, json=request_body, headers=headers)
    if response.status_code == 200:
        print("Request successful!")
    else:
        raise Exception("Request failed with status code:", response.status_code)
    
    return response.text



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
