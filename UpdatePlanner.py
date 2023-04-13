import os
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import xlrd


def main():
    # login studentlink class planner Fall 2022
    myusername = input("Enter username: ")
    mypassword = input("Enter password: ")
    options = webdriver.ChromeOptions()
    browser = webdriver.Chrome(options=options)
    # see https://stackoverflow.com/questions/61308799/unable-to-locate-elements-in-selenium-python
    browser.get(
        "https://www.bu.edu/link/bin/uiscgi_studentlink.pl/1650384260?ModuleName=reg/option/_start.pl&ViewSem=Fall%202022&KeySem=20233")
    browser.find_element(By.ID, "j_username").send_keys(myusername)
    browser.find_element(By.ID, "j_password").send_keys(mypassword)
    browser.find_element(By.NAME, "_eventId_proceed").click()
    # see https://www.testclass.cn/selenium_iframe.html
    browser.switch_to.frame("duo_iframe")
    sleep(3)
    clear()
    code = input("Enter code here: ")
    browser.find_element(By.ID, "passcode").click()
    browser.find_element(By.NAME, "passcode").send_keys(str(code))
    sleep(1)
    browser.find_element(By.ID, "passcode").click()
    sleep(3)
    browser.find_element(By.LINK_TEXT, "Plan").click()
    # clear current plan
    clearClass(browser)
    browser.find_element(By.LINK_TEXT, "Add").click()
    s = Select(browser.find_element(By.NAME, "College"))
    s.select_by_visible_text('CAS')
    browser.find_element(
        By.XPATH, "//input[contains(@onclick,'SearchSchedule')]").click()
    copy2studentlink(browser, './User/Sam/2022-FALL Sam Info.xls', 'Plan5')
    browser.quit()


def clear():
    os.system('cls')  # for windows
    os.system('clear')  # for mac/linux


def clearClass(browser):  # clear current plan
    hasRemove = True
    while (hasRemove):
        try:
            browser.find_element(By.LINK_TEXT, "Remove").click()
        except:
            hasRemove = False


def hasElement(browser, xpath):
    try:
        browser.find_element(By.XPATH, xpath)
    except:
        return False
    return True


def readPrefData(filePath, sheetName):
    dataList = []
    book = xlrd.open_workbook(filePath)
    sheet = book.sheet_by_name(sheetName)
    rows = sheet.nrows
    cols = len(sheet.row_slice(0))
    for r in range(1, rows):
        data = []
        for c in range(cols):
            data.append(sheet.cell_value(r, c))
        dataList.append(data)
    return dataList


def findNameWeb(browser):
    element = browser.find_elements(
        By.XPATH, "/html/body/form/table[1]/tbody/tr[2]/td[3]")
    if (element[0].text != ""):
        name = str(element[0].text)
        value = 0
    else:
        element = browser.find_elements(
            By.XPATH, "/html/body/form/table[1]/tbody/tr[3]/td[3]")
        value = 1
        name = str(element[0].text)
    if (name == ""):
        element = browser.find_elements(
            By.XPATH, "/html/body/form/table[1]/tbody/tr[3]/td[3]")
        name = str(element[0].text)
        value = 1
        print("return value is: ", value, " content is: ", name)
        return value
    print("return value is: ", value, " content is: ", name)
    return value


def copy2studentlink(browser, filePath, sheetName):
    dataList = readPrefData(filePath, sheetName)
    for i in range(len(dataList)):
     # read a class info once at a time
        [col, dep, cour] = dataList[i][9].split(" ")
        sect = dataList[i][0]
        # fill out studentlink once at a time
        try:
            browser.find_element(By.NAME, "College").clear()
            browser.find_element(By.NAME, "Dept").clear()
            browser.find_element(By.NAME, "Course").clear()
            browser.find_element(By.NAME, "Section").clear()
            browser.find_element(By.NAME, "College").send_keys(col)
            browser.find_element(By.NAME, "Dept").send_keys(dep)
            browser.find_element(By.NAME, "Course").send_keys(cour)
            browser.find_element(By.NAME, "Section").send_keys(sect)
            # see https://www.cnpython.com/qa/138943
            browser.find_element(
                By.XPATH, "//input[contains(@onclick,'ShowMore')]").click()  # search
            try:
                if (findNameWeb(browser) == 1):
                    # check box at line 2
                    if (hasElement(browser, "/html/body/form/table[1]/tbody/tr[3]/td[1]/a") == False):
                        browser.find_element(
                            By.XPATH, "/html/body/form/table[1]/tbody/tr[3]/td[1]/input").click()
                    else:
                        print("The course is blocked: ", col, dep, cour, sect)
                else:
                    # check box at line 1
                    if (hasElement(browser, "/html/body/form/table[1]/tbody/tr[2]/td[1]/a") == False):
                        browser.find_element(
                            By.XPATH, "/html/body/form/table[1]/tbody/tr[2]/td[1]/input").click()
                    else:
                        print("The course is blocked: ", col, dep, cour, sect)
                # /html/body/form/table[1]/tbody/tr[3]/td[1]/input
                print(col, dep, cour, sect, " added")
            except:
                print("Can't add course", col, dep, cour, sect)
        except:
            print("Can't find course", col, dep, cour, sect)
    browser.find_element(
        By.XPATH, "/html/body/form/center[2]/table/tbody/tr/td[1]/input").click()


if __name__ == "__main__":
    main()
