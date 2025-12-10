from peewee import *
from database import db

class BaseModel(Model):
    class Meta:
        database = db


class Class(BaseModel):
    name = CharField()
    day_of_week = CharField()
    start_time = TimeField()
    end_time = TimeField()
    location = CharField(null=True)


class Employer(BaseModel):
    name = CharField()
    hourly_rate = FloatField(default=0.0)


class Shift(BaseModel):
    employer = ForeignKeyField(Employer, backref='shifts')
    date = DateField()
    start_time = TimeField()
    end_time = TimeField()
    notes = TextField(null=True)
