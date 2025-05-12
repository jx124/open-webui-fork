from fastapi import Depends, HTTPException, status
from typing import List, Optional

from fastapi import APIRouter

from apps.webui.models.evaluations import EvaluationForm, EvaluationModel, Evaluations
from apps.webui.models.prompts_classes import Prompts
from utils.utils import get_admin_user
from constants import ERROR_MESSAGES

router = APIRouter()

############################
# GetEvaluations
############################


@router.get("/", response_model=List[EvaluationModel])
async def get_evaluations(user=Depends(get_admin_user)):
    return Evaluations.get_evaluations()


############################
# GetEvaluationsById
############################


@router.get("/{eval_id}", response_model=Optional[EvaluationModel])
async def get_evaluation_by_id(eval_id: int, user=Depends(get_admin_user)):
    return Evaluations.get_evaluation_by_id(eval_id)


############################
# CreateNewEvaluation
############################


@router.post("/create", response_model=Optional[EvaluationModel])
async def create_new_evaluation(form_data: EvaluationForm, user=Depends(get_admin_user)):
    if len(form_data.title) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.INVALID_EVAL_TITLE,
        )

    evaluation = Evaluations.get_evaluation_by_title(form_data.title)
    if evaluation is None:
        evaluation = Evaluations.insert_new_evaluation(form_data)

        if evaluation:
            return evaluation
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(),
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ERROR_MESSAGES.EVAL_TITLE_TAKEN(form_data.title),
    )


############################
# UpdateEvaluationByCommand
############################


@router.post("/update", response_model=Optional[EvaluationModel])
async def update_evaluation(form_data: EvaluationForm, user=Depends(get_admin_user)):
    if len(form_data.title) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.INVALID_EVAL_TITLE,
        )

    evaluation = Evaluations.get_evaluation_by_title(form_data.title)
    if evaluation is None or evaluation.id == form_data.id:
        result = Evaluations.update_evaluation(form_data)
        if result:
            return result

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(),
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ERROR_MESSAGES.EVAL_TITLE_TAKEN(form_data.title),
    )

# ############################
# DeleteEvaluationByCommand
# ############################


@router.delete("/delete/{eval_id}", response_model=bool)
async def delete_evaluation_by_id(eval_id: int, user=Depends(get_admin_user)):
    profiles = Prompts.get_profile_titles_by_eval_id(eval_id)
    if len(profiles) != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.INVALID_EVAL_DELETION(profiles),
        )

    result = Evaluations.delete_evaluation_by_id(eval_id)
    return result
