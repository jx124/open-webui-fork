from fastapi import Depends, FastAPI, HTTPException, status
from datetime import datetime, timedelta
from typing import List, Union, Optional

from fastapi import APIRouter
from pydantic import BaseModel
import json

from apps.webui.models.classes import ClassForm, ClassModel, Classes
from utils.utils import get_admin_or_instructor, get_current_user, get_admin_user
from constants import ERROR_MESSAGES

router = APIRouter()

############################
# GetClasses
############################


@router.get("/", response_model=List[ClassModel])
async def get_classes(user=Depends(get_current_user)):
    return Classes.get_classes(user.id, user.role)


############################
# CreateNewClass
############################


@router.post("/create", response_model=Optional[ClassModel])
async def create_new_prompt(form_data: ClassForm, user=Depends(get_admin_or_instructor)):
    class_ = Classes.get_class_by_name(form_data.name)
    if class_ == None:
        class_ = Classes.insert_new_class(form_data)
        if class_:
            return class_

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(),
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ERROR_MESSAGES.CLASS_NAME_TAKEN(form_data.name),
    )


############################
# UpdateClass
############################


# @router.post("/command/{command}/update", response_model=Optional[PromptModel])
# async def update_prompt_by_command(
#     command: str, form_data: PromptForm, user=Depends(get_admin_user)
# ):
#     prompt = Prompts.update_prompt_by_command(user.id, f"/{command}", form_data)
#     if prompt:
#         return prompt
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
#         )


############################
# DeleteClass
############################


# @router.delete("/command/{command}/delete", response_model=bool)
# async def delete_prompt_by_command(command: str, user=Depends(get_admin_user)):
#     result = Prompts.delete_prompt_by_command(user.id, f"/{command}")
#     return result
