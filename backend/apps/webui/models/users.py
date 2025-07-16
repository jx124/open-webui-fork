from pydantic import BaseModel, ConfigDict
import peewee as pw
from playhouse.shortcuts import model_to_dict
from typing import List, Optional, Dict
import time

from apps.webui.internal.db import DB, JSONField
from apps.webui.models.roles import Role, RoleModel

import logging
from config import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# User DB Schema
####################


class User(pw.Model):
    id = pw.CharField(unique=True, primary_key=True)
    name = pw.CharField()
    email = pw.CharField()
    role_id = pw.ForeignKeyField(Role, backref="users", default=1)
    profile_image_url = pw.TextField()

    last_active_at = pw.BigIntegerField()
    updated_at = pw.BigIntegerField()
    created_at = pw.BigIntegerField()

    api_key = pw.CharField(null=True, unique=True)
    settings = JSONField(null=True)

    token_count = pw.BigIntegerField(default=0)
    attempts = pw.BigIntegerField(default=0)
    session_time = pw.BigIntegerField(default=0)

    class Meta:
        database = DB


class UserSettings(BaseModel):
    ui: Optional[dict[str, object]] = {}
    model_config = ConfigDict(extra="allow")
    pass


class UserModel(BaseModel):
    id: str
    name: str
    email: str
    role: str = "pending"  # role is stored in DB as a foreign key, but expanded to actual role name when returned
    profile_image_url: str

    last_active_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch
    created_at: int  # timestamp in epoch

    api_key: Optional[str] = None
    settings: Optional[UserSettings] = None


class UserStatistics(BaseModel):
    token_count: int
    attempts: int
    session_time: int


class UserProfile(BaseModel):
    name: str
    profile_image_url: str


####################
# Forms
####################


class UserRoleUpdateForm(BaseModel):
    id: str
    role: str


class UserUpdateForm(BaseModel):
    name: str
    email: str
    profile_image_url: str
    password: Optional[str] = None


class UserImportForm(BaseModel):
    name: str
    email: str
    role: str
    password: Optional[str] = None


def user_to_usermodel(user: User) -> UserModel:
    # flattens the user dict so "role" is visible to UserModel
    user_dict = model_to_dict(user)
    return UserModel(**user_dict, role=user_dict["role_id"]["name"])


class UsersTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([User])

    def insert_new_user(
        self,
        id: str,
        name: str,
        email: str,
        profile_image_url: str = "/user.png",
        role: str = "pending",
    ) -> Optional[UserModel]:
        try:
            role_model: RoleModel = Role.get_or_none(Role.name == role)

            if role_model is None:
                return None

            user = UserModel(
                **{
                    "id": id,
                    "name": name,
                    "email": email,
                    "role": role_model.name,
                    "profile_image_url": profile_image_url,
                    "last_active_at": int(time.time()),
                    "created_at": int(time.time()),
                    "updated_at": int(time.time())
                }
            )
            result = User.create(**user.model_dump(exclude={"role"}), role_id=role_model.id)
            if result:
                return user
            else:
                return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_user_by_id(self, id: str) -> Optional[UserModel]:
        try:
            user = User.get_or_none(User.id == id)
            if user:
                return user_to_usermodel(user)
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_user_by_api_key(self, api_key: str) -> Optional[UserModel]:
        try:
            user = User.get_or_none(User.api_key == api_key)
            if user:
                return user_to_usermodel(user)
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        try:
            user = User.get_or_none(User.email == email)
            if user:
                return user_to_usermodel(user)
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_users(self) -> List[UserModel]:
        try:
            return [
                user_to_usermodel(user)
                for user in User.select().join(Role)
            ]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_user_profiles(self) -> Dict[str, UserProfile]:
        try:
            query = User.select(User.id, User.name, User.profile_image_url)
            result = {}
            for user in query:
                result[user.id] = UserProfile(name=user.name, profile_image_url=user.profile_image_url)

            return result

        except Exception:
            log.exception(" Exception caught in model method.")
            return {}

    def get_user_names(self) -> Dict[str, str]:
        try:
            query = User.select(User.id, User.name)
            result = {}
            for user in query:
                result[user.id] = user.name

            return result

        except Exception:
            log.exception(" Exception caught in model method.")
            return {}

    def get_user_statistics(self) -> Dict[str, UserStatistics]:
        try:
            stats: Dict[str, UserStatistics] = {}

            query = User.select(User.id, User.token_count, User.attempts, User.session_time)
            for user in query:
                stats[user.id] = UserStatistics(
                    token_count=user.token_count,
                    attempts=user.attempts,
                    session_time=user.session_time
                )
            return stats

        except Exception:
            log.exception(" Exception caught in model method.")
            return {}

    def get_num_users(self) -> Optional[int]:
        try:
            count: int = User.select().count()
            return count

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_first_user(self) -> Optional[UserModel]:
        try:
            user = User.select().join(Role).order_by(User.created_at).first()
            return user_to_usermodel(user)

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_users_by_role_id(self, role_id: int) -> List[UserModel]:
        try:
            return [
                user_to_usermodel(user)
                for user in User.select().join(Role).where(Role.id == role_id)
            ]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_num_users_by_role_id(self, role_id: int) -> Optional[int]:
        try:
            count: int = User.select().join(Role).where(Role.id == role_id).count()
            return count

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def update_user_role_by_id(self, id: str, role: str) -> Optional[UserModel]:
        try:
            role_model: RoleModel
            role_model, _ = Role.get_or_create(name=role.strip())

            query = User.update(role_id=role_model.id).where(User.id == id)
            result = query.execute()

            if result:
                user = User.get_or_none(User.id == id)
                return user_to_usermodel(user)
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def update_user_profile_image_url_by_id(self, id: str, profile_image_url: str) -> Optional[UserModel]:
        try:
            query = User.update(profile_image_url=profile_image_url).where(
                User.id == id
            )
            result = query.execute()

            if result:
                user = User.get_or_none(User.id == id)
                return user_to_usermodel(user)
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def update_user_last_active_by_id(self, id: str) -> Optional[UserModel]:
        try:
            query = User.update(last_active_at=int(time.time())).where(User.id == id)
            result = query.execute()

            if result:
                user = User.get_or_none(User.id == id)
                return user_to_usermodel(user)
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def update_user_by_id(self, id: str, updated: dict[str, object]) -> Optional[UserModel]:
        try:
            query = User.update(**updated).where(User.id == id)
            result = query.execute()

            if result:
                user = User.get_or_none(User.id == id)
                return user_to_usermodel(user)
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def delete_user_by_id(self, id: str) -> bool:
        try:
            query = User.delete().where(User.id == id)
            delete_result: int = query.execute()  # Remove the rows, return number of rows removed.

            return delete_result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def update_user_api_key_by_id(self, id: str, api_key: Optional[str]) -> bool:
        try:
            query = User.update(api_key=api_key).where(User.id == id)
            result: int = query.execute()

            return result == 1

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def get_user_api_key_by_id(self, id: str) -> Optional[str]:
        try:
            user: Optional[UserModel] = User.get_or_none(User.id == id)
            if user:
                return user.api_key
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def increment_user_token_count_by_id(self, id: str, count: int) -> bool:
        try:
            query = User.update(token_count=User.token_count + count).where(User.id == id)
            result: int = query.execute()

            return result == 1

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def increment_user_chat_attempts_by_id(self, id: str) -> bool:
        try:
            query = User.update(attempts=User.attempts + 1).where(User.id == id)
            result: int = query.execute()

            return result == 1

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def increment_user_session_time_by_id(self, id: str, amount: int) -> bool:
        try:
            query = User.update(session_time=User.session_time + amount).where(User.id == id)
            result: int = query.execute()

            return result == 1

        except Exception:
            log.exception(" Exception caught in model method.")
            return False


Users = UsersTable(DB)
