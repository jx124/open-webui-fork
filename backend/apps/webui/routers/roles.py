from fastapi import Depends, HTTPException, status
from typing import List, Optional

from fastapi import APIRouter

from apps.webui.models.roles import Roles, RoleForm, RoleModel
from apps.webui.models.users import Users, UserModel
from apps.webui.models.prompts_classes import PromptRoles

from utils.utils import get_admin_or_instructor, get_admin_user
from constants import ERROR_MESSAGES

router = APIRouter()

############################
# GetRoles
############################


@router.get("/", response_model=List[RoleModel])
async def get_roles(user: UserModel = Depends(get_admin_or_instructor)) -> List[RoleModel]:
    result: List[RoleModel] = Roles.get_roles()
    return result


############################
# CreateNewRole
############################


@router.post("/create", response_model=Optional[RoleModel])
async def create_new_role(form_data: RoleForm, user: UserModel = Depends(get_admin_user)) -> Optional[RoleModel]:
    if "," in form_data.name or len(form_data.name) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.INVALID_ROLE_FORMAT,
        )

    role = Roles.get_role_by_name(form_data.name)
    if role is None:

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


############################
# UpdateRoleByCommand
############################


@router.post("/update", response_model=List[RoleModel])
async def update_roles(roles: List[RoleForm], user: UserModel = Depends(get_admin_user)) -> List[RoleModel]:
    for role in roles:
        if "," in role.name or len(role.name) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.INVALID_ROLE_FORMAT,
            )
        if role.name in ["pending", "admin", "instructor"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.INVALID_ROLE_CHANGE,
            )

        if role.id == 0:
            Roles.insert_new_role(role.name)
        else:
            result: Optional[RoleModel] = Roles.update_role(role)
            if result is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ERROR_MESSAGES.DUPLICATE_ROLES,
                )

    new_roles: List[RoleModel] = Roles.get_roles()
    return new_roles


# ############################
# # DeleteRoleByCommand
# ############################


@router.delete("/delete/{role_id}", response_model=bool)
async def delete_role_by_id(role_id: int, user: UserModel = Depends(get_admin_user)) -> bool:
    if role_id == 0:
        return True

    invalid_roles = [role.id for role in Roles.get_roles() if role.name in ["pending", "admin", "instructor"]]

    # "pending", "admin", and "instructor" roles cannot be deleted
    if role_id in invalid_roles:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.INVALID_ROLE_CHANGE,
            )

    num_users = Users.get_num_users_by_role_id(role_id)
    if num_users != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.INVALID_ROLE_DELETION(num_users),
        )

    result: bool = PromptRoles.delete_prompt_roles_by_role(role_id)
    role_result: bool = False

    if result:
        role_result = Roles.delete_role_by_id(role_id)
    return result and role_result
