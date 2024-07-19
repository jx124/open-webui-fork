from pydantic import BaseModel
from peewee import *
from playhouse.shortcuts import model_to_dict
from typing import List, Union, Optional
import time
from collections import defaultdict

from apps.webui.models.roles import Role
from apps.webui.models.users import User

from apps.webui.internal.db import DB

####################
# Prompts DB Schema
####################


class Prompt(Model):
    command = CharField(unique=True)
    user_id = CharField()
    title = TextField()
    content = TextField()
    timestamp = BigIntegerField()
    is_visible = BooleanField(default=True)
    additional_info = TextField(default="")

    class Meta:
        database = DB


class PromptModel(BaseModel):
    id: int
    command: str
    user_id: str
    title: str
    content: str
    timestamp: int  # timestamp in epoch
    is_visible: bool   # whether prompt is visible to others
    additional_info: str
    permitted_roles: List[int]


####################
# PromptRole DB Schema
####################

# Schema placed here to prevent circular dependencies

class PromptRole(Model):
    prompt_id = ForeignKeyField(Prompt)
    role_id = ForeignKeyField(Role)

    class Meta:
        database = DB


class PromptRoleModel(BaseModel):
    prompt_id: int
    role_id: int


####################
# Prompt Forms
####################


class PromptForm(BaseModel):
    command: str
    title: str
    content: str
    is_visible: bool
    additional_info: str
    permitted_roles: List[int]


class PromptsTable:

    def __init__(self, db):
        self.db = db
        self.db.create_tables([Prompt])

    def insert_new_prompt(
        self, user_id: str, form_data: PromptForm
    ) -> Optional[PromptModel]:
        prompt = PromptModel(
            **{
                "id": 0,
                "user_id": user_id,
                "command": form_data.command,
                "title": form_data.title,
                "content": form_data.content,
                "timestamp": int(time.time()),
                "is_visible": form_data.is_visible,
                "additional_info": form_data.additional_info,
                "permitted_roles": form_data.permitted_roles
            }
        )

        try:
            result = Prompt.create(**prompt.model_dump(exclude={'id', 'permitted_roles'}))
            if result:
                prompt_id = Prompt.get(Prompt.command == form_data.command).id
                prompt.id = prompt_id
                PromptRoles.insert_new_prompt_roles_by_prompt(prompt_id, form_data.permitted_roles)

                return prompt
            return None
        except:
            return None

    def get_prompt_by_command(self, user_id: str, command: str) -> Optional[PromptModel]:
        try:
            prompt = None
            if (user_id):
                # used a left outer join so admin role does not need to be added for every prompt
                prompt = Prompt.select()\
                    .join(PromptRole, JOIN.LEFT_OUTER)\
                    .join(User, on=(User.id == Prompt.user_id))\
                    .join(Role, on=(Role.id == User.role_id))\
                    .where(Prompt.command == command)\
                    .where(((Prompt.is_visible == True) & (User.role_id == PromptRole.role_id))       # user permitted
                           | (Prompt.user_id == user_id)                                              # user's own prompt
                           | ((Prompt.is_visible == True) & (Role.name == "admin"))).distinct().get() # user is admin
            else:
                # If no user_id is provided, directly return prompt to check for collisions when creating prompts
                prompt = Prompt.get(Prompt.command == command)

            # fill in the permitted roles manually since group concat is not supported
            prompt_roles = []
            prompt_roles_query = PromptRole.select().where(PromptRole.prompt_id == prompt.id)
            for row in prompt_roles_query:
                prompt_roles.append(row.role_id.id)
            
            return PromptModel(**model_to_dict(prompt), permitted_roles=prompt_roles)
        except:
            return None

    def get_prompts(self, user_id: str) -> List[PromptModel]:
        prompts = [
            model_to_dict(prompt)

            # used a left outer join so admin role does not need to be added for every prompt
            for prompt in Prompt.select()\
                .join(PromptRole, JOIN.LEFT_OUTER)\
                .join(User, on=(User.id == Prompt.user_id))\
                .join(Role, on=(Role.id == User.role_id))\
                .where(((Prompt.is_visible == True) & (User.role_id == PromptRole.role_id))     # user permitted
                        | (Prompt.user_id == user_id)                                           # user's own prompt
                        | ((Prompt.is_visible == True) & (Role.name == "admin")))               # user is admin
                .distinct()
        ]

        # fill in the permitted roles manually since group concat is not supported
        prompt_roles = defaultdict(list[int])
        prompt_roles_query = PromptRole.select()
        for row in prompt_roles_query:
            prompt_roles[row.prompt_id.id].append(row.role_id.id)
        
        for prompt in prompts:
            prompt["permitted_roles"] = prompt_roles[prompt["id"]]

        return [PromptModel(**prompt) for prompt in prompts]
    
    def update_prompt_by_command(
        self, user_id: str, command: str, form_data: PromptForm
    ) -> Optional[PromptModel]:
        try:
            query = Prompt.update(
                title=form_data.title,
                content=form_data.content,
                timestamp=int(time.time()),
                is_visible=form_data.is_visible,
                additional_info=form_data.additional_info
            ).where(Prompt.command == command, (Prompt.is_visible == True) | (Prompt.user_id == user_id))
            # we do not check the roles here since we only allow admins to update/delete prompts, which is validated by
            # the router

            result = query.execute()

            if result:
                prompt = Prompt.get(Prompt.command == command)
                prompt = PromptModel(**model_to_dict(prompt), permitted_roles=form_data.permitted_roles)
                
                PromptRoles.update_prompt_roles_by_prompt(prompt.id, form_data.permitted_roles)

                return prompt

            return None
        except:
            return None

    def delete_prompt_by_command(self, user_id: str, command: str) -> bool:
        try:
            prompt = Prompts.get_prompt_by_command(user_id, command)

            if not prompt:
                return False

            PromptRoles.delete_prompt_roles_by_prompt(prompt.id)

            query = Prompt.delete().where(
                Prompt.command == command,
                (Prompt.is_visible == True) | (Prompt.user_id == user_id)
            )
            # we do not check the roles here since we only allow admins to update/delete prompts, which is validated by
            # the router
            query.execute()  # Remove the rows, return number of rows removed.

            return True
        except:
            return False


Prompts = PromptsTable(DB)


####################
# PromptRole Forms
####################


class PromptRoleForm(BaseModel):
    prompt_id: int
    role_id: int


class PromptRolesTable:

    def __init__(self, db):
        self.db = db
        self.db.create_tables([PromptRole])

    def insert_new_prompt_roles_by_prompt(
        self, prompt_id: int, role_ids: List[int] 
    ) -> List[PromptRoleModel]:
        data = [{ "prompt_id": prompt_id, "role_id": role_id } for role_id in role_ids]

        try:
            result = PromptRole.insert_many(data).execute()
            if result:
                return PromptRole.select()
            else:
                return None
        except:
            return None

    def update_prompt_roles_by_prompt(
        self, prompt_id: int, role_ids: List[int]
    ) -> List[PromptRoleModel]:
        try:
            with self.db.atomic():
                # delete everything and reinsert for now since the expected number of roles is still quite small
                delete = PromptRole.delete().where(PromptRole.prompt_id == prompt_id).execute()
                return self.insert_new_prompt_roles_by_prompt(prompt_id, role_ids)
        except:
            return None

    def delete_prompt_roles_by_prompt(self, prompt_id: int) -> bool:
        try:
            query = PromptRole.delete().where(PromptRole.prompt_id == prompt_id)
            query.execute()  # Remove the rows, return number of rows removed.

            return True
        except:
            return False


PromptRoles = PromptRolesTable(DB)
