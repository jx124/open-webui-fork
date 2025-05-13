import asyncio
from email.mime.text import MIMEText
import secrets
import smtplib
import time
from fastapi import Request
from fastapi import Depends, HTTPException, status

from fastapi import APIRouter
from pydantic import BaseModel
import re
import uuid
from typing import Optional

from apps.webui.models.auths import (
    ResetOTPForm,
    ResetPasswordForm,
    ResetPasswordOTPForm,
    SigninForm,
    SignupForm,
    AddUserForm,
    UpdateProfileForm,
    UpdatePasswordForm,
    UserResponse,
    SigninResponse,
    Auths,
    ApiKey,
)
from apps.webui.models.users import UserModel, Users
from apps.webui.models.roles import Roles

from utils.utils import (
    get_password_hash,
    get_current_user,
    get_admin_user,
    create_token,
    create_api_key,
)
from utils.misc import parse_duration, validate_email_format
from utils.webhook import post_webhook
from constants import ERROR_MESSAGES, WEBHOOK_MESSAGES
from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, WEBUI_AUTH, WEBUI_AUTH_TRUSTED_EMAIL_HEADER

router = APIRouter()

############################
# GetSessionUser
############################


@router.get("/", response_model=UserResponse)
async def get_session_user(user: UserModel = Depends(get_current_user)) -> UserResponse:
    return UserResponse(**{
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "profile_image_url": user.profile_image_url,
    })


############################
# Update Profile
############################


@router.post("/update/profile", response_model=UserResponse)
async def update_profile(
    form_data: UpdateProfileForm, session_user: UserModel = Depends(get_current_user)
) -> UserResponse:
    if session_user:
        user = Users.update_user_by_id(
            session_user.id,
            {"profile_image_url": form_data.profile_image_url, "name": form_data.name},
        )
        if user is None:
            raise HTTPException(500, detail=ERROR_MESSAGES.DEFAULT())
        return user

    else:
        raise HTTPException(401, detail=ERROR_MESSAGES.INVALID_CRED)


############################
# Update Password
############################


@router.post("/update/password", response_model=bool)
async def update_password(
    form_data: UpdatePasswordForm, session_user: UserModel = Depends(get_current_user)
) -> bool:
    if WEBUI_AUTH_TRUSTED_EMAIL_HEADER:
        raise HTTPException(401, detail=ERROR_MESSAGES.ACTION_PROHIBITED)
    if session_user:
        user = Auths.authenticate_user(session_user.email, form_data.password)

        if user is None:
            raise HTTPException(401, detail=ERROR_MESSAGES.INVALID_PASSWORD)

        hashed = get_password_hash(form_data.new_password)
        success = Auths.update_user_password_by_id(user.id, hashed)

        if success is None:
            raise HTTPException(500, detail=ERROR_MESSAGES.DEFAULT())

        return success
    else:
        raise HTTPException(401, detail=ERROR_MESSAGES.INVALID_CRED)


############################
# SignIn
############################


@router.post("/signin", response_model=SigninResponse)
async def signin(request: Request, form_data: SigninForm) -> SigninResponse:
    if WEBUI_AUTH_TRUSTED_EMAIL_HEADER:
        if WEBUI_AUTH_TRUSTED_EMAIL_HEADER not in request.headers:
            raise HTTPException(401, detail=ERROR_MESSAGES.INVALID_TRUSTED_HEADER)

        trusted_email = request.headers[WEBUI_AUTH_TRUSTED_EMAIL_HEADER].lower()
        if not Users.get_user_by_email(trusted_email.lower()):
            await signup(
                request,
                SignupForm(
                    email=trusted_email, password=str(uuid.uuid4()), name=trusted_email
                ),
            )
        user = Auths.authenticate_user_by_trusted_header(trusted_email)
    elif not WEBUI_AUTH:
        admin_email = "admin@localhost"
        admin_password = "admin"

        if Users.get_user_by_email(admin_email.lower()):
            user = Auths.authenticate_user(admin_email.lower(), admin_password)
        else:
            if Users.get_num_users() != 0:
                raise HTTPException(403, detail=ERROR_MESSAGES.EXISTING_USERS)

            await signup(
                request,
                SignupForm(email=admin_email, password=admin_password, name="User"),
            )

            user = Auths.authenticate_user(admin_email.lower(), admin_password)
    else:
        user = Auths.authenticate_user(form_data.email.lower(), form_data.password)

    if user:
        token = create_token(
            data={"id": user.id},
            expires_delta=parse_duration(request.app.state.config.JWT_EXPIRES_IN),
        )

        return SigninResponse(**{
            "token": token,
            "token_type": "Bearer",
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "profile_image_url": user.profile_image_url,
        })
    else:
        raise HTTPException(401, detail=ERROR_MESSAGES.INVALID_CRED)


############################
# SignUp
############################


@router.post("/signup", response_model=SigninResponse)
async def signup(request: Request, form_data: SignupForm) -> SigninResponse:
    if not request.app.state.config.ENABLE_SIGNUP and WEBUI_AUTH:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail=ERROR_MESSAGES.ACCESS_PROHIBITED
        )

    if not validate_email_format(form_data.email.lower()):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.INVALID_EMAIL_FORMAT
        )

    if Users.get_user_by_email(form_data.email.lower()):
        raise HTTPException(400, detail=ERROR_MESSAGES.EMAIL_TAKEN)

    try:
        role = (
            "admin"
            if Users.get_num_users() == 0
            else request.app.state.config.DEFAULT_USER_ROLE
        )
        hashed = get_password_hash(form_data.password)
        user = Auths.insert_new_auth(
            form_data.email.lower(),
            hashed,
            form_data.name,
            form_data.profile_image_url,
            role,
        )

        if user is None:
            raise HTTPException(500, detail=ERROR_MESSAGES.CREATE_USER_ERROR)

        token = create_token(
            data={"id": user.id},
            expires_delta=parse_duration(request.app.state.config.JWT_EXPIRES_IN),
        )
        # response.set_cookie(key='token', value=token, httponly=True)

        if request.app.state.config.WEBHOOK_URL:
            post_webhook(
                request.app.state.config.WEBHOOK_URL,
                WEBHOOK_MESSAGES.USER_SIGNUP(user.name),
                {
                    "action": "signup",
                    "message": WEBHOOK_MESSAGES.USER_SIGNUP(user.name),
                    "user": user.model_dump_json(exclude_none=True),
                },
            )

        return SigninResponse(**{
            "token": token,
            "token_type": "Bearer",
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "profile_image_url": user.profile_image_url,
        })
    except Exception as err:
        raise HTTPException(500, detail=ERROR_MESSAGES.DEFAULT(err))


############################
# AddUser
############################


@router.post("/add", response_model=SigninResponse)
async def add_user(form_data: AddUserForm, user: UserModel = Depends(get_admin_user)) -> SigninResponse:

    if not validate_email_format(form_data.email.lower()):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.INVALID_EMAIL_FORMAT
        )

    if Users.get_user_by_email(form_data.email.lower()):
        raise HTTPException(400, detail=ERROR_MESSAGES.EMAIL_TAKEN)

    try:
        hashed = get_password_hash(form_data.password)
        new_user: Optional[UserModel] = Auths.insert_new_auth(
            form_data.email.lower(),
            hashed,
            form_data.name,
            form_data.profile_image_url,
            form_data.role,
        )

        if new_user is None:
            raise HTTPException(500, detail=ERROR_MESSAGES.CREATE_USER_ERROR)

        token = create_token(data={"id": new_user.id})
        return SigninResponse(**{
            "token": token,
            "token_type": "Bearer",
            "id": new_user.id,
            "email": new_user.email,
            "name": new_user.name,
            "role": new_user.role.strip(),
            "profile_image_url": new_user.profile_image_url,
        })
    except Exception as err:
        raise HTTPException(500, detail=ERROR_MESSAGES.DEFAULT(err))


############################
# ResetUserPassword
############################

background_tasks = set()


@router.post("/reset", response_model=bool)
async def send_user_otp(form_data: ResetPasswordForm) -> bool:

    user = Users.get_user_by_email(form_data.email.lower())

    if user is None:
        await asyncio.sleep(2)
        raise HTTPException(400, detail=ERROR_MESSAGES.EMAIL_MISMATCH)

    try:
        otp = secrets.randbelow(1000000)
        expiry = int(time.time()) + 60 * 15

        result = Auths.update_user_otp_by_id(user.id, otp, expiry)

        if result:
            task = asyncio.create_task(email_user_otp(user, str(otp).zfill(6)))

            # save reference to prevent garbage collection
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)
            return True

        else:
            raise HTTPException(500, detail=ERROR_MESSAGES.DEFAULT())

    except Exception:
        return True


# TODO: set daily limits
async def email_user_otp(user: UserModel, otp: str) -> None:
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)

    text = (
        f"Dear {user.name},\n\n"
        f"You have clicked on \"Forgot Password\" for your SWAT:RolePlay account.\n\n"
        f"Your OTP is {otp}, please do not share it with anyone else."
    )

    msg = MIMEText(text)
    msg["Subject"] = "SWAT:RolePlay Reset Password OTP"
    msg["To"] = user.email
    msg["From"] = GMAIL_ADDRESS

    try:
        smtp_server.sendmail(msg["From"], user.email, msg.as_string())
        print(f"Sent reset password OTP email to {user.email}")
    except Exception as e:
        print(f"SMTP error {e}")

    smtp_server.quit()


@router.post("/reset/verify", response_model=bool)
async def verify_user_otp(form_data: ResetOTPForm) -> bool:

    user = Users.get_user_by_email(form_data.email.lower())

    if user is None:
        await asyncio.sleep(1)
        raise HTTPException(400, detail=ERROR_MESSAGES.EMAIL_MISMATCH)

    try:
        authorized = Auths.authenticate_user_otp(user.id, form_data.OTP)

        if authorized:
            return True

        await asyncio.sleep(1)
        raise HTTPException(401, detail=ERROR_MESSAGES.INVALID_OTP)

    except Exception:
        await asyncio.sleep(1)
        raise HTTPException(401, detail=ERROR_MESSAGES.INVALID_OTP)


@router.post("/reset/password", response_model=bool)
async def reset_user_password(form_data: ResetPasswordOTPForm) -> bool:

    user = Users.get_user_by_email(form_data.email.lower())

    if user is None:
        await asyncio.sleep(1)
        raise HTTPException(400, detail=ERROR_MESSAGES.EMAIL_MISMATCH)

    try:
        authorized = Auths.authenticate_user_otp(user.id, form_data.OTP)

        if not authorized:
            await asyncio.sleep(1)
            raise HTTPException(401, detail=ERROR_MESSAGES.INVALID_OTP)

        hashed = get_password_hash(form_data.password)
        result = Auths.update_user_password_by_id(user.id, hashed)

        if result:
            return True
        raise HTTPException(500, detail=ERROR_MESSAGES.DEFAULT())

    except Exception:
        await asyncio.sleep(1)
        raise HTTPException(401, detail=ERROR_MESSAGES.INVALID_OTP)


############################
# ToggleSignUp
############################


@router.get("/signup/enabled", response_model=bool)
async def get_sign_up_status(request: Request, user: UserModel = Depends(get_admin_user)) -> bool:
    enabled: bool = request.app.state.config.ENABLE_SIGNUP
    return enabled


@router.get("/signup/enabled/toggle", response_model=bool)
async def toggle_sign_up(request: Request, user: UserModel = Depends(get_admin_user)) -> bool:
    request.app.state.config.ENABLE_SIGNUP = not request.app.state.config.ENABLE_SIGNUP
    return request.app.state.config.ENABLE_SIGNUP


############################
# Default User Role
############################


@router.get("/signup/user/role", response_model=str)
async def get_default_user_role(request: Request, user: UserModel = Depends(get_admin_user)) -> str:
    default_role: str = request.app.state.config.DEFAULT_USER_ROLE
    return default_role


class UpdateRoleForm(BaseModel):
    role: str


@router.post("/signup/user/role", response_model=str)
async def update_default_user_role(
    request: Request, form_data: UpdateRoleForm, user: UserModel = Depends(get_admin_user)
) -> str:
    roles = [role.name for role in Roles.get_roles()]
    if form_data.role.strip() in roles:
        request.app.state.config.DEFAULT_USER_ROLE = form_data.role.strip()
    new_role: str = request.app.state.config.DEFAULT_USER_ROLE
    return new_role


############################
# JWT Expiration
############################


@router.get("/token/expires", response_model=str)
async def get_token_expires_duration(request: Request, user: UserModel = Depends(get_admin_user)) -> str:
    duration: str = request.app.state.config.JWT_EXPIRES_IN
    return duration


class UpdateJWTExpiresDurationForm(BaseModel):
    duration: str


@router.post("/token/expires/update", response_model=str)
async def update_token_expires_duration(
    request: Request,
    form_data: UpdateJWTExpiresDurationForm,
    user: UserModel = Depends(get_admin_user),
) -> str:
    pattern = r"^(-1|0|(-?\d+(\.\d+)?)(ms|s|m|h|d|w))$"

    # Check if the input string matches the pattern
    if re.match(pattern, form_data.duration):
        request.app.state.config.JWT_EXPIRES_IN = form_data.duration
    else:
        raise HTTPException(400, detail=ERROR_MESSAGES.INVALID_DURATION)

    duration: str = request.app.state.config.JWT_EXPIRES_IN
    return duration


############################
# API Key
############################


# create api key
@router.post("/api_key", response_model=ApiKey)
async def create_api_key_(user: UserModel = Depends(get_current_user)) -> ApiKey:
    api_key = create_api_key()
    success = Users.update_user_api_key_by_id(user.id, api_key)
    if success:
        result: ApiKey = ApiKey(api_key=api_key)
        return result
    else:
        raise HTTPException(500, detail=ERROR_MESSAGES.CREATE_API_KEY_ERROR)


# delete api key
@router.delete("/api_key", response_model=bool)
async def delete_api_key(user: UserModel = Depends(get_current_user)) -> bool:
    success: bool = Users.update_user_api_key_by_id(user.id, None)
    return success


# get api key
@router.get("/api_key", response_model=ApiKey)
async def get_api_key(user: UserModel = Depends(get_current_user)) -> ApiKey:
    api_key = Users.get_user_api_key_by_id(user.id)
    if api_key is not None:
        return ApiKey(api_key=api_key)
    else:
        raise HTTPException(404, detail=ERROR_MESSAGES.API_KEY_NOT_FOUND)
