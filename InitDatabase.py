import shutil
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
# print(base_dir)

# try:
#     base_dir = base_dir.replace("\\", "/")
#     path = base_dir + "/instance"
#     # print(path)
#     shutil.rmtree(path)
# except:
#     print("No instance folder")

from web import app, db
app.app_context().push()
db.create_all()