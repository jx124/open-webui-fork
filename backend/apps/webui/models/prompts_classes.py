from collections import defaultdict
import datetime
from pydantic import BaseModel
import peewee as pw
from playhouse.shortcuts import model_to_dict
from typing import Dict, List, Optional
import time

from apps.webui.models.roles import Role
from apps.webui.models.users import User
from apps.webui.models.evaluations import Evaluation
from apps.webui.models.chats import Chat, ChatModel, Chats

from apps.webui.internal.db import DB

import logging
from config import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

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
    evaluation = pw.ForeignKeyField(Evaluation, null=True)
    model_id = pw.TextField(default="")
    audio = pw.TextField(null=True, default=None)

    class Meta:
        database = DB


class AudioSettings(BaseModel):
    STTEngine: str
    TTSEngine: str
    speaker: str
    model: str


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
    evaluation_id: Optional[int]
    selected_model_id: str = ""  # prevent namespace collision
    evaluation_model_id: str = ""
    audio: Optional[str] = None  # string is json of AudioSettings


def prompt_to_promptmodel(prompt: Prompt, is_admin: bool) -> PromptModel:
    prompt_dict = model_to_dict(prompt)
    if not is_admin:
        prompt_dict["content"] = ""
    evaluation_id = None if prompt_dict.get("evaluation") is None else prompt_dict.get("evaluation", {}).get("id")
    evaluation_model = "" if prompt_dict.get("evaluation") is None else prompt_dict.get("evaluation", {}).get("model_id")
    model_id = prompt_dict.get("model_id")

    return PromptModel(**prompt_dict,
                       evaluation_id=evaluation_id,
                       selected_model_id=model_id,
                       evaluation_model_id=evaluation_model)


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
    evaluation_id: Optional[int]
    selected_model_id: str

    audio: Optional[AudioSettings] = None


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
                    "evaluation_id": form_data.evaluation_id,
                    "selected_model_id": form_data.selected_model_id,
                    "audio": None if form_data.audio is None else form_data.audio.model_dump_json(),
                }
            )

            result = Prompt.create(**prompt.model_dump(exclude={'id'}), model_id=prompt.selected_model_id)
            return prompt_to_promptmodel(result, True)

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_prompt_by_command(self, user_id: str, user_role: str, command: str) -> Optional[PromptModel]:
        try:
            if user_role == "admin":
                prompt = Prompt.get_or_none(Prompt.command == command)

                if prompt:
                    return prompt_to_promptmodel(prompt, True)
                return None

            elif user_role == "instructor":
                prompt = Prompt.select()\
                    .where((Prompt.command == command)
                           & ((Prompt.user_id == user_id) | Prompt.is_visible == True)).get_or_none()

                if prompt:
                    return prompt_to_promptmodel(prompt, True)
                return None

            else:
                return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_prompt_id_by_command(self, command: str) -> Optional[int]:
        try:
            prompt: PromptModel = Prompt.select(Prompt.id).where(Prompt.command == command).get_or_none()
            if prompt:
                return prompt.id
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_prompt_content_by_id(self, id: str) -> Optional[str]:
        try:
            prompt: PromptModel = Prompt.select(Prompt.content).where(Prompt.id == id).get_or_none()
            if prompt:
                return prompt.content
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_prompt_selected_model_by_id(self, id: str) -> Optional[str]:
        try:
            prompt: PromptModel = Prompt.select(Prompt.content).where(Prompt.id == id).get_or_none()
            if prompt:
                return prompt.model_id
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

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
                    .join(StudentClass, on=(Class.id == StudentClass.class_id))\
                    .join(User, on=(StudentClass.student_id == User.id))\
                    .distinct()

            return [prompt_to_promptmodel(prompt, user_role == "admin") for prompt in query]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_prompt_titles(self, user_id: str, user_role: str) -> Dict[int, str]:
        try:
            prompts = []
            if user_role == "admin":
                prompts = Prompt.select(Prompt.id, Prompt.title)

            elif user_role == "instructor":
                prompts = Prompt.select(Prompt.id, Prompt.title)\
                    .where(((Prompt.user_id == user_id) | Prompt.is_visible == True))

            else:
                prompts = Prompt.select(Prompt.id, Prompt.title)\
                    .join(ClassPrompt, on=(Prompt.id == ClassPrompt.prompt_id))\
                    .join(Class, on=(ClassPrompt.class_id == Class.id))\
                    .join(StudentClass, on=(Class.id == StudentClass.class_id))\
                    .join(User, on=(StudentClass.student_id == User.id))\
                    .distinct()

            result = {}
            for prompt in prompts:
                result[prompt.id] = prompt.title
            return result
        except Exception:
            log.exception(" Exception caught in model method.")
            return {}

    def get_profile_titles_by_eval_id(self, eval_id: int) -> List[str]:
        try:
            return [prompt.title for prompt in Prompt.select(Prompt.title).where(Prompt.evaluation == eval_id)]
        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def update_prompt_by_command(
        self, form_data: PromptForm
    ) -> bool:
        try:
            command = f"/{form_data.command}"

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
                    "evaluation_id": form_data.evaluation_id,
                    "selected_model_id": form_data.selected_model_id,
                    "audio": None if form_data.audio is None else form_data.audio.model_dump_json(),
                }
            )

            prompt_id = self.get_prompt_id_by_command(command)
            if prompt_id is None:
                return False

            excluded_columns = {"id", "user_id", "selected_model_id", "evaluation_model_id"}

            query = Prompt.update(**prompt.model_dump(exclude=excluded_columns),
                                  model_id=form_data.selected_model_id)\
                .where(Prompt.command == command)
            result: int = query.execute()

            return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def delete_prompt_by_command(self, user_id: str, user_role: str, command: str) -> bool:
        try:
            prompt = Prompts.get_prompt_by_command(user_id, user_role, command)
            if prompt is None:
                return False

            with self.db.atomic():
                ClassPrompts.delete_class_prompts_by_prompt(prompt.id)
                Prompt.delete().where(Prompt.command == command).execute()

            return True

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def delete_prompt_by_id(self, prompt_id: int) -> bool:
        try:
            with self.db.atomic():
                ClassPrompts.delete_class_prompts_by_prompt(prompt_id)
                Prompt.delete().where(Prompt.id == prompt_id).execute()

            return True

        except Exception:
            log.exception(" Exception caught in model method.")
            return False


Prompts = PromptsTable(DB)


####################
# PromptRole DB Schema
####################


class PromptRole(pw.Model):
    prompt_id = pw.ForeignKeyField(Prompt)
    role_id = pw.ForeignKeyField(Role)

    class Meta:
        database = DB


class PromptRoleModel(BaseModel):
    prompt_id: int
    role_id: int


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
        data = [{"prompt_id": prompt_id, "role_id": role_id} for role_id in role_ids]

        try:
            result = PromptRole.insert_many(data).execute()
            if result:
                prompt_roles: List[PromptRoleModel] = PromptRole.select()
                return prompt_roles
            else:
                return []

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def update_prompt_roles_by_prompt(
        self, prompt_id: int, role_ids: List[int]
    ) -> List[PromptRoleModel]:
        try:
            with self.db.atomic():
                # delete everything and reinsert for now since the expected number of roles is still quite small
                PromptRole.delete().where(PromptRole.prompt_id == prompt_id).execute()
                return self.insert_new_prompt_roles_by_prompt(prompt_id, role_ids)

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def delete_prompt_roles_by_prompt(self, prompt_id: int) -> bool:
        try:
            query = PromptRole.delete().where(PromptRole.prompt_id == prompt_id)
            result: int = query.execute()  # Remove the rows, return number of rows removed.

            return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def delete_prompt_roles_by_role(self, role_id: int) -> bool:
        try:
            query = PromptRole.delete().where(PromptRole.role_id == role_id)
            result: int = query.execute()  # Remove the rows, return number of rows removed.

            return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False


PromptRoles = PromptRolesTable(DB)


####################
# Class DB Schema
####################


class Class(pw.Model):
    id = pw.AutoField()
    name = pw.CharField(null=False, unique=True)
    instructor = pw.ForeignKeyField(User)
    image_url = pw.TextField(default="")

    class Meta:
        database = DB


####################
# ClassPrompt DB Schema
####################


class ClassPrompt(pw.Model):
    class_id = pw.ForeignKeyField(Class)
    prompt_id = pw.ForeignKeyField(Prompt)

    deadline = pw.DateTimeField(null=True)
    allow_multiple_attempts = pw.BooleanField(default=True)
    allow_submit_after_deadline = pw.BooleanField(default=True)

    class Meta:
        database = DB


class ClassPromptModel(BaseModel):
    class_id: int
    prompt_id: int

    deadline: Optional[str] = None
    allow_multiple_attempts: bool = True
    allow_submit_after_deadline: bool = True


class ClassPromptForm(BaseModel):
    class_id: int
    prompt_id: int

    deadline: Optional[str] = None
    allow_multiple_attempts: bool = True
    allow_submit_after_deadline: bool = True


class ClassModel(BaseModel):
    id: int
    name: str
    instructor_id: str
    instructor_name: str
    image_url: str

    assignments: List[ClassPromptModel]
    assigned_students: List[str]


####################
# Class Forms
####################


class ClassForm(BaseModel):
    id: int
    name: str
    instructor_id: str
    image_url: str

    assignments: List[ClassPromptForm]
    assigned_students: List[str]


def class_to_classmodel(cls: Class, assignments: List[ClassPromptModel] = [], students: List[str] = []) -> ClassModel:
    class_dict = model_to_dict(cls)
    return ClassModel(**class_dict,
                      instructor_id=class_dict["instructor"]["id"],
                      instructor_name=class_dict["instructor"]["name"],
                      assignments=assignments,
                      assigned_students=students)


class ClassesTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([Class])

    def get_classes(self, user_id: str, user_role: str) -> List[ClassModel]:
        try:
            query = None
            if user_role == "admin":
                query = Class.select()

            elif user_role == "instructor":
                query = Class.select()\
                    .where(Class.instructor == user_id)

            else:
                query = Class.select()\
                            .join(StudentClass, on=(Class.id == StudentClass.class_id))\
                            .join(User, on=(User.id == StudentClass.student_id))\
                            .where((User.id == user_id))

            assignments = ClassPrompts.get_all_assignments_by_classes()
            students = StudentClasses.get_all_students_by_classes()

            return [class_to_classmodel(class_, assignments[class_.id], students[class_.id]) for class_ in query]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_class_by_name(self, name: str) -> Optional[ClassModel]:
        try:
            class_ = Class.select()\
                .where(Class.name == name).get_or_none()

            if class_ is None:
                return None

            prompts = ClassPrompts.get_assignments_by_class(class_.id)
            students = StudentClasses.get_students_by_class(class_.id)

            return class_to_classmodel(class_, prompts, students)

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_class_by_id(self, user_id: str, user_role: str, class_id: int) -> Optional[ClassModel]:
        try:
            class_ = Class.select()\
                .where((Class.id == class_id) & ((Class.instructor == user_id) | (user_role == "admin"))).get_or_none()

            if class_ is None:
                return None

            prompts = ClassPrompts.get_assignments_by_class(class_.id)
            students = StudentClasses.get_students_by_class(class_.id)

            return class_to_classmodel(class_, prompts, students)

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_class_count_by_instructor_id(self, instructor_id: str) -> Optional[int]:
        try:
            count = Class.select().where(Class.instructor == instructor_id).count()
            return count

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    # Chat methods placed here to prevent circular dependencies
    def get_chat_list_by_user_id_and_instructor(
        self,
        user_id: str,
        instructor_id: str,
        include_archived: bool = False,
    ) -> List[ChatModel]:
        try:
            if include_archived:
                return [
                    ChatModel(**model_to_dict(chat, recurse=False))
                    for chat in Chat.select()
                    .join(Class, pw.JOIN.LEFT_OUTER, on=(Chat.class_id == Class.id))
                    .where((Class.instructor == instructor_id) | (Class.id.is_null() & (Chat.user_id == instructor_id)))
                    .where(Chat.user_id == user_id)
                    .order_by(Chat.updated_at.desc())
                ]
            else:
                return [
                    ChatModel(**model_to_dict(chat, recurse=False))
                    for chat in Chat.select()
                    .join(Class, pw.JOIN.LEFT_OUTER, on=(Chat.class_id == Class.id))
                    .where((Class.instructor == instructor_id) | (Class.id.is_null() & (Chat.user_id == instructor_id)))
                    .where(Chat.archived == False)
                    .where(Chat.user_id == user_id)
                    .order_by(Chat.updated_at.desc())
                ]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_chats_by_instructor(
        self,
        instructor_id: str,
    ) -> List[ChatModel]:
        try:
            return [
                ChatModel(**model_to_dict(chat, recurse=False))
                for chat in Chat.select()
                .join(Class, pw.JOIN.LEFT_OUTER, on=(Chat.class_id == Class.id))
                .where((Class.instructor == instructor_id) | (Class.id.is_null() & (Chat.user_id == instructor_id)))
                .order_by(Chat.updated_at.desc())
            ]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_chat_by_id_and_instructor(self, id: str, instructor_id: str) -> Optional[ChatModel]:
        try:
            chat = Chat.select()\
                .join(Class, pw.JOIN.LEFT_OUTER, on=(Chat.class_id == Class.id))\
                .where((Class.instructor == instructor_id) | (Class.id.is_null() & (Chat.user_id == instructor_id)))\
                .where(Chat.id == id)\
                .get_or_none()

            if chat:
                return ChatModel(**model_to_dict(chat, recurse=False))
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_chats_by_class_id(self, class_id: str) -> List[ChatModel]:
        try:
            return [
                ChatModel(**model_to_dict(chat, recurse=False))
                for chat in Chat.select()
                .join(Class, on=(Chat.class_id == Class.id))
                .where(Class.id == class_id)
            ]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_chats_by_class_id_and_instructor(self, class_id: str, instructor_id: str) -> List[ChatModel]:
        try:
            return [
                ChatModel(**model_to_dict(chat, recurse=False))
                for chat in Chat.select()
                .join(Class, on=(Chat.class_id == Class.id))
                .where((Class.id == class_id) & (Class.instructor == instructor_id))
            ]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_class_name(self, class_id: str) -> Optional[str]:
        try:
            class_: Optional[ClassModel] = Class.select(Class.name).where(Class.id == class_id).get_or_none()
            if class_:
                return class_.name
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def insert_new_class(self, form_data: ClassForm) -> Optional[ClassModel]:
        try:
            with self.db.atomic():
                result = Class.create(**form_data.model_dump(exclude={"id", "assignments", "assigned_students"}))
                assignments = ClassPrompts.insert_new_assignments(result.id, form_data.assignments)
                StudentClasses.insert_new_student_classes_by_class(result.id, form_data.assigned_students)

                return class_to_classmodel(result, assignments, form_data.assigned_students)

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def update_class_by_id(self, form_data: ClassForm) -> bool:
        excluded_columns = {"id", "assignments", "assigned_students"}

        try:
            with self.db.atomic():
                ClassPrompts.update_class_prompts_by_class(form_data.id, form_data.assignments)
                StudentClasses.update_student_classes_by_class(form_data.id, form_data.assigned_students)
                Class.update(**form_data.model_dump(exclude=excluded_columns)).where(Class.id == form_data.id).execute()

            return True

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def delete_class_by_id(self, class_id: int) -> bool:
        try:
            with self.db.atomic():
                Chats.remove_class_reference(class_id)
                ClassPrompts.delete_class_prompts_by_class(class_id)
                StudentClasses.delete_student_classes_by_class(class_id)
                Class.delete().where(Class.id == class_id).execute()

            return True

        except Exception:
            log.exception(" Exception caught in model method.")
            return False


Classes = ClassesTable(DB)


####################
# StudentClass DB Schema
####################


class StudentClass(pw.Model):
    student_id = pw.ForeignKeyField(User)
    class_id = pw.ForeignKeyField(Class)

    class Meta:
        database = DB


class StudentClassModel(BaseModel):
    student_id: str
    class_id: int


####################
# StudentClass Forms
####################


class StudentClassesTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([StudentClass])

    def insert_new_student_classes_by_student(
        self, student_id: str, class_ids: List[int]
    ) -> List[StudentClassModel]:
        data = [{"student_id": student_id, "class_id": class_id} for class_id in class_ids]

        try:
            result = StudentClass.insert_many(data).execute()
            if result:
                student_classes: List[StudentClassModel] = StudentClass.select()
                return student_classes
            else:
                return []

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def insert_new_student_classes_by_class(
        self, class_id: int, student_ids: List[str]
    ) -> List[StudentClassModel]:
        data = [{"student_id": student_id, "class_id": class_id} for student_id in student_ids]

        try:
            result = StudentClass.insert_many(data).execute()
            if result:
                student_classes: List[StudentClassModel] = StudentClass.select()
                return student_classes
            else:
                return []

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_classes_by_student(self, student_id: str) -> List[int]:
        try:
            query = StudentClass.select(StudentClass.student_id, StudentClass.class_id)\
                .where(StudentClass.student_id == student_id)
            return [row.class_id.id for row in query]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_students_by_class(self, class_id: int) -> List[str]:
        try:
            query = StudentClass.select(StudentClass.student_id, StudentClass.class_id)\
                .where(StudentClass.class_id == class_id)
            return [row.student_id.id for row in query]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_all_classes_by_students(self) -> defaultdict[str, List[int]]:
        # returns defaultdict of student_id -> [class_ids]
        try:
            query = StudentClass.select(StudentClass.student_id, StudentClass.class_id)
            result = defaultdict(lambda: [])

            for row in query:
                result[row.student_id.id].append(row.class_id.id)

            return result

        except Exception:
            log.exception(" Exception caught in model method.")
            return defaultdict(lambda: [])

    def get_all_students_by_classes(self) -> defaultdict[int, List[str]]:
        # returns defaultdict of class_id -> [student_ids]
        try:
            query = StudentClass.select(StudentClass.student_id, StudentClass.class_id)
            result = defaultdict(lambda: [])

            for row in query:
                result[row.class_id.id].append(row.student_id.id)

            return result

        except Exception:
            log.exception(" Exception caught in model method.")
            return defaultdict(lambda: [])

    def update_student_classes_by_student(
        self, student_id: str, class_ids: List[int]
    ) -> List[StudentClassModel]:
        try:
            with self.db.atomic():
                # delete everything and reinsert for now since the expected no. of classes/students is still quite small
                StudentClass.delete().where(StudentClass.student_id == student_id).execute()
                return self.insert_new_student_classes_by_student(student_id, class_ids)

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def update_student_classes_by_class(
        self, class_id: int, student_ids: List[str]
    ) -> List[StudentClassModel]:
        try:
            with self.db.atomic():
                # delete everything and reinsert for now since the expected no. of classes/students is still quite small
                StudentClass.delete().where(StudentClass.class_id == class_id).execute()
                return self.insert_new_student_classes_by_class(class_id, student_ids)

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def delete_student_classes_by_student(self, student_id: str) -> bool:
        try:
            query = StudentClass.delete().where(StudentClass.student_id == student_id)
            result: int = query.execute()  # Remove the rows, return number of rows removed.

            return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def delete_student_classes_by_class(self, class_id: int) -> bool:
        try:
            query = StudentClass.delete().where(StudentClass.class_id == class_id)
            result: int = query.execute()  # Remove the rows, return number of rows removed.

            return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False


StudentClasses = StudentClassesTable(DB)


####################
# ClassPrompt Forms
####################


def classprompt_to_classprompt_model(classprompt: ClassPrompt) -> ClassPromptModel:
    classprompt_dict = model_to_dict(classprompt, recurse=False, exclude=[ClassPrompt.deadline])
    date_str = classprompt.deadline

    # postgres has a datetime type, but sqlite stores it as a string
    if date_str is not None and type(date_str) is not str:
        date_str = classprompt.deadline.isoformat() if classprompt.deadline is not None else None

    result = ClassPromptModel(**classprompt_dict, deadline=date_str)
    return result


class ClassPromptsTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([ClassPrompt])

    def insert_new_assignments(
        self, class_id: int, assignments: List[ClassPromptForm]
    ) -> List[ClassPromptModel]:
        data = [
            {
                "class_id": class_id,
                "prompt_id": assignment.prompt_id,
                "deadline": assignment.deadline,
                "allow_multiple_attempts": assignment.allow_multiple_attempts,
                "allow_submit_after_deadline": assignment.allow_submit_after_deadline,
            } for assignment in assignments]

        try:
            result = ClassPrompt.insert_many(data).execute()
            if result:
                return [
                    classprompt_to_classprompt_model(row)
                    for row in ClassPrompt.select().where(ClassPrompt.class_id == class_id)
                ]
            else:
                return []

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_assignments_by_class(self, class_id: int) -> List[ClassPromptModel]:
        try:
            query = ClassPrompt.select().where(ClassPrompt.class_id == class_id)
            return [classprompt_to_classprompt_model(row) for row in query]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_all_classes_by_prompts(self) -> defaultdict[int, List[int]]:
        # returns defaultdict of prompt_id -> [class_ids]
        try:
            query = ClassPrompt.select(ClassPrompt.prompt_id, ClassPrompt.class_id)
            result = defaultdict(lambda: [])

            for row in query:
                result[row.prompt_id.id].append(row.class_id.id)

            return result

        except Exception:
            log.exception(" Exception caught in model method.")
            return defaultdict(lambda: [])

    def get_all_assignments_by_classes(self) -> defaultdict[int, List[ClassPromptModel]]:
        # returns defaultdict of class_id -> [ClassPromptModel]
        try:
            query = ClassPrompt.select()
            result = defaultdict(lambda: [])

            for row in query:
                result[row.class_id.id].append(classprompt_to_classprompt_model(row))

            return result

        except Exception:
            log.exception(" Exception caught in model method.")
            return defaultdict(lambda: [])

    def get_all_assignments_by_classes_and_instructor(self, instructor_id: str) -> defaultdict[int, List[ClassPromptModel]]:
        # returns defaultdict of class_id -> [ClassPromptModel]
        try:
            query = ClassPrompt.select()\
                .join(Class, on=(ClassPrompt.class_id == Class.id))\
                .where(Class.instructor == instructor_id)
            result = defaultdict(lambda: [])

            for row in query:
                result[row.class_id.id].append(classprompt_to_classprompt_model(row))

            return result

        except Exception:
            log.exception(" Exception caught in model method.")
            return defaultdict(lambda: [])

    def check_assignment_before_deadline(self, chat_id: str) -> bool:
        try:
            chat = Chat.select(Chat.class_id, Chat.prompt_id).where((Chat.id == chat_id)).get_or_none()
            if chat is None:
                return False

            assignment = ClassPrompt.select().where(
                (ClassPrompt.class_id == chat.class_id) & (ClassPrompt.prompt_id == chat.prompt_id)).get_or_none()
            if assignment is None:
                return False

            if assignment.allow_submit_after_deadline:
                return True

            unparsed_deadline: Optional[str | datetime.datetime] = assignment.deadline
            deadline: datetime.datetime

            if unparsed_deadline is None:
                return True

            # postgres has a datetime type, but sqlite stores it as a string
            if type(unparsed_deadline) is not datetime.datetime:
                deadline = datetime.datetime.fromisoformat(assignment.deadline)
            else:
                deadline = unparsed_deadline

            return datetime.datetime.now() <= deadline

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def get_assignment_submission_by_class_and_user_id(self, class_id: int, user_id: str) -> Dict[int, bool]:
        # returns a dict mapping prompt_id -> submission status
        try:
            prompts = ClassPrompt.select(ClassPrompt.prompt_id).where(ClassPrompt.class_id == class_id)
            result = {prompt.prompt_id.id: False for prompt in prompts}

            submitted = ClassPrompt.select(ClassPrompt.prompt_id)\
                .join(Chat, on=((Chat.class_id == ClassPrompt.class_id) & (Chat.prompt_id == ClassPrompt.prompt_id)))\
                .where((Chat.is_submitted) & (Chat.user_id == user_id) & (Chat.class_id == class_id))

            for chat in submitted:
                result[chat.prompt_id.id] = True

            return result

        except Exception:
            log.exception(" Exception caught in model method.")
            return {}

    def update_class_prompts_by_class(
        self, class_id: int, assignments: List[ClassPromptForm]
    ) -> List[ClassPromptModel]:
        try:
            with self.db.atomic():
                # delete everything and reinsert for now since the expected no. of classes/prompts is still quite small
                ClassPrompt.delete().where(ClassPrompt.class_id == class_id).execute()
                return self.insert_new_assignments(class_id, assignments)

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def delete_class_prompts_by_prompt(self, prompt_id: int) -> bool:
        try:
            query = ClassPrompt.delete().where(ClassPrompt.prompt_id == prompt_id)
            query.execute()  # Remove the rows, return number of rows removed.

            return True

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def delete_class_prompts_by_class(self, class_id: int) -> bool:
        try:
            query = ClassPrompt.delete().where(ClassPrompt.class_id == class_id)
            query.execute()  # Remove the rows, return number of rows removed.

            return True

        except Exception:
            log.exception(" Exception caught in model method.")
            return False


ClassPrompts = ClassPromptsTable(DB)
