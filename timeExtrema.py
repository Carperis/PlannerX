import pandas as pd


def timeExtrema(filename):
    # read file to get schedule
    df = pd.read_excel(filename, None, usecols=[5])
    # initialized var
    startMax = 24
    endMin = 0
    for j in range(len(df)):
        name = 'Plan' + str(j+1)
        for i in range(df[name].shape[0]):
            a = df[name].loc[i].at["Schedule"]
            days, start, mix, when2 = a.split(' ')
            when1, end = mix.split('-')
            hour1, minute1 = start.split(':')
            hour2, minute2 = end.split(':')
            if when1 == "pm" and int(hour1) != 12:
                start_time = int(hour1)+12+int(minute1)/60
            else:
                start_time = int(hour1)+int(minute1)/60
            if when2 == "pm" and int(hour2) != 12:
                end_time = int(hour2)+12+int(minute2)/60
            else:
                end_time = int(hour2)+int(minute2)/60
            if (start_time < startMax):
                startMax = start_time
            if (end_time > endMin):
                endMin = end_time
    if startMax > 12:
        hour1 = int(startMax)-12
        when1 = "pm"
    else:
        hour1 = int(startMax)
        when1 = "am"
    if endMin > 12:
        hour2 = int(endMin)-12
        when2 = "pm"
    else:
        hour2 = int(endMin)
        when2 = "am"
    minute1 = int((startMax - int(startMax))*60)
    minute2 = int((endMin - int(endMin))*60)
    print("max is: ", hour1, ':', minute1,
          when1, " ", hour2, ':', minute2, when2)
    timeExteme = [startMax, endMin]
    return timeExteme

<<<<<<< HEAD
#test
username = input("Enter your user name: ")
name = "./User/" + username + "/2022-Fall "+ username +" Info.xls"
print(name)
timeExtrema(name)
=======

# test
name = './User/Sam/2022-FALL Sam Info.xls'
timeExtrema(name)
>>>>>>> 338ea482229d565651ab3569e00fd079efc1034a
