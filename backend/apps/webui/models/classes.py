from pydantic import BaseModel
from peewee import *
from playhouse.shortcuts import model_to_dict
from typing import List, Union, Optional

from apps.webui.internal.db import DB
from apps.webui.models.users import User
from apps.webui.models.prompts import Prompt

####################
# Class DB Schema
####################


class Class(Model):
    id = AutoField()
    name = CharField(null=False, unique=True)
    instructor_id = ForeignKeyField(User)

    class Meta:
        database = DB


class ClassModel(BaseModel):
    id: int
    name: str


####################
# StudentClass DB Schema
####################


class StudentClass(Model):
    student_id = ForeignKeyField(User)
    class_id = ForeignKeyField(Class)

    class Meta:
        database = DB


####################
# ClassPrompt DB Schema
####################


class ClassPrompt(Model):
    class_id = ForeignKeyField(Class)
    prompt_id = ForeignKeyField(Prompt)

    class Meta:
        database = DB


####################
# Class Forms
####################


class ClassesTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([Class])


Classes = ClassesTable(DB)


####################
# StudentClass Forms
####################


class StudentClassesTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([StudentClass])


StudentClasses = StudentClassesTable(DB)


####################
# ClassPrompt Forms
####################


class ClassPromptsTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([ClassPrompt])


ClassPrompts = ClassPromptsTable(DB)