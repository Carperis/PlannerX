import os
import itertools
from os import curdir
import re
import xlrd
from xlrd import count_records

from GetSeats import GetSeats

# a = 0
# set = [a]
# for i in range(0, 10):
#     print(a)
#     print(set)
#     a += 1

# a = 1
# b = "abc"
# print(a, b)

# coreq = "<p>Prereq: <a href=\"search.php?search=CASBI108&amp;yearsem=*&amp;college=\">CAS BI 108</a> or <a href=\"search.php?search=CASNE102&amp;yearsem=*&amp;college=\">CAS NE 102</a>; and <a href=\"search.php?search=CASCH102&amp;yearsem=*&amp;college=\">CAS CH 102</a> or equivalent.<br></p>"
# print(coreq)
# coreq = re.sub(r"<a href=\"(.*?)\">", " ", coreq)
# coreq = coreq.replace("</a>", "")
# coreq = coreq.replace("<br>", "")
# print(coreq)

# i = 1
# code = "EOP EN 095"
# print("No.%4d: %s" % (i, code))

# secNotes = "Stamped Approval<br/>Pre-req: WP700<br/>&amp; WP701 or<br/>permission of<br/>department<br/>chair.<br/>Make-up class<br/>on June 4"
# secNotes = secNotes.replace("<br/>", " ")
# secNotes = secNotes.replace(" &amp", "")
# print(secNotes)

# print(input("Enter: "))


# def getAB():
#     AB = [2, 3]
#     return AB

# [a, b] = getAB()
# print(a, b)


# a = [["abc", 2], ["def", 3]]
# a.remove(a[0])
# print(a)

# str = "a,b,c"
# print(str.split(","))

# a = []
# a.append([])
# print(a)

# def newSchdule():
#     timeRange = 24*12
#     weekRange = 7
#     schedule = []
#     oneWeek = ["Time", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
#     hours = 0
#     minutes = 0
#     for i in range(0, timeRange + 1):
#         schedule.append([])
#         for j in range(0, weekRange + 1):
#             if(i == 0):
#                 schedule[i].append(oneWeek[j])
#             else:
#                 if(j == 0):
#                     time = "%2d" % hours + ":" + "%2d" % minutes
#                     schedule[i].append(time)
#                     minutes += 5
#                     if(minutes >= 60):
#                         minutes = 0
#                         hours += 1
#                     if(hours >= 24):
#                         hours = 0
#                 else:
#                     schedule[i].append("")
#     return schedule


# def printSchedule(schedule):
#     for i in range(0, len(schedule)):
#         # print("%3d" % i, end="")
#         for j in range(0, len(schedule[0])):
#             format = "[" + schedule[i][j] + "]"
#             print(format, end="")
#         print("")


# def findIndex(day, hours, minutes):
#     if(day == "M"):
#         col = 1
#     elif(day == "T"):
#         col = 2
#     elif(day == "W"):
#         col = 3
#     elif(day == "R"):
#         col = 4
#     elif(day == "F"):
#         col = 5
#     # elif(day == "Sa"):
#     #     col = 6
#     # elif(day == "Su"):
#     #     col = 7
#     row = int(1 + (12*hours) + (minutes/5))
#     return [row, col]


# schedule = newSchdule()
# [row, col] = findIndex("M", 00, 00)
# schedule[row][col] = "Here!"
# printSchedule(schedule)


# course = [[1, 2], [3, 4, 5]]
# length = len(course)
# partLen = []
# currInd = []
# for part in course:
#     partLen.append(len(part)-1)
#     currInd.append(0)
# currInd[0] -= 1
# while(currInd != partLen):
#     # increment currInd
#     currInd[0] += 1
#     for i in range(len(currInd)):
#         if(currInd[i] > partLen[i]):
#             currInd[i] = 0
#             if((i+1) < len(currInd)):
#                 currInd[i+1] += 1
#     selected = []
#     for i in range(length):
#         selected.append(course[i][currInd[i]])
#     print(selected, currInd)


# partLen = [4, 2, 3]
# currInd = [0, 0, 0]
# while(currInd != partLen):
#     currInd[0] += 1
#     for i in range(len(currInd)):
#         if(currInd[i] > partLen[i]):
#             currInd[i] = 0
#             if((i+1) < len(currInd)):
#                 currInd[i+1] += 1
#     print(currInd)

# courses = {
#     "CAS_XX_XXX" : {
#         "LEC" :
#     }
# }

# x = [[1], []]
# print(any(x))

# x = {'a': {'a1': [1]}, 'b': {'b1': [1]}}
# print(len(x))

# x = [1, 2]
# x = x + [3, 4]
# x.append(5)
# print(x)

# x = []
# str = "123"
# x.append(str)
# print(len("123"))

# x = [1, 2]
# y = list(x)
# y[0] = 3
# print(x)
# print(y)

# print([1, 2] + [3, 4])
# print(False in [False])


# def newSchedule():  # indexChange
#     timeRange = 24*12
#     weekRange = 7
#     schedule = []
#     # oneWeek = ["Time", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
#     hours = 0
#     minutes = 0
#     for i in range(0, timeRange + 1):
#         schedule.append([])
#         for j in range(0, weekRange + 1):
#             schedule[i].append([])
#     return schedule


# def isListEmpty(inList):
#     if isinstance(inList, list):  # Is a list
#         return all(map(isListEmpty, inList))
#     return False  # Not a list


# alist = newSchedule()
# print(isListEmpty(alist))

# alist = [0] * 10
# print(alist)

# def copyLayers(layers):
#     newlayers = {}
#     for key, layer in layers.items():
#         newlayers[key] = []
#         i = 0
#         for rowList in layer:
#             newlayers[key].append([])
#             for colList in rowList:
#                 newlayers[key][i].append(colList.copy())
#             i += 1
#     return newlayers


# x = {'a': [[[1], [2]], [[3], [4]]], 'b': [[[5], [6]], [[7], [8]]]}
# y = copyLayers(x)
# y["a"][0][0][0] = 2
# print(x)
# print(x.clear())
# x = y
# print(y)

# x = {'a': []}
# print([''][0])


# print([0, 1] in [0, 2, 1])


# def clear(): return os.system('clear')


# clear()

# [a, b] = [1, 2]
# print(a, b)

# def checkFolder(savePath):
#     folders = savePath.split("/")
#     newPath = folders[0] + "/"
#     for i in range(1, len(folders)):
#         pathNotExist = bool(1 - (os.path.exists(newPath)))
#         if(pathNotExist):
#             os.mkdir(newPath)
#         newPath = newPath + folders[i] + "/"
#     print("done")


# checkFolder("./Semesters/abc/")

# xlrd.open_workbook("./Semesters/2022-FALL/2021-FALL Sections/CAS AA 103.xls")

# list = ["",""]
# list[0] = 1;
# print(list)
# a = {}
# a["a"] = 0
# a["a"]["b"]
# print(a)


# a = [1,2]
# b = [3,4]
# c = a + 0
# print(c)

# import GetSeats
# sectionData = [
#     "CAS AH 111 SB1"
# ]
# semester = "2022-SUMM"
# summTerm = "2"
# result = GetSeats.findCourseScore(sectionData, semester, summTerm)
# print(result)


# a = "END"
# print(a.split("_"))

import pdf2image
image = pdf2image.convert_from_path("./static/schedule.pdf")[0]
image.save("./static/schedule.png")