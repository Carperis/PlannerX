import shutil
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
# print(base_dir)

def initialize_database():
    # try:
    #     base_dir = base_dir.replace("\\", "/")
    #     path = base_dir + "/instance"
    #     # print(path)
    #     shutil.rmtree(path)
    # except:
    #     print("No instance folder")

    from web_init import app, db
    app.app_context().push()
    db.create_all()
    print("Database initialized")

if __name__ == "__main__":
    initialize_database()