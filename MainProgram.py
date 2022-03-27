import os
import GetCourses
import GetSections
import GetTeachersScores
import GetPreference
import AutoSelection


def main():
    clear()
    semester = "2022-FALL"  # Fall:"FALL", Summer:"SUMM", Spring:"SPRG"
    prefName = "My Preference F22"
    print("Which one to run?\n1.GetCourses\n2.GetSections\n3.GetTeachersScores\n4.GetPreference\n5.AutoSelection")
    choice = int(input("\nSelection (1-5): "))
    if (choice == 1):
        clear()
        GetCourses.GetCourses(semester)
    elif (choice == 2):
        clear()
        GetSections.GetSections(semester)
    elif (choice == 3):
        clear()
        GetTeachersScores.GetTeachersScores()
    elif (choice == 4):
        clear()
        GetPreference.GetPreference(prefName)
    elif (choice == 5):
        clear()
        AutoSelection.AutoSelection(semester, prefName)
    elif (choice == 6):
        pass


def clear():
    os.system('cls')  # for windows
    os.system('clear')  # for mac/linux


if __name__ == "__main__":
    main()
