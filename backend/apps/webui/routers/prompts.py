from fastapi import Depends, HTTPException, status
from typing import Dict, List, Optional

from fastapi import APIRouter

from apps.webui.models.prompts_classes import Prompts, PromptForm, PromptModel

from apps.webui.models.chats import Chats
from apps.webui.models.users import UserModel
from utils.utils import get_admin_user, get_current_user
from constants import ERROR_MESSAGES

router = APIRouter()

############################
# GetPrompts
############################


@router.get("/", response_model=List[PromptModel])
async def get_prompts(user: UserModel = Depends(get_current_user)) -> List[PromptModel]:
    result: List[PromptModel] = Prompts.get_prompts(user.id, user.role)
    return result


############################
# GetPromptTitles
############################


@router.get("/titles", response_model=Dict[int, str])
async def get_prompt_titles(user: UserModel = Depends(get_current_user)) -> Dict[int, str]:
    result: Dict[int, str] = Prompts.get_prompt_titles(user.id, user.role)
    return result


############################
# CreateNewPrompt
############################


@router.post("/create", response_model=Optional[int])
async def create_new_prompt(form_data: PromptForm, user: UserModel = Depends(get_admin_user)) -> Optional[int]:
    prompt: Optional[PromptModel] = Prompts.get_prompt_by_command(user.id, "admin", form_data.command)

    if prompt is None:
        new_prompt: Optional[PromptModel] = Prompts.insert_new_prompt(user.id, form_data)

        if new_prompt:
            return new_prompt.id
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(),
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ERROR_MESSAGES.COMMAND_TAKEN(form_data.command),
    )


############################
# GetPromptByCommand
############################


# TODO: change to a Union type, show users only title etc.
@router.get("/command/{command}", response_model=Optional[PromptModel])
async def get_prompt_by_command(command: str, user: UserModel = Depends(get_current_user)) -> Optional[PromptModel]:
    prompt: Optional[PromptModel] = Prompts.get_prompt_by_command(user.id, user.role, f"/{command}")

    if prompt:
        return prompt
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# UpdatePromptByCommand
############################


@router.post("/command/{command}/update", response_model=bool)
async def update_prompt_by_command(
    form_data: PromptForm, user: UserModel = Depends(get_admin_user)
) -> bool:
    result: bool = Prompts.update_prompt_by_command(form_data)
    if result:
        return result

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ERROR_MESSAGES.DEFAULT(),
    )


############################
# DeletePromptByCommand
############################


@router.delete("/command/{command}/delete", response_model=bool)
async def delete_prompt_by_command(command: str, user: UserModel = Depends(get_admin_user)) -> bool:
    prompt_id: Optional[int] = Prompts.get_prompt_id_by_command(f"/{command}")
    if prompt_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    count: int = Chats.count_chats_by_prompt_id(prompt_id)
    if count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.PROFILE_EXISTING_CHATS,
        )

    result: bool = Prompts.delete_prompt_by_id(prompt_id)

    if result:
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT(),
        )
