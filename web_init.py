from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
import os

# DO NOT USE AUTO FORMATTING IN THIS FILE

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///web.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'

db = SQLAlchemy(app)

# make sure this matches with that's in client_secret.json
app.secret_key = "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"
# to allow Http traffic for local dev
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
try:
    with open('email.txt', 'r') as file:
        email = file.readline().strip()
        password = file.readline().strip()
    app.config['MAIL_USERNAME'] = email
    app.config['MAIL_PASSWORD'] = password
except:
    print("email.txt not found")
    pass
# print(app.config['MAIL_USERNAME'])
# print(app.config['MAIL_PASSWORD'])
mail = Mail(app)

# To make sure you can run the app,
# !!!!! PLEASE PUT "import web_routes" BELOW THIS LINE !!!!!
import web_routes