from pydantic import BaseModel
import peewee as pw
from typing import List, Optional

from apps.webui.internal.db import DB

import logging
from config import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# Evaluation DB Schema
####################


class Evaluation(pw.Model):
    title = pw.CharField(null=False, unique=True)
    content = pw.TextField(default="")
    model_id = pw.TextField(default="")

    class Meta:
        database = DB


class EvaluationModel(BaseModel):
    id: int
    title: str
    content: str
    selected_model_id: str  # prevent namespace collision


####################
# Forms
####################

class EvaluationForm(BaseModel):
    id: int = 0
    title: str
    content: str
    selected_model_id: str


class EvaluationsTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([Evaluation])

    def get_evaluations(self) -> List[EvaluationModel]:
        try:
            return [EvaluationModel(
                id=result.id,
                title=result.title,
                content=result.content,
                selected_model_id=result.model_id
            ) for result in Evaluation.select()]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_evaluation_by_id(self, eval_id: int) -> Optional[EvaluationModel]:
        try:
            result = Evaluation.get_or_none(Evaluation.id == eval_id)
            if result:
                return EvaluationModel(
                    id=result.id,
                    title=result.title,
                    content=result.content,
                    selected_model_id=result.model_id
                )
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_evaluation_content_by_id(self, eval_id: int) -> Optional[str]:
        try:
            result: Optional[EvaluationModel] = Evaluation.get_or_none(Evaluation.id == eval_id)
            if result:
                return result.content
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_evaluation_by_title(self, title: str) -> Optional[EvaluationModel]:
        try:
            result = Evaluation.get_or_none(Evaluation.title == title)
            if result:
                return EvaluationModel(
                    id=result.id,
                    title=result.title,
                    content=result.content,
                    selected_model_id=result.model_id
                )
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def insert_new_evaluation(self, form_data: EvaluationForm) -> Optional[EvaluationModel]:
        try:
            result: Evaluation = Evaluation.create(
                    title=form_data.title, content=form_data.content, model_id=form_data.selected_model_id)
            if result:
                return EvaluationModel(
                    id=result.id,
                    title=result.title,
                    content=result.content,
                    selected_model_id=result.model_id
                )
            else:
                return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def update_evaluation(self, form_data: EvaluationForm) -> Optional[EvaluationModel]:
        try:
            result = Evaluation.update(
                    title=form_data.title,
                    content=form_data.content,
                    model_id=form_data.selected_model_id)\
                .where(Evaluation.id == form_data.id).execute()
            if result:
                updated = Evaluation.get_or_none(Evaluation.id == form_data.id)
                return EvaluationModel(
                    id=updated.id,
                    title=updated.title,
                    content=updated.content,
                    selected_model_id=updated.model_id
                )
            else:
                return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def delete_evaluation_by_id(self, eval_id: int) -> bool:
        try:
            result: int = Evaluation.delete().where(Evaluation.id == eval_id).execute()
            return result == 1

        except Exception:
            log.exception(" Exception caught in model method.")
            return False


Evaluations = EvaluationsTable(DB)
