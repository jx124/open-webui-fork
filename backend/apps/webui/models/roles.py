from pydantic import BaseModel, ConfigDict
from peewee import *
from playhouse.shortcuts import model_to_dict
from typing import List, Union, Optional
import time
from utils.misc import get_gravatar_url

from apps.webui.internal.db import DB, JSONField

####################
# Role DB Schema
####################


class Role(Model):
    id = AutoField()
    name = CharField(null=False, default="pending", unique=True)

    class Meta:
        database = DB


class RoleModel(BaseModel):
    id: int
    name: str


####################
# Forms
####################


class RoleForm(BaseModel):
    id: int
    name: str

class RolesTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([Role])

    def insert_new_role(self, name: str) -> Optional[RoleModel]:
        try:
            result = Role.get_or_create(name=name)
            if result:
                return RoleModel(**model_to_dict(result))
            else:
                return None
        except:
            return None
        
    def get_role_by_name(self, name: str) -> Optional[RoleModel]:
        try:
            role = Role.get(Role.name == name)
            return RoleModel(**model_to_dict(role))
        except Exception as e:
            return None

    def get_roles(self) -> List[RoleModel]:
        return [
            RoleModel(**model_to_dict(role))
            for role in Role.select().order_by(Role.id)
        ]
    
    def update_role(self, role: RoleForm) -> Optional[RoleModel]:
        try:
            result = Role.update(name=role.name).where(Role.id == role.id).execute()

            if result:
                return RoleModel(**model_to_dict(Role.get(Role.id == role.id)))
            else:
                return None
            
        except Exception as e:
            return None
        
    def delete_role_by_id(self, id: int) -> bool:
        try:
            result = Role.delete().where(Role.id == id).execute()
            return result == 1
        except:
            return False



Roles = RolesTable(DB)
