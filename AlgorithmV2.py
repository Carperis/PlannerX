# -*- coding: utf-8 -*-

import re


def autoMatchCourses(prepData, SameTeacherDict):
    SameTeacherSect = getSameTeacherSections(prepData, SameTeacherDict)
    sectList = getSectList(prepData)  # ['CAS CH 131,LEC' ...]
    scheduleLayers = getScheduleLayers(sectList, prepData)
    numSect = len(sectList)
    allPlans = getPlans(scheduleLayers, numSect, sectList, SameTeacherSect)
    return allPlans


def getSameTeacherSections(prepData, SameTeacherDict):
    def getTeachers(sectDict):
        teachers = []
        for type, sections in sectDict.items():
            for section in sections:
                if (not section[2] in teachers and section[2] != "Staff"):
                    teachers.append(section[2])
        return teachers

    SameTeacherSect = {}
    for course, types in SameTeacherDict.items():
        if (types[0] != ''):
            teachers = getTeachers(prepData[course])
            SameTeacherSect[course] = {}
            for teacher in teachers:
                SameTeacherSect[course][teacher] = []
                for type in types:
                    if (type in list(prepData[course].keys())):
                        for section in prepData[course][type]:
                            if (section[2] == teacher):
                                sectName = section[0] + "-" + \
                                    section[len(
                                        section)-1] + "," + section[3]  # this must be same as section names in scheduleLayers
                                SameTeacherSect[course][teacher].append(
                                    sectName)
    return SameTeacherSect


def getSectOfLayer(layer):
    sections = {}
    for c in range(1-1, len(layer[0])):
        for r in range(1-1, len(layer)):
            for i in layer[r][c]:
                if (any(i)):
                    if (i in sections):
                        sections[i].append([r, c])
                    else:
                        sections[i] = [[r, c]]
    return sections


def getRemoveList(layers, times, SameTeacherSect, section):
    removeList = []

    course = section.split('-')[1].split(',')[0]
    if (course in list(SameTeacherSect.keys())):
        thisTeacher = ''
        for teacher, sectList in SameTeacherSect[course].items():
            if (section in sectList):
                thisTeacher = teacher
        for teacher, sectList in SameTeacherSect[course].items():
            if (teacher != thisTeacher):
                removeList += sectList

    for sectName, layer in layers.items():
        for time in times:
            if (any(layer[time[0]][time[1]])):
                for sect in layer[time[0]][time[1]]:
                    if ((sect in removeList) == False):
                        removeList.append(sect)
    return removeList


def removeSections(layers, removeList):
    newLayers = layers.copy()
    for sectName, layer in layers.items():
        for c in range(1-1, len(layer[0])):
            for r in range(1-1, len(layer)):
                removeItems = []
                for i in layer[r][c]:
                    if (i in removeList):
                        # layer[r][c].remove(i)
                        removeItems.append(i)
                for i in removeItems:
                    newLayers[sectName][r][c].remove(i)
    return newLayers


def removeEmptyLayers(layers):
    # see https://stackoverflow.com/questions/1593564/python-how-to-check-if-a-nested-list-is-essentially-empty
    def isListEmpty(inList):
        if isinstance(inList, list):  # Is a list
            return all(map(isListEmpty, inList))
        return False  # Not a list

    emptyLayers = []
    for sectName, layer in layers.items():
        if (isListEmpty(layer)):
            emptyLayers.append(sectName)
    for emptyLayer in emptyLayers:
        layers.pop(emptyLayer)
    return layers.copy()


def checkFullDictionary(dict1):
    result = True
    for key, value in dict1.items():
        if (value == None):
            result = False
    return result


def copyLayers(layers):
    newlayers = {}
    for key, layer in layers.items():
        newlayers[key] = []
        i = 0
        for rowList in layer:
            newlayers[key].append([])
            for colList in rowList:
                newlayers[key][i].append(colList.copy())
            i += 1
    return newlayers


def getPlans(scheduleLayers, numSect, sectList, SameTeacherSect):
    allPlans = []
    onePlan = dict.fromkeys(sectList)
    depth = numSect
    alist = [0] * numSect
    numPlanDone = [0]
    planLimit = -1

    # see https://stackoverflow.com/questions/4138851/recursive-looping-function-in-python
    def recurse(layers, depth):
        if (len(layers) <= 0 or depth <= 0):
            return
        topKey = list(layers.keys())[0]
        availableSect = getSectOfLayer(layers[topKey])
        layers.pop(topKey)
        for section, times in availableSect.items():
            if (planLimit != -1 and planLimit == len(allPlans)):
                return
            removeList = getRemoveList(layers, times, SameTeacherSect, section)
            newlayers = removeSections(copyLayers(layers), removeList)
            length = len(layers)
            newlayers = removeEmptyLayers(newlayers)

            if (len(layers) != length):
                continue
            onePlan[section.split('-')[1]] = section
            if (checkFullDictionary(onePlan) and depth == 1):
                allPlans.append(onePlan.copy())
                numPlanDone[0] += 1
            alist[depth - 1] += 1
            print("\r", end="")
            print(alist, end="")
            print(" %d Zip Plans Done" % (numPlanDone[0]), end="")
            recurse(copyLayers(newlayers), depth-1)

    recurse(copyLayers(scheduleLayers), depth)

    print("")
    return allPlans


def getSectList(prepData):
    sectList = []
    countSect = {}
    for course in prepData:
        for type in prepData[course]:
            sectName = course + "," + type
            countSect[sectName] = len(prepData[course][type])
    countSect = dict(sorted(countSect.items(), key=lambda item: item[1]))
    for sectName in countSect:
        sectList.append(sectName)
    return sectList


def getScheduleLayers(sectList, prepData):
    scheduleLayers = {}
    for sectName in sectList:
        course = sectName.split(",")[0]
        type = sectName.split(",")[1]
        sections = prepData[course][type]
        oneSchedule = getOneSchedule(sections, newSchedule())
        scheduleLayers[sectName] = oneSchedule
    return scheduleLayers


def newSchedule():  # indexChange
    timeRange = 24*12
    weekRange = 7
    schedule = []
    # oneWeek = ["Time", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hours = 0
    minutes = 0
    for i in range(0, timeRange + 1):
        schedule.append([])
        for j in range(0, weekRange + 1):
            schedule[i].append([])
    return schedule


def getOneSchedule(sections, sch):
    def findIndex(day, hours, minutes):  # indexChange
        if(day == "M"):
            col = 1-1
        elif(day == "T"):
            col = 2-1
        elif(day == "W"):
            col = 3-1
        elif(day == "R"):
            col = 4-1
        elif(day == "F"):
            col = 5-1
        # elif(day == "Sa"):
        #     col = 6
        # elif(day == "Su"):
        #     col = 7
        row = int(1-1 + (12*hours) + (minutes/5))
        return [row, col]

    def timeConvertion(time):
        timeDict = {"hours": 0, "minutes": 0}
        hrMin = time[0].split(":")
        AmPm = time[1]
        if((AmPm == "pm") & (int(hrMin[0]) < 12)):
            timeDict["hours"] = int(hrMin[0]) + 12
        else:
            timeDict["hours"] = int(hrMin[0])
        timeDict["minutes"] = int(hrMin[1])
        return timeDict

    for section in sections:
        # Creat display title
        ID = section[0]
        code = section[len(section) - 1]
        type = section[3]
        title = ID + "-" + code + "," + type

        # Extract time information
        timeRawData = section[5].split(",")
        timeNewData = []
        for oneRawtime in timeRawData:

            days = re.findall(r'[A-Z]', oneRawtime)
            time = re.findall(
                r'([0-9]?[0-9]:[0-9][0-9]) ([a-z]{2})', oneRawtime)
            if(len(time) < 2):
                return False
            start = timeConvertion(time[0])
            end = timeConvertion(time[1])
            onetime = [days, start, end]
            timeNewData.append(onetime)

        # Put section in schedule
        for oneNewtime in timeNewData:
            startHr = oneNewtime[1]["hours"]
            startMin = oneNewtime[1]["minutes"]
            endHr = oneNewtime[2]["hours"]
            endMin = oneNewtime[2]["minutes"]
            for day in oneNewtime[0]:
                [srow, scol] = findIndex(day, startHr, startMin)
                [erow, ecol] = findIndex(day, endHr, endMin)
                for i in range(srow, erow+1):
                    sch[i][ecol].append(title)
    return sch
