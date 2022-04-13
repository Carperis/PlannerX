from flask import Flask, redirect, render_template, request, flash
import GetPreferenceWeb
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/', methods=['POST', 'GET'])
def index():
    prefDict = {}
    classes = ["", ""]
    if (request.method == 'POST'):
        cls = request.form['content']
        username = request.form['username']
        classes = str(cls).split(",")
        prefDict["Courses"] = classes
        prefDict["AvgScore"] = [3.5]
        prefDict["EarlyTime"] = [8]
        prefDict["LateTime"] = [18]
        result = GetPreferenceWeb.GetPreference(
            username, prefDict, "2022-FALL")
        if (result == False):
            print(classes)
            flash("Invalid course input!")
        else:
            flash("Preferences Saved!")
    else:
        pass
    return render_template('index.html', classes=classes)


if __name__ == "__main__":
    app.run(debug=True)
