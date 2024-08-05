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
    title: str
    content: str


####################
# Forms
####################


class EvaluationsTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([Evaluation])


Evaluations = EvaluationsTable(DB)
