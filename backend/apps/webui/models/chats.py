from pydantic import BaseModel
from typing import List, Optional
import peewee as pw
from playhouse.shortcuts import model_to_dict

import json
import uuid
import time

from apps.webui.internal.db import DB

import logging
from config import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# Chat DB Schema
####################


class Chat(pw.Model):
    id = pw.CharField(unique=True)
    user_id = pw.CharField()
    title = pw.TextField()
    chat = pw.TextField()  # Save Chat JSON as Text

    created_at = pw.BigIntegerField()
    updated_at = pw.BigIntegerField()

    share_id = pw.CharField(null=True, unique=True)
    archived = pw.BooleanField(default=False)

    session_time = pw.BigIntegerField(default=0)  # Chat session length in seconds
    visits = pw.BigIntegerField(default=0)        # Number of visits to this chat session

    class_id = pw.IntegerField(null=True)   # Not using foreign key field since that leads to an error with postgres
    prompt_id = pw.IntegerField(null=True)  # Not using foreign key field since that leads to an error with postgres

    is_submitted = pw.BooleanField(default=False)
    is_disabled = pw.BooleanField(default=False)

    class Meta:
        database = DB


class ChatModel(BaseModel):
    id: str
    user_id: str
    title: str
    chat: str

    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch

    share_id: Optional[str] = None
    archived: bool = False

    session_time: int = 0
    visits: int = 0

    class_id: Optional[int] = None
    prompt_id: Optional[int] = None

    is_submitted: bool = False
    is_disabled: bool = False


####################
# Forms
####################


class ChatForm(BaseModel):
    chat: dict[str, object]     # TODO: formalize chat json fields


class ChatTitleForm(BaseModel):
    title: str


class ChatTimingForm(BaseModel):
    timings: dict[str, int]     # map of chat_id to time spent in seconds


class ChatResponse(BaseModel):
    id: str
    user_id: str
    title: str
    chat: dict[str, object]     # TODO: formalize chat json fields
    updated_at: int  # timestamp in epoch
    created_at: int  # timestamp in epoch
    share_id: Optional[str] = None  # id of the chat to be shared
    archived: bool
    class_id: Optional[int] = None
    prompt_id: Optional[int] = None
    is_submitted: bool = False
    is_disabled: bool = False


class ChatTitleIdResponse(BaseModel):
    id: str
    title: str
    class_id: Optional[int] = None
    prompt_id: Optional[int] = None
    updated_at: int
    created_at: int


class ChatInfoResponse(BaseModel):
    id: str
    title: str
    token_count: int
    session_time: int
    visits: int
    updated_at: int
    created_at: int
    class_id: Optional[int] = None
    prompt_id: Optional[int] = None
    is_submitted: bool = False
    is_disabled: bool = False


class ChatTable:
    def __init__(self, db):
        self.db = db
        db.create_tables([Chat])

    def insert_new_chat(self, user_id: str, form_data: ChatForm) -> Optional[ChatModel]:
        try:
            id = str(uuid.uuid4())
            chat = ChatModel(
                **{
                    "id": id,
                    "user_id": user_id,
                    "title": (
                        form_data.chat["title"] if "title" in form_data.chat else "New Chat"
                    ),
                    "chat": json.dumps(form_data.chat),
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                    "class_id": form_data.chat.get("class_id", None),
                    "prompt_id": form_data.chat.get("prompt_id", None),
                }
            )

            result = Chat.create(**chat.model_dump())
            return chat if result else None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def update_chat_by_id(self, id: str, chat: dict[str, object]) -> Optional[ChatModel]:
        try:
            query = Chat.update(
                chat=json.dumps(chat),
                title=chat["title"] if "title" in chat else "New Chat",
                updated_at=int(time.time()),
            ).where(Chat.id == id)
            query.execute()

            chat = Chat.get_or_none(Chat.id == id)
            if chat:
                return ChatModel(**model_to_dict(chat, recurse=False))
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def update_chat_session_times(self, user_id: str, data: ChatTimingForm) -> bool:
        timings = data.timings

        try:
            for chat_id, timing in timings.items():
                query = Chat.update(
                    session_time=Chat.session_time + timing
                ).where((Chat.id == chat_id) & (Chat.user_id == user_id))
                query.execute()

            return True

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def insert_shared_chat_by_chat_id(self, chat_id: str) -> Optional[ChatModel]:
        try:
            # Get the existing chat to share
            chat = Chat.get_or_none(Chat.id == chat_id)
            # Check if the chat is already shared
            if chat and chat.share_id:
                return self.get_chat_by_id_and_user_id(chat.share_id, "shared")
            # Create a new chat with the same data, but with a new ID
            shared_chat = ChatModel(
                **{
                    "id": str(uuid.uuid4()),
                    "user_id": f"shared-{chat_id}",
                    "title": chat.title,
                    "chat": chat.chat,
                    "created_at": chat.created_at,
                    "updated_at": int(time.time()),
                    "class_id": chat.get("class_id", None),
                    "prompt_id": chat.get("prompt_id", None),
                }
            )
            shared_result = Chat.create(**shared_chat.model_dump())
            # Update the original chat with the share_id
            result = (
                Chat.update(share_id=shared_chat.id).where(Chat.id == chat_id).execute()
            )

            return shared_chat if (shared_result and result) else None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def update_shared_chat_by_chat_id(self, chat_id: str) -> Optional[ChatModel]:
        try:
            chat = Chat.get_or_none(Chat.id == chat_id)

            if chat is None:
                return None

            query = Chat.update(
                title=chat.title,
                chat=chat.chat,
            ).where(Chat.id == chat.share_id)

            query.execute()

            chat = Chat.get_or_none(Chat.id == chat.share_id)
            return ChatModel(**model_to_dict(chat, recurse=False))

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def delete_shared_chat_by_chat_id(self, chat_id: str) -> bool:
        try:
            query = Chat.delete().where(Chat.user_id == f"shared-{chat_id}")
            result: int = query.execute()  # Remove the rows, return number of rows removed.

            return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def update_chat_share_id_by_id(self, id: str, share_id: Optional[str]) -> Optional[ChatModel]:
        try:
            query = Chat.update(
                share_id=share_id,
            ).where(Chat.id == id)
            result = query.execute()

            if result:
                chat = Chat.get_or_none(Chat.id == id)
                return ChatModel(**model_to_dict(chat, recurse=False))
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def toggle_chat_archive_by_id(self, id: str) -> Optional[ChatModel]:
        try:
            chat = self.get_chat_by_id(id)

            if chat is None:
                return None

            query = Chat.update(
                archived=(not chat.archived),
            ).where(Chat.id == id)

            result = query.execute()

            if result:
                chat = Chat.get_or_none(Chat.id == id)
                return ChatModel(**model_to_dict(chat, recurse=False))
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def archive_all_chats_by_user_id(self, user_id: str) -> bool:
        try:
            chats = self.get_chats_by_user_id(user_id)
            result = 0
            for chat in chats:
                query = Chat.update(
                    archived=True,
                ).where(Chat.id == chat.id)

                result += query.execute()

            return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def get_archived_chat_list_by_user_id(self, user_id: str, skip: int = 0, limit: int = 50) -> List[ChatModel]:
        try:
            return [
                ChatModel(**model_to_dict(chat, recurse=False))
                for chat in Chat.select()
                .where(Chat.archived == True)
                .where(Chat.user_id == user_id)
                .order_by(Chat.updated_at.desc())
            ]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_chat_list_by_user_id(
        self,
        user_id: str,
        include_archived: bool = False,
    ) -> List[ChatModel]:
        try:
            if include_archived:
                return [
                    ChatModel(**model_to_dict(chat, recurse=False))
                    for chat in Chat.select()
                    .where(Chat.user_id == user_id)
                    .order_by(Chat.updated_at.desc())
                ]
            else:
                return [
                    ChatModel(**model_to_dict(chat, recurse=False))
                    for chat in Chat.select()
                    .where(Chat.archived == False)
                    .where(Chat.user_id == user_id)
                    .order_by(Chat.updated_at.desc())
                ]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_chat_list_by_chat_ids(
        self, chat_ids: List[str], skip: int = 0, limit: int = 50
    ) -> List[ChatModel]:
        try:
            return [
                ChatModel(**model_to_dict(chat, recurse=False))
                for chat in Chat.select()
                .where(Chat.archived == False)
                .where(Chat.id.in_(chat_ids))
                .order_by(Chat.updated_at.desc())
            ]
        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_chat_by_id(self, id: str) -> Optional[ChatModel]:
        try:
            chat = Chat.get_or_none(Chat.id == id)
            if chat:
                return ChatModel(**model_to_dict(chat, recurse=False))
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_chat_by_share_id(self, id: str) -> Optional[ChatModel]:
        try:
            chat = Chat.get_or_none(Chat.share_id == id)

            if chat:
                chat = Chat.get_or_none(Chat.id == id)
                return ChatModel(**model_to_dict(chat, recurse=False))
            else:
                return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_chat_by_id_and_user_id(self, id: str, user_id: str) -> Optional[ChatModel]:
        try:
            chat = Chat.get_or_none(Chat.id == id, Chat.user_id == user_id)
            if chat:
                return ChatModel(**model_to_dict(chat, recurse=False))
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def increment_chat_visits(self, id: str, user_id: str) -> bool:
        try:
            # check user id so admin visiting chat does not increment visits
            result: int = Chat.update(visits=Chat.visits + 1)\
                    .where((Chat.id == id) & (Chat.user_id == user_id)).execute()
            return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def get_chats(self, skip: int = 0, limit: int = 50) -> List[ChatModel]:
        try:
            return [
                ChatModel(**model_to_dict(chat, recurse=False))
                for chat in Chat.select().order_by(Chat.updated_at.desc())
            ]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_chats_by_user_id(self, user_id: str) -> List[ChatModel]:
        try:
            return [
                ChatModel(**model_to_dict(chat, recurse=False))
                for chat in Chat.select()
                .where(Chat.user_id == user_id)
                .order_by(Chat.updated_at.desc())
            ]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_archived_chats_by_user_id(self, user_id: str) -> List[ChatModel]:
        try:
            return [
                ChatModel(**model_to_dict(chat, recurse=False))
                for chat in Chat.select()
                .where(Chat.archived == True)
                .where(Chat.user_id == user_id)
                .order_by(Chat.updated_at.desc())
            ]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def delete_chats_by_prompt_id(self, prompt_id: int) -> int:
        try:
            query = Chat.delete().where(Chat.prompt_id == prompt_id)
            result = query.execute()

            return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return 0

    def delete_chat_by_id(self, id: str) -> bool:
        try:
            query = Chat.delete().where((Chat.id == id))
            result = query.execute()  # Remove the rows, return number of rows removed.

            return result != 0 and self.delete_shared_chat_by_chat_id(id)

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def delete_chat_by_id_and_user_id(self, id: str, user_id: str) -> bool:
        try:
            query = Chat.delete().where((Chat.id == id) & (Chat.user_id == user_id))
            result = query.execute()  # Remove the rows, return number of rows removed.

            return result != 0 and self.delete_shared_chat_by_chat_id(id)

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def delete_chats_by_user_id(self, user_id: str) -> bool:
        try:
            self.delete_shared_chats_by_user_id(user_id)

            query = Chat.delete().where(Chat.user_id == user_id)
            query.execute()  # Remove the rows, return number of rows removed.

            return True

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def delete_shared_chats_by_user_id(self, user_id: str) -> bool:
        try:
            shared_chat_ids = [
                f"shared-{chat.id}"
                for chat in Chat.select().where(Chat.user_id == user_id)
            ]

            for shared_id in shared_chat_ids:
                query = Chat.delete().where(Chat.share_id == shared_id)
                query.execute()  # Remove the rows, return number of rows removed.

            return True

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def disable_chat_by_id(self, user_id: str, chat_id: str) -> bool:
        try:
            query = Chat.update(is_disabled=True).where((Chat.user_id == user_id) & (Chat.id == chat_id))
            result: int = query.execute()

            return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def submit_chat_by_id(self, user_id: str, chat_id: str) -> bool:
        try:
            query = Chat.update(is_submitted=True).where((Chat.user_id == user_id) & (Chat.id == chat_id))
            result: int = query.execute()

            return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def check_chat_assignment_submission_by_id(self, user_id: str, chat_id: str) -> bool:
        try:
            chat = Chat.select(Chat.class_id, Chat.prompt_id).where((Chat.id == chat_id)).get_or_none()
            if chat:
                count: int = Chat.select(Chat.id).where(
                        (Chat.user_id == user_id) & (Chat.is_submitted == True)
                        & (Chat.class_id == chat.class_id) & (Chat.prompt_id == chat.prompt_id)).count()
                return count != 0
            return False

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def remove_class_reference(self, class_id: int) -> bool:
        try:
            query = Chat.update(class_id=None).where(Chat.class_id == class_id)
            result: int = query.execute()

            return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False


Chats = ChatTable(DB)
