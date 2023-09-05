import shutil
import os
import InitDatabase as init

try:
    path1 = "./Users/"
    shutil.rmtree(path1)
    print("Users folder deleted")
except Exception as e:
    print(e)

try:
    path2 = "./static/Users/"
    shutil.rmtree(path2)
    print("static/Users folder deleted")
except Exception as e:
    print(e)

try:
    path3 = "./instance/"
    shutil.rmtree(path3)
    print("instance folder deleted")
except Exception as e:
    print(e)
    
try:
    path4 = "./web.db"
    os.remove(path4)
    print("web.db deleted")
except Exception as e:
    print(e)

init.initialize_database()
