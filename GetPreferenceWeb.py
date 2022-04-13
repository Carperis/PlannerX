# -*- coding: utf-8 -*-
import os
import xlwt


def GetPreference(username, dataList):
    savePath = "./User/" + username + "/"
    checkFolder(savePath)
    firstRow = ["Course"]
    saveName = "Preferences " + username
    saveData(dataList, savePath, saveName, firstRow)


def checkFolder(savePath):
    folders = savePath.split("/")
    newPath = folders[0] + "/"
    for i in range(1, len(folders)):
        pathNotExist = bool(1 - (os.path.exists(newPath)))
        if(pathNotExist):
            os.mkdir(newPath)
        newPath = newPath + folders[i] + "/"


def saveData(dataList, savePath, saveName, firstRow):
    book = xlwt.Workbook(encoding="utf-8")  # 创建workbook对象
    sheetName = "Preferences"
    sheet = book.add_sheet(sheetName, cell_overwrite_ok=True)
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
    username = "Sam"
    dataList = [["ENG EC 327"], ["ENG EC 311"]]
    GetPreference(username, dataList)
