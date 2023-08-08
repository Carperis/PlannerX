# PlannerX

## Introduction

PlannerX is a website-based program that allows university students to automatically create custom schedules to meet their class requirements and personal preferences. The current version BU PlannerX is made for Boston University students.

## Setup

To correctly setup the program, please go over the following steps in your terminal:

1. Check your python version before setup the program. Make sure the version is above 3.6.

   ```
   python --version
   ```
2. In the terminal, switch to the current PlannerX folder.

   ```
   cd /path/to/PlannerX
   ```
3. Install all required libraries.

   ```
   pip install -r requirements.txt --user
   ```
4. If you first run the app, you have to initialize the database.

   ```
   python InitDatabase.py
   ```
5. If there is nothing wrong with your libraries, then you are good to run the program!

   ```
   python web.py
   ```
6. If it runs successfully, you should be able to open the website using this link: [http://127.0.0.1:5000/](http://127.0.0.1:5000/). In your browser, you should see the website looks like this:

![schedule](./webpage.png)
