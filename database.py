from peewee import *
import os

db_path = os.path.join(os.path.dirname(__file__), "schedule.db")

db = SqliteDatabase(db_path)
