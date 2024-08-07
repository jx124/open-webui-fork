from pydantic import BaseModel
import peewee as pw
from playhouse.shortcuts import model_to_dict
from typing import List, Union, Optional
import time

from apps.webui.models.roles import Role
from apps.webui.models.users import User
from apps.webui.models.evaluations import Evaluation
from apps.webui.models.models import Model
from apps.webui.models.classes import Class, StudentClass

from apps.webui.internal.db import DB

####################
# Prompts DB Schema
####################


class Prompt(pw.Model):
    command = pw.CharField(unique=True)
    user_id = pw.CharField()
    title = pw.TextField()
    content = pw.TextField()
    timestamp = pw.BigIntegerField()
    is_visible = pw.BooleanField(default=True)
    additional_info = pw.TextField(default="")

    image_url = pw.TextField(default="")
    deadline = pw.BigIntegerField(null=True)
    evaluation = pw.ForeignKeyField(Evaluation, null=True)
    model = pw.ForeignKeyField(Model, null=True)

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

    image_url: str = ""
    deadline: Optional[int]
    evaluation_id: Optional[int]
    selected_model_id: Optional[str]  # prevent namespace collision


def prompt_to_promptmodel(prompt: pw.Model) -> PromptModel:
    # flattens the prompt dict so "evaluation_id" and "model_id" is visible to PromptModel
    prompt_dict = model_to_dict(prompt)
    evaluation_id = None if prompt_dict.get("evaluation") is None else prompt_dict.get("evaluation", {}).get("id")
    model_id = None if prompt_dict.get("model") is None else prompt_dict.get("model", {}).get("id")
    
    return PromptModel(**prompt_dict,
                       evaluation_id=evaluation_id,
                       selected_model_id=model_id)


####################
# PromptRole DB Schema
####################

# Schema placed here to prevent circular dependencies

class PromptRole(Model):
    prompt_id = pw.ForeignKeyField(Prompt)
    role_id = pw.ForeignKeyField(Role)

    class Meta:
        database = DB


class PromptRoleModel(BaseModel):
    prompt_id: int
    role_id: int


####################
# ClassPrompt DB Schema
####################


class ClassPrompt(Model):
    class_id = pw.ForeignKeyField(Class)
    prompt_id = pw.ForeignKeyField(Prompt)

    class Meta:
        database = DB


####################
# Prompt Forms
####################


class PromptForm(BaseModel):
    command: str
    title: str
    content: str
    is_visible: bool
    additional_info: str

    image_url: str = ""
    deadline: Optional[int]
    evaluation_id: Optional[int]
    selected_model_id: Optional[str]


class PromptsTable:

    def __init__(self, db):
        self.db = db
        self.db.create_tables([Prompt])

    def insert_new_prompt(self, user_id: str, form_data: PromptForm) -> Optional[PromptModel]:
        try:
            prompt = PromptModel(
                **{
                    "id": 0,
                    "timestamp": int(time.time()),
                    "user_id": user_id,

                    "command": form_data.command,
                    "title": form_data.title,
                    "content": form_data.content,
                    "is_visible": form_data.is_visible,
                    "additional_info": form_data.additional_info,
                    "image_url": form_data.image_url,
                    "deadline": form_data.deadline,
                    "evaluation_id": form_data.evaluation_id,
                    "selected_model_id": form_data.selected_model_id
                }
            )

            result = Prompt.create(**prompt.model_dump(exclude={'id'}))
            if result:
                return prompt_to_promptmodel(result)
            return None
        except:
            return None

    def get_prompt_by_command(self, user_id: str, user_role: str, command: str) -> Optional[PromptModel]:
        try:
            if user_role == "admin":
                prompt = Prompt.get(Prompt.command == command)
                return prompt_to_promptmodel(prompt)

            elif user_role == "instructor":
                prompt = Prompt.select()\
                    .where((Prompt.command == command)
                           & ((Prompt.user_id == user_id) | Prompt.is_visible == True)).get()
                return prompt_to_promptmodel(prompt)

            else:
                return None
        except:
            return None

    def get_prompts(self, user_id: str, user_role: str) -> List[PromptModel]:
        query = None
        if user_role == "admin":
            query = Prompt.select()

        elif user_role == "instructor":
            query = Prompt.select().where(((Prompt.user_id == user_id) | Prompt.is_visible == True))

        else:
            query = Prompt.select()\
                .join(ClassPrompt, on=(Prompt.id == ClassPrompt.prompt_id))\
                .join(Class, on=(ClassPrompt.class_id == Class.id))\
                .join(StudentClass, on=(Class.class_id == StudentClass.id))\
                .join(User, on=(StudentClass.user_id == User.id))\
                .distinct()

        return [prompt_to_promptmodel(prompt) for prompt in query]
    
    def update_prompt_by_command(
        self, user_id: str, user_role: str, form_data: PromptForm
    ) -> bool:
        try:
            command = f"/{form_data.command}"
            result = None

            prompt = PromptModel(
                **{
                    "id": 0,
                    "command": command,
                    "user_id": "",
                    "timestamp": int(time.time()),

                    "title": form_data.title,
                    "content": form_data.content,
                    "is_visible": form_data.is_visible,
                    "additional_info": form_data.additional_info,
                    "image_url": form_data.image_url,
                    "deadline": form_data.deadline,
                    "evaluation_id": form_data.evaluation_id,
                    "selected_model_id": form_data.selected_model_id
                }
            )

            if user_role == "admin":
                query = Prompt.update(**prompt.model_dump(exclude={"id", "user_id", "selected_model_id"}),
                                      model_id=form_data.selected_model_id)\
                    .where(Prompt.command == command)
                result = query.execute()

            elif user_role == "instructor":
                query = Prompt.update(**prompt.model_dump(exclude={"id", "user_id", "selected_model_id"}),
                                      model_id=form_data.selected_model_id)\
                    .where((Prompt.command == command) & 
                           ((Prompt.user_id == user_id) | Prompt.is_visible == True))
                result = query.execute()

            if result:
                return True

            return False
        except:
            return False

    def delete_prompt_by_command(self, user_id: str, user_role: str, command: str) -> bool:
        try:
            prompt = Prompts.get_prompt_by_command(user_id, user_role, command)
            if not prompt:
                return False

            result = None
            if user_role == "admin":
                query = Prompt.delete().where(Prompt.command == command)
                result = query.execute()

            elif user_role == "instructor":
                query = Prompt.delete()\
                    .where((Prompt.command == command) & 
                           ((Prompt.user_id == user_id) | Prompt.is_visible == True))
                result = query.execute()

            if result:
                return True
            return False
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
                PromptRole.delete().where(PromptRole.prompt_id == prompt_id).execute()
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

    def delete_prompt_roles_by_role(self, role_id: int) -> bool:
        try:
            query = PromptRole.delete().where(PromptRole.role_id == role_id)
            query.execute()  # Remove the rows, return number of rows removed.

            return True
        except:
            return False

PromptRoles = PromptRolesTable(DB)


####################
# ClassPrompt Forms
####################


class ClassPromptsTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([ClassPrompt])


ClassPrompts = ClassPromptsTable(DB)