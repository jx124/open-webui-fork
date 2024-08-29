from pydantic import BaseModel
from peewee import *
from playhouse.shortcuts import model_to_dict
from typing import List, Union, Optional

from apps.webui.internal.db import DB
from apps.webui.models.chats import Chats

####################
# Evaluation DB Schema
####################


class Evaluation(Model):
    title = CharField(null=False, unique=True)
    content = TextField(default="")

    class Meta:
        database = DB


class EvaluationModel(BaseModel):
    id: int
    title: str
    content: str


####################
# Forms
####################

class EvaluationForm(BaseModel):
    id: int = 0
    title: str
    content: str

class EvaluationsTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([Evaluation])

    def get_evaluations(self) -> List[EvaluationModel]:
        return Evaluation.select()
    
    def get_evaluation_by_id(self, eval_id: int) -> Optional[EvaluationModel]:
        try:
            result = Evaluation.select().where(Evaluation.id == eval_id).get()
            return EvaluationModel(**model_to_dict(result))
        except:
            return None
    
    def get_evaluation_by_title(self, title: str) -> Optional[EvaluationModel]:
        try:
            result = Evaluation.select().where(Evaluation.title == title).get()
            return EvaluationModel(**model_to_dict(result))
        except:
            return None
    
    def insert_new_evaluation(self, form_data: EvaluationForm) -> Optional[EvaluationModel]:
        try:
            result = Evaluation.create(title=form_data.title, content=form_data.content)
            if result:
                return EvaluationModel(**model_to_dict(result))
            else:
                return None
        except:
            return None

    def update_evaluation(self, form_data: EvaluationForm) -> Optional[EvaluationModel]:
        try:
            result = Evaluation.update(title=form_data.title, content=form_data.content)\
                .where(Evaluation.id == form_data.id).execute()
            if result:
                return EvaluationModel(**model_to_dict(Evaluation.get(Evaluation.id == form_data.id)))
            else:
                return None
        except Exception as e:
            print("error", e)
            return None
        
    def delete_evaluation_by_id(self, eval_id: int) -> bool:
        try:
            result = Evaluation.delete().where(Evaluation.id == eval_id).execute()
            return result == 1
        except:
            return False

Evaluations = EvaluationsTable(DB)
