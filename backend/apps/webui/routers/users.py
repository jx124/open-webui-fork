import asyncio
from email.mime.text import MIMEText
import time
from fastapi import Request
from fastapi import Depends, HTTPException, status
from typing import List, Optional, Dict

from fastapi import APIRouter
from pydantic import BaseModel
import logging

import pandas as pd
import secrets
import io
import smtplib

from apps.webui.models.users import (
    UserModel,
    UserProfile,
    UserStatistics,
    UserUpdateForm,
    UserImportForm,
    UserRoleUpdateForm,
    UserSettings,
    Users,
)
from apps.webui.models.auths import Auths
from apps.webui.models.chats import Chats
from apps.webui.models.roles import Roles
from apps.webui.models.prompts_classes import Classes, StudentClasses

from utils.misc import validate_email_format
from utils.utils import get_admin_or_instructor, get_verified_user, get_password_hash, get_admin_user
from constants import ERROR_MESSAGES

from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, SITE_LINK, SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

router = APIRouter()

############################
# GetUsers
############################


@router.get("/", response_model=List[UserModel])
async def get_users(user: UserModel = Depends(get_admin_or_instructor)) -> List[UserModel]:
    result: List[UserModel] = Users.get_users()
    return result


############################
# GetUserNames
############################


@router.get("/profiles", response_model=Dict[str, UserProfile])
async def get_user_profiles(user: UserModel = Depends(get_admin_or_instructor)) -> Dict[str, UserProfile]:
    result: Dict[str, UserProfile] = Users.get_user_profiles()
    return result


############################
# GetUserStatistics
############################


@router.get("/statistics", response_model=Dict[str, UserStatistics])
async def get_user_statistics(user: UserModel = Depends(get_admin_or_instructor)) -> Dict[str, UserStatistics]:
    result: Dict[str, UserStatistics] = Users.get_user_statistics()
    return result


############################
# User Permissions
############################


@router.get("/permissions/user")
async def get_user_permissions(
        request: Request, user: UserModel = Depends(get_admin_or_instructor)) -> Dict[str, object]:
    return request.app.state.config.USER_PERMISSIONS


@router.post("/permissions/user")
async def update_user_permissions(
    request: Request, form_data: dict[str, object], user: UserModel = Depends(get_admin_or_instructor)
) -> Dict[str, object]:
    request.app.state.config.USER_PERMISSIONS = form_data
    return request.app.state.config.USER_PERMISSIONS


############################
# UpdateUserRole
############################


@router.post("/update/role", response_model=Optional[UserModel])
async def update_user_role(
        form_data: UserRoleUpdateForm, user: UserModel = Depends(get_admin_user)) -> Optional[UserModel]:

    first_user = Users.get_first_user()
    if first_user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(),
        )

    if user.id != form_data.id and form_data.id != first_user.id:
        if "," in form_data.role or len(form_data.role) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.INVALID_ROLE_FORMAT,
            )
        return Users.update_user_role_by_id(form_data.id, form_data.role)

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=ERROR_MESSAGES.ACTION_PROHIBITED,
    )


############################
# GetUserSettingsBySessionUser
############################


@router.get("/user/settings", response_model=Optional[UserSettings])
async def get_user_settings_by_session_user(user: UserModel = Depends(get_verified_user)) -> Optional[UserSettings]:
    if user:
        return user.settings
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.USER_NOT_FOUND,
        )


############################
# UpdateUserSettingsBySessionUser
############################


@router.post("/user/settings/update", response_model=UserSettings)
async def update_user_settings_by_session_user(
    form_data: UserSettings, user: UserModel = Depends(get_verified_user)
) -> UserSettings:
    updated_user = Users.update_user_by_id(user.id, {"settings": form_data.model_dump()})
    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.USER_NOT_FOUND,
        )

    settings = updated_user.settings
    if settings is None:
        raise HTTPException(
            status_code=500,
            detail=ERROR_MESSAGES.DEFAULT(),
        )

    return settings


############################
# GetUserById
############################


class UserResponse(BaseModel):
    name: str
    profile_image_url: str


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str, user: UserModel = Depends(get_verified_user)) -> UserResponse:

    # Check if user_id is a shared chat
    # If it is, get the user_id from the chat
    if user_id.startswith("shared-"):
        chat_id = user_id.replace("shared-", "")
        chat = Chats.get_chat_by_id(chat_id)
        if chat:
            user_id = chat.user_id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.USER_NOT_FOUND,
            )

    result = Users.get_user_by_id(user_id)

    if result:
        return UserResponse(name=result.name, profile_image_url=result.profile_image_url)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.USER_NOT_FOUND,
        )


############################
# UpdateUserById
############################


@router.post("/{user_id}/update", response_model=Optional[UserModel])
async def update_user_by_id(
    user_id: str, form_data: UserUpdateForm, session_user: UserModel = Depends(get_admin_or_instructor)
) -> Optional[UserModel]:
    user = Users.get_user_by_id(user_id)

    if user:
        if form_data.email.lower() != user.email:
            email_user = Users.get_user_by_email(form_data.email.lower())
            if email_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ERROR_MESSAGES.EMAIL_TAKEN,
                )

        if form_data.password:
            hashed = get_password_hash(form_data.password)
            log.debug(f"hashed: {hashed}")
            Auths.update_user_password_by_id(user_id, hashed)

        Auths.update_email_by_id(user_id, form_data.email.lower())
        updated_user = Users.update_user_by_id(
            user_id,
            {
                "name": form_data.name,
                "email": form_data.email.lower(),
                "profile_image_url": form_data.profile_image_url,
            },
        )

        if updated_user:
            return updated_user

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(),
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ERROR_MESSAGES.USER_NOT_FOUND,
    )


############################
# DeleteUserById
############################


@router.delete("/{user_id}", response_model=bool)
async def delete_user_by_id(user_id: str, user: UserModel = Depends(get_admin_user)) -> bool:
    if user.id != user_id:
        if Classes.get_class_count_by_instructor_id(user_id) != 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR_MESSAGES.USER_IS_INSTRUCTOR,
            )

        StudentClasses.delete_student_classes_by_student(user_id)
        Chats.delete_chats_by_user_id(user_id)
        result = Auths.delete_auth_by_id(user_id)

        if result:
            return True

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DELETE_USER_ERROR,
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=ERROR_MESSAGES.ACTION_PROHIBITED,
    )


############################
# ImportUsers
############################

background_tasks = set()


@router.post("/import", response_model=List[UserModel])
async def import_users(
        form_data: List[UserImportForm], user: UserModel = Depends(get_admin_or_instructor)) -> List[UserModel]:
    print("User import", form_data)

    existing_emails = set(Auths.get_emails())
    user_emails = set([entry.email.lower() for entry in form_data])

    # repeat or duplicate emails
    if (len(existing_emails.intersection(user_emails)) > 0 or len(user_emails) != len(form_data)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.INVALID_EMAILS
        )

    # invalid email formats
    for email in user_emails:
        if not validate_email_format(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.INVALID_EMAIL_FORMAT(email)
            )

    available_roles = set([role.name for role in Roles.get_roles()])
    user_roles = set([entry.role.strip() for entry in form_data])

    # missing roles
    if not user_roles.issubset(available_roles):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.MISSING_ROLES(user_roles.difference(available_roles))
        )

    for entry in form_data:
        entry.password = secrets.token_urlsafe(10)

    task = asyncio.create_task(email_user_account_details(form_data))

    # save reference to prevent garbage collection
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    for entry in form_data:
        hashed = get_password_hash(entry.password)
        Auths.insert_new_auth(
            entry.email.lower(),
            hashed,
            entry.name,
            "/user.png",
            entry.role,
        )

    return Users.get_users()


# TODO: set daily limits
async def email_user_account_details(users: List[UserImportForm]) -> None:
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)

    start = time.time()

    for user in users:
        text = (
            f"Dear {user.name},\n\n"
            f"Your account has been registered for the SWAT:RolePlay tool, an AI-powered "
            f"tool designed to help social worker and students practice their skills through "
            f"role-playing scenarios. Your login details are:\n\n"
            f"Email: {user.email}\n"
            f"Password: {user.password}\n\n"
            f"The site can be accessed from {SITE_LINK} > Login Here."
        )

        msg = MIMEText(text)
        msg["Subject"] = "SWAT:RolePlay Registration"
        msg["To"] = user.email
        msg["From"] = GMAIL_ADDRESS

        try:
            smtp_server.sendmail(msg["From"], user.email, msg.as_string())
            print(f"[{time.time() - start:.4f}] Sent email to {user.email}")
        except Exception as e:
            print(f"[{time.time() - start:.4f}] SMTP error {e}")

        await asyncio.sleep(1)

    smtp_server.quit()


############################
# GetUserIdssByExcel
############################


@router.post("/ids/import", response_model=List[str])
async def get_user_ids_by_excel(request: Request, user: UserModel = Depends(get_admin_or_instructor)) -> List[str]:
    users = None

    try:
        recv_bytes = await request.body()
        users = pd.read_excel(io.BytesIO(recv_bytes))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.INVALID_IMPORT_FILE
        )

    if "Email" not in users.columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.MISSING_COLUMNS_IMPORT("Email")
        )

    existing_emails = set(Auths.get_emails())
    user_emails = set([email.lower() for email in users["Email"]])

    if not user_emails.issubset(existing_emails):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.MISSING_EMAILS(user_emails.difference(existing_emails))
        )

    email_ids = Auths.get_user_ids_by_email()
    result = []

    for email in users["Email"]:
        result.append(email_ids[email])

    return result
