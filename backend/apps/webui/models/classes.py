from pydantic import BaseModel
from peewee import *
from playhouse.shortcuts import model_to_dict
from typing import List, Union, Optional

from apps.webui.internal.db import DB
from apps.webui.models.users import User
from apps.webui.models.prompts import Prompt
from apps.webui.models.roles import Role

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
    instructor_name: str


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


class ClassForm(BaseModel):
    name: str
    instructor_id: str


def class_to_classmodel(class_: Class) -> ClassModel:
    # flattens the class dict so "name" is visible to ClassModel
    class_dict = model_to_dict(class_)
    return ClassModel(**class_dict, instructor_name=class_dict["instructor_id"]["name"])


class ClassesTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([Class])

    def get_classes(self, user_id: str, user_role: str) -> List[ClassModel]:
        if user_role == "admin":
            return [class_to_classmodel(class_) for class_ in Class.select()]

        elif user_role == "instructor":
            return [
                class_to_classmodel(class_) 

                for class_ in Class.select()
                    .where(Class.instructor_id == user_id)
            ]

        else:
            return [
                class_to_classmodel(class_)

                for class_ in Class.select()
                    .join(StudentClass, on=(Class.id == StudentClass.class_id))
                    .join(User, on=(User.id == StudentClass.student_id))
                    .where((User.id == user_id))
            ]
    
    def get_class_by_name(self, name: str) -> Optional[ClassModel]:
        try:
            class_ = Class.get(Class.name == name)
            return class_to_classmodel(class_)
        except:
            return None
 
    def insert_new_class(self, form_data: ClassForm) -> Optional[ClassModel]:
        try:
            result = Class.create(**form_data.model_dump())
            return class_to_classmodel(result)
        except Exception as e:
            return None


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