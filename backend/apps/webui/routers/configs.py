from fastapi import Request
from fastapi import Depends
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from config import BannerModel
from apps.webui.models.users import UserModel

from utils.utils import (
    get_current_user,
    get_admin_user,
)

router = APIRouter()


class SetDefaultModelsForm(BaseModel):
    models: str


class PromptSuggestion(BaseModel):
    title: List[str]
    content: str


class SetDefaultSuggestionsForm(BaseModel):
    suggestions: List[PromptSuggestion]


############################
# SetDefaultModels
############################


@router.post("/default/models", response_model=str)
async def set_global_default_models(
    request: Request, form_data: SetDefaultModelsForm, user: UserModel = Depends(get_admin_user)
) -> str:
    request.app.state.config.DEFAULT_MODELS = form_data.models
    return request.app.state.config.DEFAULT_MODELS


@router.post("/default/suggestions", response_model=List[PromptSuggestion])
async def set_global_default_suggestions(
    request: Request,
    form_data: SetDefaultSuggestionsForm,
    user: UserModel = Depends(get_admin_user),
) -> List[PromptSuggestion]:
    data = form_data.model_dump()
    request.app.state.config.DEFAULT_PROMPT_SUGGESTIONS = data["suggestions"]
    result: List[PromptSuggestion] = request.app.state.config.DEFAULT_PROMPT_SUGGESTIONS
    return result


############################
# SetBanners
############################


class SetBannersForm(BaseModel):
    banners: List[BannerModel]


@router.post("/banners", response_model=List[BannerModel])
async def set_banners(
    request: Request,
    form_data: SetBannersForm,
    user: UserModel = Depends(get_admin_user),
) -> List[BannerModel]:
    data = form_data.model_dump()
    request.app.state.config.BANNERS = data["banners"]
    result: List[BannerModel] = request.app.state.config.BANNERS
    return result


@router.get("/banners", response_model=List[BannerModel])
async def get_banners(
    request: Request,
    user: UserModel = Depends(get_current_user),
) -> List[BannerModel]:
    result: List[BannerModel] = request.app.state.config.BANNERS
    return result
