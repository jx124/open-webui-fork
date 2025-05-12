from pydantic import BaseModel
import peewee as pw
from playhouse.shortcuts import model_to_dict
from typing import List, Optional
import time

from apps.webui.internal.db import DB

import json

import logging
from config import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# Documents DB Schema
####################


class Document(pw.Model):
    collection_name = pw.CharField(unique=True)
    name = pw.CharField(unique=True)
    title = pw.TextField()
    filename = pw.TextField()
    content = pw.TextField(null=True)
    user_id = pw.CharField()
    timestamp = pw.BigIntegerField()

    class Meta:
        database = DB


class DocumentModel(BaseModel):
    collection_name: str
    name: str
    title: str
    filename: str
    content: Optional[str] = None
    user_id: str
    timestamp: int  # timestamp in epoch


####################
# Forms
####################


class DocumentResponse(BaseModel):
    collection_name: str
    name: str
    title: str
    filename: str
    content: Optional[dict] = None
    user_id: str
    timestamp: int  # timestamp in epoch


class DocumentUpdateForm(BaseModel):
    name: str
    title: str


class DocumentForm(DocumentUpdateForm):
    collection_name: str
    filename: str
    content: Optional[str] = None


class DocumentsTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([Document])

    def insert_new_doc(
        self, user_id: str, form_data: DocumentForm
    ) -> Optional[DocumentModel]:
        try:
            document = DocumentModel(
                **{
                    **form_data.model_dump(),
                    "user_id": user_id,
                    "timestamp": int(time.time()),
                }
            )

            result = Document.create(**document.model_dump())
            if result:
                return document
            else:
                return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_doc_by_name(self, name: str) -> Optional[DocumentModel]:
        try:
            document = Document.get_or_none(Document.name == name)
            if document:
                return DocumentModel(**model_to_dict(document))
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_docs(self) -> List[DocumentModel]:
        try:
            return [
                DocumentModel(**model_to_dict(doc))
                for doc in Document.select()
            ]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def update_doc_by_name(
        self, name: str, form_data: DocumentUpdateForm
    ) -> Optional[DocumentModel]:
        try:
            query = Document.update(
                title=form_data.title,
                name=form_data.name,
                timestamp=int(time.time()),
            ).where(Document.name == name)
            result = query.execute()

            if result:
                return self.get_doc_by_name(name)
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def update_doc_content_by_name(
        self, name: str, updated: dict
    ) -> Optional[DocumentModel]:
        try:
            doc = self.get_doc_by_name(name)
            doc_content = json.loads(doc.content if doc.content else "{}")
            doc_content = {**doc_content, **updated}

            query = Document.update(
                content=json.dumps(doc_content),
                timestamp=int(time.time()),
            ).where(Document.name == name)
            result = query.execute()

            if result:
                return self.get_doc_by_name(name)
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def delete_doc_by_name(self, name: str) -> bool:
        try:
            query = Document.delete().where((Document.name == name))
            result = query.execute()  # Remove the rows, return number of rows removed.

            return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False


Documents = DocumentsTable(DB)
