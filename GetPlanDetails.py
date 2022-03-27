def AddPlanDetails(semester, prefName):
    Info_bookName = semester + "_" + prefName + "_" + "Info"


if __name__ == "__main__":
    semester = "2022-SPRG"  # Fall:"FALL", Summer:"SUMM", Spring:"SPRG"
    prefName = "My Preference 1"
    AddPlanDetails(semester, prefName)
