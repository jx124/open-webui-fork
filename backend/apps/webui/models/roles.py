from pydantic import BaseModel
import peewee as pw
from playhouse.shortcuts import model_to_dict
from typing import List, Optional

from apps.webui.internal.db import DB

import logging
from config import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# Role DB Schema
####################


class Role(pw.Model):
    id = pw.AutoField()
    name = pw.CharField(null=False, default="pending", unique=True)

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
            result = Role.get_or_create(name=name.strip())
            if result:
                return RoleModel(**model_to_dict(result))
            else:
                return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_role_by_name(self, name: str) -> Optional[RoleModel]:
        try:
            role = Role.get_or_none(Role.name == name)
            if role:
                return RoleModel(**model_to_dict(role))
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_roles(self) -> List[RoleModel]:
        try:
            return [
                RoleModel(**model_to_dict(role))
                for role in Role.select().order_by(Role.id)
            ]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def update_role(self, role: RoleForm) -> Optional[RoleModel]:
        try:
            result = Role.update(name=role.name.strip()).where(Role.id == role.id).execute()

            if result:
                return RoleModel(**model_to_dict(Role.get_or_none(Role.id == role.id)))
            else:
                return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def delete_role_by_id(self, id: int) -> bool:
        try:
            result = Role.delete().where(Role.id == id).execute()
            return result == 1

        except Exception:
            log.exception(" Exception caught in model method.")
            return False


Roles = RolesTable(DB)
