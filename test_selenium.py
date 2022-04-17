import os
from selenium import webdriver
from time import sleep
from http.cookies import SimpleCookie
from selenium.webdriver.common.by import By


def clear():
    os.system('cls')  # for windows
    os.system('clear')  # for mac/linux


def findSeat(browser):
    element = browser.find_elements(
        By.XPATH, "/html/body/form/table[1]/tbody/tr[2]/td[6]")  # see https://stackoverflow.com/questions/3030487/is-there-a-way-to-get-the-xpath-in-google-chrome
    if (element[0].text != ""):
        seat = int(element[0].text)
    else:
        element = browser.find_elements(
            By.XPATH, "/html/body/form/table[1]/tbody/tr[3]/td[6]")
        seat = int(element[0].text)
    return seat


options = webdriver.ChromeOptions()
browser = webdriver.Chrome(options=options)
# see https://stackoverflow.com/questions/61308799/unable-to-locate-elements-in-selenium-python
browser.get("https://www.bu.edu/link/bin/uiscgi_studentlink.pl/1642611818?ModuleName=reg%2Fadd%2Fbrowse_schedule.pl&SearchOptionDesc=Class+Number&SearchOptionCd=S&ViewSem=Spring+2022&KeySem=20224&AddPlannerInd=Y&College=CAS&Dept=&Course=&Section=")
browser.find_element(By.ID, "j_username").send_keys("qiupeng")
browser.find_element(By.ID, "j_password").send_keys("QPSam15982818")
browser.find_element(By.NAME, "_eventId_proceed").click()
# see https://www.testclass.cn/selenium_iframe.html
browser.switch_to.frame("duo_iframe")
sleep(5)
clear()
code = input("Enter code here: ")
browser.find_element(By.ID, "passcode").click()
browser.find_element(By.NAME, "passcode").send_keys(str(code))
sleep(1)
browser.find_element(By.ID, "passcode").click()
sleep(1)
# pageSource = browser.page_source
# print(pageSource)


i = ""
while(i != "q"):
    i = input("Enter course: ")
    try:
        [col, dep, cour, sect] = i.split(" ")
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
            By.XPATH, "//input[contains(@onclick,'ShowMore')]").click()
        print(findSeat(browser))
    except:
        pass

browser.quit()
