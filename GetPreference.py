# -*- coding: utf-8 -*-

import xlwt


def GetPreference(saveName):
    dataList = getData()
    savePath = "./"
    firstRow = ["Code", "Sections", "Same Teacher", ]
    saveData(dataList, savePath, saveName, firstRow)


def getData():
    print("Please provide your course preference")
    dataList = []
    courseNum = 1
    while(True):
        data = []
        print("")
        ans = input("Continue? y/n: ")
        if(ans == "y"):
            # 获取课程代码
            code = input("What is Course %d code: " % courseNum)
            data.append(code)

            # 获取课程种类
            scores = input(
                "What kinds of section does Course %d have: " % courseNum)
            data.append(scores)

            # 获取同教师Sections
            sections = input(
                "What sections above will be taught by the same teacher: " % courseNum)
            data.append(sections)

            print("Get your course %d data!" % courseNum)
            dataList.append(data)
            courseNum += 1
        elif(ans == "n"):
            break
        else:
            continue
    return dataList


def saveData(dataList, savePath, saveName, firstRow):
    book = xlwt.Workbook(encoding="utf-8")  # 创建workbook对象
    # 创建表单对象，cell_overwrite_ok允许单元格被覆盖
    sheetName = "My Preference"
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
    prefName = "My Preference"
    GetPreference(prefName)
