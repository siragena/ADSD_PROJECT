# ADSD_PROJECT
Advanced Database System Design Final Project Fall 2025
-------------------------------------------------------
Prerequisites:
•	Python 3.x installed on the machine
1. Obtain the source code

Either clone the GitHub repository of our Project or download the ZIP file from GitHub and extract it, then open that folder in VS Code or your preferred editor.

2. Create and activate a virtual environment 
In the project folder, open the terminal and type the following commands:
       python -m venv venv
       .\venv\Scripts\activate

3. Install dependencies

In the same terminal run the following commands,
    python -m pip install --upgrade pip
    python -m pip install flask peewee

4. Initialize the database

Run the database creation script, in our project is create_tables.py file.
Command to run in VS terminal: python create_tables.py
This creates the SQLite database file named schedule.db with the Class, Employer, and Shift tables.

5. Start the web application

Command to run in VS terminal: python app.py
By default, Flask runs on http://127.0.0.1:5000/, and by using the browser open that link to access the application, you should see the main page of the Work Shifts and Class Schedules Tracker.



