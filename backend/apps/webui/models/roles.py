from pydantic import BaseModel, ConfigDict
from peewee import *
from playhouse.shortcuts import model_to_dict
from typing import List, Union, Optional
import time
from utils.misc import get_gravatar_url

from apps.webui.internal.db import DB, JSONField
from apps.webui.models.chats import Chats

####################
# Role DB Schema
####################


class Role(Model):
    id = AutoField()
    name = TextField(null=False, default="pending")

    class Meta:
        database = DB


class RoleModel(BaseModel):
    id: int
    name: str


####################
# Forms
####################


class UserRoleUpdateForm(BaseModel):
    id: str
    role: str

class RolesTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([Role])

Roles = RolesTable(DB)
