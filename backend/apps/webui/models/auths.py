import datetime
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid
import peewee as pw

from apps.webui.models.users import UserModel, Users
from utils.utils import verify_password

from apps.webui.internal.db import DB

import logging
from config import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# DB MODEL
####################


class Auth(pw.Model):
    id = pw.CharField(unique=True)
    email = pw.CharField()
    password = pw.TextField()
    active = pw.BooleanField()
    otp_value = pw.IntegerField()
    otp_expiry = pw.TimestampField()

    class Meta:
        database = DB


class AuthModel(BaseModel):
    id: str
    email: str
    password: str
    active: bool = True


####################
# Forms
####################


class Token(BaseModel):
    token: str
    token_type: str


class ApiKey(BaseModel):
    api_key: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    profile_image_url: str


class SigninResponse(Token, UserResponse):
    pass


class SigninForm(BaseModel):
    email: str
    password: str


class ResetPasswordForm(BaseModel):
    email: str


class ResetOTPForm(BaseModel):
    OTP: str
    email: str


class ResetPasswordOTPForm(BaseModel):
    OTP: str
    email: str
    password: str


class ProfileImageUrlForm(BaseModel):
    profile_image_url: str


class UpdateProfileForm(BaseModel):
    profile_image_url: str
    name: str


class UpdatePasswordForm(BaseModel):
    password: str
    new_password: str


class SignupForm(BaseModel):
    name: str
    email: str
    password: str
    profile_image_url: Optional[str] = "/user.png"


class AddUserForm(SignupForm):
    role: Optional[str] = "pending"


class AuthsTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([Auth])

    def insert_new_auth(
        self,
        email: str,
        password: str,
        name: str,
        profile_image_url: Optional[str] = "/user.png",
        role: Optional[str] = "pending",
    ) -> Optional[UserModel]:
        log.info("insert_new_auth")
        try:
            id = str(uuid.uuid4())

            auth = AuthModel(
                **{"id": id, "email": email, "password": password, "active": True}
            )
            result = Auth.create(**auth.model_dump())

            user = Users.insert_new_user(id, name, email,
                                         profile_image_url if profile_image_url is not None else "/user.png",
                                         role.strip() if role is not None else "pending")

            if result and user:
                return user
            else:
                return None
        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        log.info(f"authenticate_user: {email}")
        try:
            auth = Auth.get_or_none(Auth.email == email, Auth.active == True)
            if auth:
                if verify_password(password, auth.password):
                    user = Users.get_user_by_id(auth.id)
                    return user
                else:
                    return None
            else:
                return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def authenticate_user_by_api_key(self, api_key: str) -> Optional[UserModel]:
        log.info(f"authenticate_user_by_api_key: {api_key}")
        # if no api_key, return None
        if not api_key:
            return None

        try:
            user = Users.get_user_by_api_key(api_key)
            return user

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def authenticate_user_by_trusted_header(self, email: str) -> Optional[UserModel]:
        log.info(f"authenticate_user_by_trusted_header: {email}")
        try:
            auth = Auth.get_or_none(Auth.email == email, Auth.active == True)
            if auth:
                user = Users.get_user_by_id(auth.id)
                return user
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def authenticate_user_otp(self, id: str, otp: str) -> Optional[bool]:
        try:
            auth = Auth.get_or_none(Auth.id == id)
            if auth:
                if auth.otp_value is None:
                    return False

                now = datetime.datetime.now()

                if (str(auth.otp_value).zfill(6) != otp) or (auth.otp_expiry <= now):
                    return False
                return True

            return False

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def update_user_password_by_id(self, id: str, new_password: str) -> Optional[bool]:
        try:
            query = Auth.update(password=new_password).where(Auth.id == id)
            result: int = query.execute()

            return result == 1

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def update_user_otp_by_id(self, id: str, otp: int, expiry: int) -> Optional[bool]:
        try:
            query = Auth.update(otp_value=otp, otp_expiry=expiry).where(Auth.id == id)
            result: int = query.execute()

            return result == 1

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def update_email_by_id(self, id: str, email: str) -> Optional[bool]:
        try:
            query = Auth.update(email=email).where(Auth.id == id)
            result: int = query.execute()

            return result == 1

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def delete_auth_by_id(self, id: str) -> Optional[bool]:
        try:
            # Delete User
            result = Users.delete_user_by_id(id)

            if result:
                # Delete Auth
                query = Auth.delete().where(Auth.id == id)
                query.execute()  # Remove the rows, return number of rows removed.

                return True
            else:
                return False

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_emails(self) -> List[str]:
        try:
            result = [
                auth.email for auth in Auth.select(Auth.email)
            ]
            return result

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_user_ids_by_email(self) -> Dict[str, str]:
        try:
            result = {}
            rows = Auth.select(Auth.id, Auth.email)
            for row in rows:
                result[row.email] = row.id

            return result

        except Exception:
            log.exception(" Exception caught in model method.")
            return {}


Auths = AuthsTable(DB)
