from pydantic import BaseModel
from typing import List, Optional
import peewee as pw
from playhouse.shortcuts import model_to_dict

import uuid
import time

from apps.webui.internal.db import DB

import logging
from config import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# Tag DB Schema
####################


class Tag(pw.Model):
    id = pw.CharField(unique=True)
    name = pw.CharField()
    user_id = pw.CharField()
    data = pw.TextField(null=True)

    class Meta:
        database = DB


class ChatIdTag(pw.Model):
    id = pw.CharField(unique=True)
    tag_name = pw.CharField()
    chat_id = pw.CharField()
    user_id = pw.CharField()
    timestamp = pw.BigIntegerField()

    class Meta:
        database = DB


class TagModel(BaseModel):
    id: str
    name: str
    user_id: str
    data: Optional[str] = None


class ChatIdTagModel(BaseModel):
    id: str
    tag_name: str
    chat_id: str
    user_id: str
    timestamp: int


####################
# Forms
####################


class ChatIdTagForm(BaseModel):
    tag_name: str
    chat_id: str


class TagChatIdsResponse(BaseModel):
    chat_ids: List[str]


class ChatTagsResponse(BaseModel):
    tags: List[str]


class TagTable:
    def __init__(self, db):
        self.db = db
        db.create_tables([Tag, ChatIdTag])

    def insert_new_tag(self, name: str, user_id: str) -> Optional[TagModel]:
        id = str(uuid.uuid4())
        tag = TagModel(**{"id": id, "user_id": user_id, "name": name})
        try:
            result = Tag.create(**tag.model_dump())
            if result:
                return tag
            else:
                return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_tag_by_name_and_user_id(self, name: str, user_id: str) -> Optional[TagModel]:
        try:
            tag = Tag.get_or_none(Tag.name == name, Tag.user_id == user_id)
            if tag:
                return TagModel(**model_to_dict(tag))
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def add_tag_to_chat(self, user_id: str, form_data: ChatIdTagForm) -> Optional[ChatIdTagModel]:
        try:
            tag: TagModel
            opt_tag = self.get_tag_by_name_and_user_id(form_data.tag_name, user_id)

            if opt_tag is None:
                new_tag = self.insert_new_tag(form_data.tag_name, user_id)
                if new_tag is None:
                    return None
                tag = new_tag
            else:
                tag = opt_tag

            id = str(uuid.uuid4())
            chatIdTag = ChatIdTagModel(
                **{
                    "id": id,
                    "user_id": user_id,
                    "chat_id": form_data.chat_id,
                    "tag_name": tag.name,
                    "timestamp": int(time.time()),
                }
            )

            result = ChatIdTag.create(**chatIdTag.model_dump())
            if result:
                return chatIdTag
            else:
                return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_tags_by_user_id(self, user_id: str) -> List[TagModel]:
        try:
            tag_names = [
                ChatIdTagModel(**model_to_dict(chat_id_tag)).tag_name
                for chat_id_tag in ChatIdTag.select()
                .where(ChatIdTag.user_id == user_id)
                .order_by(ChatIdTag.timestamp.desc())
            ]

            return [
                TagModel(**model_to_dict(tag))
                for tag in Tag.select()
                .where(Tag.user_id == user_id)
                .where(Tag.name.in_(tag_names))
            ]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_tags_by_chat_id_and_user_id(self, chat_id: str, user_id: str) -> List[TagModel]:
        try:
            tag_names = [
                ChatIdTagModel(**model_to_dict(chat_id_tag)).tag_name
                for chat_id_tag in ChatIdTag.select()
                .where((ChatIdTag.user_id == user_id) & (ChatIdTag.chat_id == chat_id))
                .order_by(ChatIdTag.timestamp.desc())
            ]

            return [
                TagModel(**model_to_dict(tag))
                for tag in Tag.select()
                .where(Tag.user_id == user_id)
                .where(Tag.name.in_(tag_names))
            ]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_chat_ids_by_tag_name_and_user_id(self, tag_name: str, user_id: str) -> List[ChatIdTagModel]:
        try:
            return [
                ChatIdTagModel(**model_to_dict(chat_id_tag))
                for chat_id_tag in ChatIdTag.select()
                .where((ChatIdTag.user_id == user_id) & (ChatIdTag.tag_name == tag_name))
                .order_by(ChatIdTag.timestamp.desc())
            ]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def count_chat_ids_by_tag_name_and_user_id(self, tag_name: str, user_id: str) -> int:
        try:
            count: int = ChatIdTag.select()\
                .where((ChatIdTag.tag_name == tag_name) & (ChatIdTag.user_id == user_id))\
                .count()
            return count

        except Exception:
            log.exception(" Exception caught in model method.")
            return 0

    def delete_tag_by_tag_name_and_user_id(self, tag_name: str, user_id: str) -> bool:
        try:
            with self.db.atomic():
                query = ChatIdTag.delete().where(
                    (ChatIdTag.tag_name == tag_name) & (ChatIdTag.user_id == user_id)
                )
                result: int = query.execute()  # Remove the rows, return number of rows removed.

                tag_count = self.count_chat_ids_by_tag_name_and_user_id(tag_name, user_id)
                if tag_count == 0:
                    # Remove tag item from Tag col as well
                    query = Tag.delete().where(
                        (Tag.name == tag_name) & (Tag.user_id == user_id)
                    )
                    result += query.execute()  # Remove the rows, return number of rows removed.

                return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def delete_tag_by_tag_name_and_chat_id_and_user_id(self, tag_name: str, chat_id: str, user_id: str) -> bool:
        try:
            with self.db.atomic():
                query = ChatIdTag.delete().where(
                    (ChatIdTag.tag_name == tag_name)
                    & (ChatIdTag.chat_id == chat_id)
                    & (ChatIdTag.user_id == user_id)
                )
                result: int = query.execute()  # Remove the rows, return number of rows removed.

                tag_count = self.count_chat_ids_by_tag_name_and_user_id(tag_name, user_id)
                if tag_count == 0:
                    # Remove tag item from Tag col as well
                    query = Tag.delete().where(
                        (Tag.name == tag_name) & (Tag.user_id == user_id)
                    )
                    tag_result: int = query.execute()  # Remove the rows, return number of rows removed.
                    result += tag_result

                return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def delete_tags_by_chat_id_and_user_id(self, chat_id: str, user_id: str) -> bool:
        try:
            with self.db.atomic():
                tags = self.get_tags_by_chat_id_and_user_id(chat_id, user_id)
                result = True

                for tag in tags:
                    result &= self.delete_tag_by_tag_name_and_chat_id_and_user_id(
                        tag.tag_name, chat_id, user_id
                    )

                return result

        except Exception:
            log.exception(" Exception caught in model method.")
            return False


Tags = TagTable(DB)
