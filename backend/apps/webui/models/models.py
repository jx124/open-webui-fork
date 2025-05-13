import peewee as pw

from playhouse.shortcuts import model_to_dict
from pydantic import BaseModel, ConfigDict

from apps.webui.internal.db import DB, JSONField

from typing import List, Optional

import time

import logging
from config import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# Models DB Schema
####################


# ModelParams is a model for the data stored in the params field of the Model table
class ModelParams(BaseModel):
    model_config = ConfigDict(extra="allow")
    pass


# ModelMeta is a model for the data stored in the meta field of the Model table
class ModelMeta(BaseModel):
    profile_image_url: Optional[str] = "/favicon.png"

    description: Optional[str] = None
    """
        User-facing description of the model.
    """

    capabilities: Optional[dict[str, bool]] = None

    model_config = ConfigDict(extra="allow")

    pass


class Model(pw.Model):
    id = pw.TextField(unique=True)
    """
        The model's id as used in the API. If set to an existing model, it will override the model.
    """
    user_id = pw.TextField()

    base_model_id = pw.TextField(null=True)
    """
        An optional pointer to the actual model that should be used when proxying requests.
    """

    name = pw.TextField()
    """
        The human-readable display name of the model.
    """

    params = JSONField()
    """
        Holds a JSON encoded blob of parameters, see `ModelParams`.
    """

    meta = JSONField()
    """
        Holds a JSON encoded blob of metadata, see `ModelMeta`.
    """

    updated_at = pw.BigIntegerField()
    created_at = pw.BigIntegerField()

    class Meta:
        database = DB


class ModelModel(BaseModel):
    id: str
    user_id: str
    base_model_id: Optional[str] = None

    name: str
    params: ModelParams
    meta: ModelMeta

    updated_at: int  # timestamp in epoch
    created_at: int  # timestamp in epoch


####################
# Forms
####################


class ModelResponse(BaseModel):
    id: str
    name: str
    meta: ModelMeta
    updated_at: int  # timestamp in epoch
    created_at: int  # timestamp in epoch


class ModelForm(BaseModel):
    id: str
    base_model_id: Optional[str] = None
    name: str
    meta: ModelMeta
    params: ModelParams


class ModelsTable:
    def __init__(
        self,
        db: pw.SqliteDatabase | pw.PostgresqlDatabase,
    ):
        self.db = db
        self.db.create_tables([Model])

    def insert_new_model(
        self, form_data: ModelForm, user_id: str
    ) -> Optional[ModelModel]:
        try:
            model = ModelModel(
                **{
                    **form_data.model_dump(),
                    "user_id": user_id,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )
            result = Model.create(**model.model_dump())

            if result:
                return model
            else:
                return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_all_models(self) -> List[ModelModel]:
        try:
            return [ModelModel(**model_to_dict(model)) for model in Model.select()]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_model_by_id(self, id: str) -> Optional[ModelModel]:
        try:
            model = Model.get_or_none(Model.id == id)
            if model:
                return ModelModel(**model_to_dict(model))
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def update_model_by_id(self, id: str, model: ModelForm) -> Optional[ModelModel]:
        try:
            # update only the fields that are present in the model
            query = Model.update(**model.model_dump()).where(Model.id == id)
            query.execute()

            model = Model.get_or_none(Model.id == id)
            if model:
                return ModelModel(**model_to_dict(model))
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def delete_model_by_id(self, id: str) -> bool:
        try:
            query = Model.delete().where(Model.id == id)
            result: int = query.execute()
            return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False


Models = ModelsTable(DB)
