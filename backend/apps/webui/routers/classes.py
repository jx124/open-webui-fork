from fastapi import Depends, HTTPException, status
from typing import List, Optional

from fastapi import APIRouter

from apps.webui.models.prompts_classes import ClassForm, ClassModel, Classes
from utils.utils import get_admin_or_instructor, get_current_user
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
async def create_new_class(form_data: ClassForm, user=Depends(get_admin_or_instructor)):
    class_ = Classes.get_class_by_name(form_data.name)
    if class_ is None:
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
# GetClassById
############################


@router.get("/{class_id}", response_model=Optional[ClassModel])
async def get_class_by_id(class_id: int, user=Depends(get_admin_or_instructor)):
    class_ = Classes.get_class_by_id(user.id, user.role, class_id)

    if class_:
        return class_

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
    )


###########################
# UpdateClass
###########################


@router.post("/update", response_model=bool)
async def update_class_by_id(
    form_data: ClassForm, user=Depends(get_admin_or_instructor)
):
    # check if authorized
    class_ = Classes.get_class_by_id(user.id, user.role, form_data.id)
    if class_ is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )
    
    # check for name collision
    class_ = Classes.get_class_by_name(form_data.name)
    if class_ is None or class_.id == form_data.id:
        result = Classes.update_class_by_id(form_data)
        if result:
            return result

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(),
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ERROR_MESSAGES.CLASS_NAME_TAKEN(form_data.name),
    )


############################
# DeleteClass
############################


@router.delete("/delete/{class_id}", response_model=bool)
async def delete_class_by_id(class_id: int, user=Depends(get_admin_or_instructor)):
    # check if authorized
    class_ = Classes.get_class_by_id(user.id, user.role, class_id)
    if class_ is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )
    
    result = Classes.delete_class_by_id(class_id)
    return result
