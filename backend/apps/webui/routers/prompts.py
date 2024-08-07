from fastapi import Depends, HTTPException, status
from typing import List, Optional

from fastapi import APIRouter

from apps.webui.models.prompts import Prompts, PromptForm, PromptModel

from utils.utils import get_admin_or_instructor, get_current_user
from constants import ERROR_MESSAGES

router = APIRouter()

############################
# GetPrompts
############################


@router.get("/", response_model=List[PromptModel])
async def get_prompts(user=Depends(get_current_user)):
    return Prompts.get_prompts(user.id, user.role)


############################
# CreateNewPrompt
############################


@router.post("/create", response_model=Optional[int])
async def create_new_prompt(form_data: PromptForm, user=Depends(get_admin_or_instructor)):
    prompt = Prompts.get_prompt_by_command(user.id, "admin", form_data.command)

    if prompt is None:
        prompt = Prompts.insert_new_prompt(user.id, form_data)

        if prompt:
            return prompt.id
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
async def get_prompt_by_command(command: str, user=Depends(get_current_user)):
    prompt = Prompts.get_prompt_by_command(user.id, user.role, f"/{command}")

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
    form_data: PromptForm, user=Depends(get_admin_or_instructor)
):
    result = Prompts.update_prompt_by_command(user.id, user.role, form_data)
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
async def delete_prompt_by_command(command: str, user=Depends(get_admin_or_instructor)):
    result = Prompts.delete_prompt_by_command(user.id, user.role, f"/{command}")
    if result:
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )
