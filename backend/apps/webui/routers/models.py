from fastapi import Depends, HTTPException, status, Request
from typing import List, Optional

from fastapi import APIRouter
from apps.webui.models.models import Models, ModelModel, ModelForm, ModelResponse
from apps.webui.models.users import UserModel

from utils.utils import get_verified_user, get_admin_user
from constants import ERROR_MESSAGES

router = APIRouter()

###########################
# getModels
###########################


@router.get("/", response_model=List[ModelResponse])
async def get_models(user: UserModel = Depends(get_verified_user)) -> List[ModelResponse]:
    return Models.get_all_models()


############################
# AddNewModel
############################


@router.post("/add", response_model=Optional[ModelModel])
async def add_new_model(
    request: Request, form_data: ModelForm, user: UserModel = Depends(get_admin_user)
) -> Optional[ModelModel]:
    if form_data.id in request.app.state.MODELS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.MODEL_ID_TAKEN,
        )
    else:
        model: Optional[ModelModel] = Models.insert_new_model(form_data, user.id)

        if model:
            return model
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.DEFAULT(),
            )


############################
# GetModelById
############################


@router.get("/", response_model=Optional[ModelModel])
async def get_model_by_id(id: str, user: UserModel = Depends(get_verified_user)) -> Optional[ModelModel]:
    model: Optional[ModelModel] = Models.get_model_by_id(id)

    if model:
        return model
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# UpdateModelById
############################


@router.post("/update", response_model=Optional[ModelModel])
async def update_model_by_id(
    request: Request, id: str, form_data: ModelForm, user: UserModel = Depends(get_admin_user)
) -> Optional[ModelModel]:
    model: Optional[ModelModel] = Models.get_model_by_id(id)
    if model:
        model = Models.update_model_by_id(id, form_data)
        return model
    else:
        if form_data.id in request.app.state.MODELS:
            model = Models.insert_new_model(form_data, user.id)
            if model:
                return model
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ERROR_MESSAGES.DEFAULT(),
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.DEFAULT(),
            )


############################
# DeleteModelById
############################


@router.delete("/delete", response_model=bool)
async def delete_model_by_id(id: str, user: UserModel = Depends(get_admin_user)) -> bool:
    result: bool = Models.delete_model_by_id(id)
    return result
