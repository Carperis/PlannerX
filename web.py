from flask import Flask, redirect, render_template, request
import GetPreferenceWeb
app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    classes = ["", ""]
    if (request.method == 'POST'):
        cls = request.form['content']
        username = request.form['username']
        classes = str(cls).split(",")
        newcls = classes.copy()
        for i in range(0, len(classes)):
            newcls[i] = [classes[i]]
        GetPreferenceWeb.GetPreference(username, newcls)
    else:
        pass
    return render_template('index.html', classes=classes)


if __name__ == "__main__":
    app.run(debug=True)
