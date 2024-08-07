from collections import defaultdict
from pydantic import BaseModel
import peewee as pw
from playhouse.shortcuts import model_to_dict
from typing import Dict, List, Union, Optional
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
    id = pw.AutoField()
    command = pw.CharField(unique=True)
    user_id = pw.CharField()
    title = pw.TextField()
    content = pw.TextField()
    timestamp = pw.BigIntegerField()
    is_visible = pw.BooleanField(default=True)
    additional_info = pw.TextField(default="")

    image_url = pw.TextField(default="")
    deadline = pw.DateTimeField(null=True)
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
    deadline: Optional[str]
    evaluation_id: Optional[int]
    selected_model_id: Optional[str]  # prevent namespace collision

    assigned_classes: List[int]


def prompt_to_promptmodel(prompt: pw.Model, classes: List[int] = []) -> PromptModel:
    # flattens the prompt dict so "evaluation_id" and "model_id" is visible to PromptModel
    prompt_dict = model_to_dict(prompt)
    evaluation_id = None if prompt_dict.get("evaluation") is None else prompt_dict.get("evaluation", {}).get("id")
    model_id = None if prompt_dict.get("model") is None else prompt_dict.get("model", {}).get("id")
    
    return PromptModel(**prompt_dict,
                        evaluation_id=evaluation_id,
                        selected_model_id=model_id,
                        assigned_classes=classes)

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


class ClassPromptModel(BaseModel):
    class_id: int
    prompt_id: int


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
    deadline: Optional[str]
    evaluation_id: Optional[int]
    selected_model_id: Optional[str]

    assigned_classes: List[int]


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
                    "selected_model_id": form_data.selected_model_id,
                    "assigned_classes": form_data.assigned_classes,
                }
            )

            with self.db.atomic():
                result = Prompt.create(**prompt.model_dump(exclude={'id'}))
                if result:
                    ClassPrompts.insert_new_class_prompts_by_prompt(result.id, form_data.assigned_classes)

                    return prompt_to_promptmodel(result)
            return None
        except:
            return None

    def get_prompt_by_command(self, user_id: str, user_role: str, command: str) -> Optional[PromptModel]:
        try:
            classes = []
            if user_role == "admin":
                prompt = Prompt.get(Prompt.command == command)

                if prompt:
                    classes = ClassPrompts.get_classes_by_prompt(prompt.id)

                return prompt_to_promptmodel(prompt, classes)

            elif user_role == "instructor":
                prompt = Prompt.select()\
                    .where((Prompt.command == command)
                           & ((Prompt.user_id == user_id) | Prompt.is_visible == True)).get()
                
                if prompt:
                    classes = ClassPrompts.get_classes_by_prompt(prompt.id)
                
                return prompt_to_promptmodel(prompt, classes)

            else:
                return None
        except:
            return None
        
    def get_prompt_id_by_command(self, command: str) -> Optional[int]:
        try:
            return Prompt.select(Prompt.id).where(Prompt.command == command).get()
        except:
            return None

    # TODO: define list model with less info
    def get_prompts(self, user_id: str, user_role: str) -> List[PromptModel]:
        try:
            query = None
            if user_role == "admin":
                query = Prompt.select()

            elif user_role == "instructor":
                query = Prompt.select()\
                    .where(((Prompt.user_id == user_id) | Prompt.is_visible == True))

            else:
                query = Prompt.select()\
                    .join(ClassPrompt, on=(Prompt.id == ClassPrompt.prompt_id))\
                    .join(Class, on=(ClassPrompt.class_id == Class.id))\
                    .join(StudentClass, on=(Class.class_id == StudentClass.id))\
                    .join(User, on=(StudentClass.user_id == User.id))\
                    .distinct()
                
            result = ClassPrompts.get_all_classes_by_prompts()

            return [prompt_to_promptmodel(prompt, result[prompt.id]) for prompt in query]
        except:
            return None

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
                    "assigned_classes": [],

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

            prompt_id = self.get_prompt_id_by_command(command)
            if prompt_id is None:
                return False

            excluded_columns = {"id", "user_id", "selected_model_id", "assigned_classes"}

            with self.db.atomic():
                if user_role == "admin":
                    query = Prompt.update(**prompt.model_dump(exclude=excluded_columns),
                                        model_id=form_data.selected_model_id)\
                        .where(Prompt.command == command)
                    result = query.execute()

                elif user_role == "instructor":
                    query = Prompt.update(**prompt.model_dump(exclude=excluded_columns),
                                        model_id=form_data.selected_model_id)\
                        .where((Prompt.command == command) & 
                            ((Prompt.user_id == user_id) | Prompt.is_visible == True))
                    result = query.execute()

                if result:
                    ClassPrompts.update_class_prompts_by_prompt(prompt_id, form_data.assigned_classes)

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
            with self.db.atomic():
                ClassPrompts.delete_class_prompts_by_prompt(prompt.id)

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

    def insert_new_class_prompts_by_prompt(
        self, prompt_id: int, class_ids: List[int] 
    ) -> List[ClassPromptModel]:
        data = [{ "class_id": class_id, "prompt_id": prompt_id } for class_id in class_ids]

        try:
            result = ClassPrompt.insert_many(data).execute()
            if result:
                return ClassPrompt.select()
            else:
                return None
        except:
            return None
 
    def get_classes_by_prompt(self, prompt_id: int) -> List[int]:
        try:
            query = ClassPrompt.select(ClassPrompt.prompt_id, ClassPrompt.class_id).where(ClassPrompt.prompt_id == prompt_id)
            return [row.class_id.id for row in query]
        except:
            return []
    
    def get_all_classes_by_prompts(self):
        # returns defaultdict of prompt_id -> [class_ids]
        try:
            query = ClassPrompt.select(ClassPrompt.prompt_id, ClassPrompt.class_id)
            result = defaultdict(lambda: [])

            for row in query:
                result[row.prompt_id.id].append(row.class_id.id)

            return result
        except:
            return {}


    def update_class_prompts_by_prompt(
        self, prompt_id: int, role_ids: List[int]
    ) -> List[ClassPromptModel]:
        try:
            with self.db.atomic():
                # delete everything and reinsert for now since the expected number of roles is still quite small
                ClassPrompt.delete().where(ClassPrompt.prompt_id == prompt_id).execute()
                return self.insert_new_class_prompts_by_prompt(prompt_id, role_ids)
        except:
            return None

    def delete_class_prompts_by_prompt(self, prompt_id: int) -> bool:
        try:
            query = ClassPrompt.delete().where(ClassPrompt.prompt_id == prompt_id)
            query.execute()  # Remove the rows, return number of rows removed.

            return True
        except:
            return False

    def delete_class_prompts_by_class(self, class_id: int) -> bool:
        try:
            query = ClassPrompt.delete().where(ClassPrompt.class_id == class_id)
            query.execute()  # Remove the rows, return number of rows removed.

            return True
        except:
            return False


ClassPrompts = ClassPromptsTable(DB)