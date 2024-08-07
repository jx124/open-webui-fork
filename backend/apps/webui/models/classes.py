from pydantic import BaseModel
from peewee import *
from playhouse.shortcuts import model_to_dict
from typing import List, Union, Optional

from apps.webui.internal.db import DB
from apps.webui.models.users import User

####################
# Class DB Schema
####################


class Class(Model):
    id = AutoField()
    name = CharField(null=False, unique=True)
    instructor = ForeignKeyField(User)

    class Meta:
        database = DB


class ClassModel(BaseModel):
    id: int
    name: str
    instructor_id: str
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
# Class Forms
####################


class ClassForm(BaseModel):
    id: int
    name: str
    instructor_id: str


def class_to_classmodel(class_: Class) -> ClassModel:
    # flattens the class dict so "name" is visible to ClassModel
    class_dict = model_to_dict(class_)
    return ClassModel(**class_dict,
                      instructor_id=class_dict["instructor"]["id"],
                      instructor_name=class_dict["instructor"]["name"])


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
        
    def get_class_by_id(self, user_id:str, user_role: str, class_id: int) -> Optional[ClassModel]:
        try:
            class_ = Class.select()\
                .join(User)\
                .where((Class.id == class_id) & ((Class.instructor.id == user_id) | (user_role == "admin"))).get()

            return class_to_classmodel(class_)
        except:
            return None
 
    def insert_new_class(self, form_data: ClassForm) -> Optional[ClassModel]:
        try:
            result = Class.create(**form_data.model_dump(exclude={"id"}))
            return class_to_classmodel(result)
        except:
            return None

    def update_class_by_id(self, form_data: ClassForm) -> bool:
        try:
            query = Class.update(**form_data.model_dump(exclude={"id"})).where(Class.id == form_data.id)
            query.execute()

            return True
        except:
            return False
        
    def delete_class_by_id(self, class_id: int) -> bool:
        try:
            query = Class.delete().where(Class.id == class_id)
            query.execute()  # Remove the rows, return number of rows removed.

            return True
        except:
            return False


Classes = ClassesTable(DB)


####################
# StudentClass Forms
####################


class StudentClassesTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([StudentClass])


StudentClasses = StudentClassesTable(DB)
