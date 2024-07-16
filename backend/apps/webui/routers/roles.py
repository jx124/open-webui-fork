from fastapi import Depends, FastAPI, HTTPException, status
from datetime import datetime, timedelta
from typing import List, Union, Optional

from fastapi import APIRouter
from pydantic import BaseModel
import json

from apps.webui.models.roles import Roles, RoleForm, RoleModel
from apps.webui.models.users import Users

from utils.utils import get_current_user, get_admin_user
from constants import ERROR_MESSAGES

router = APIRouter()

############################
# GetRoles
############################


@router.get("/", response_model=List[RoleModel])
async def get_roles(user=Depends(get_admin_user)):
    return Roles.get_roles()


############################
# CreateNewRole
############################


@router.post("/create", response_model=Optional[RoleModel])
async def create_new_role(form_data: RoleForm, user=Depends(get_admin_user)):
    role = Roles.get_role_by_name(form_data.name)
    if role == None:
        role = Roles.insert_new_role(form_data.name)

        if role:
            return role
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(),
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ERROR_MESSAGES.ROLE_NAME_TAKEN(form_data.name),
    )


# ############################
# # GetPromptByCommand
# ############################


# @router.get("/command/{command}", response_model=Optional[PromptModel])
# async def get_prompt_by_command(command: str, user=Depends(get_current_user)):
#     prompt = Prompts.get_prompt_by_command(user.id, f"/{command}")

#     if prompt:
#         return prompt
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=ERROR_MESSAGES.NOT_FOUND,
#         )


############################
# UpdateRoleByCommand   
############################


@router.post("/update", response_model=List[RoleModel])
async def update_roles(roles: List[RoleForm], user=Depends(get_admin_user)):
    for role in roles:
        if (role.id == 1 and role.name != "pending") or (role.id == 2 and role.name != "admin"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.INVALID_ROLE_CHANGE,
            )
        if role.id == 0:
            Roles.insert_new_role(role.name)
        else:
            result = Roles.update_role(role)
            if result is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ERROR_MESSAGES.DUPLICATE_ROLES,
                )

    return Roles.get_roles()


# ############################
# # DeleteRoleByCommand
# ############################


@router.delete("/delete/{role_id}", response_model=bool)
async def delete_role_by_id(role_id: int, user=Depends(get_admin_user)):
    if role_id == 0:
        return True
    
    num_users = len(Users.get_users_by_role_id(role_id))
    if num_users != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.INVALID_ROLE_DELETION(num_users),
        )
    
    result = Roles.delete_role_by_id(role_id)
    return result
