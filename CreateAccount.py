from web_init import db, bcrypt, app
from web_models import User
import os

app.app_context().push()

if (os.system('clear') == 1):
    os.system('cls')
print("Follow the prompts to create a new user account. Press ENTER to comfirm each entry.")
email = input("Enter user email: ")
username = input("Enter user name: ")
password = input("Enter user password: ")

hashed_password = bcrypt.generate_password_hash(password)
new_user = User(username=username, email=email,
                password=hashed_password, google=False)
db.session.add(new_user)
db.session.commit()
