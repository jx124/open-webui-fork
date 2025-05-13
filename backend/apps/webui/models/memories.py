from pydantic import BaseModel
import peewee as pw
from playhouse.shortcuts import model_to_dict
from typing import List, Optional

from apps.webui.internal.db import DB

import time
import uuid

import logging
from config import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# Memory DB Schema
####################


class Memory(pw.Model):
    id = pw.CharField(unique=True)
    user_id = pw.CharField()
    content = pw.TextField()
    updated_at = pw.BigIntegerField()
    created_at = pw.BigIntegerField()

    class Meta:
        database = DB


class MemoryModel(BaseModel):
    id: str
    user_id: str
    content: str
    updated_at: int  # timestamp in epoch
    created_at: int  # timestamp in epoch


####################
# Forms
####################


class MemoriesTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([Memory])

    def insert_new_memory(
        self,
        user_id: str,
        content: str,
    ) -> Optional[MemoryModel]:
        try:
            id = str(uuid.uuid4())

            memory = MemoryModel(
                **{
                    "id": id,
                    "user_id": user_id,
                    "content": content,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )
            result = Memory.create(**memory.model_dump())
            if result:
                return memory
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_memories(self) -> List[MemoryModel]:
        try:
            memories = Memory.select()
            return [MemoryModel(**model_to_dict(memory)) for memory in memories]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_memories_by_user_id(self, user_id: str) -> List[MemoryModel]:
        try:
            memories = Memory.select().where(Memory.user_id == user_id)
            return [MemoryModel(**model_to_dict(memory)) for memory in memories]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_memory_by_id(self, id: str) -> Optional[MemoryModel]:
        try:
            memory = Memory.get_or_none(Memory.id == id)
            if memory:
                return MemoryModel(**model_to_dict(memory))
            return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def delete_memory_by_id(self, id: str) -> bool:
        try:
            query = Memory.delete().where(Memory.id == id)
            result: int = query.execute()  # Remove the rows, return number of rows removed.

            return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def delete_memories_by_user_id(self, user_id: str) -> bool:
        try:
            query = Memory.delete().where(Memory.user_id == user_id)
            result: int = query.execute()

            return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False

    def delete_memory_by_id_and_user_id(self, id: str, user_id: str) -> bool:
        try:
            query = Memory.delete().where(Memory.id == id, Memory.user_id == user_id)
            result: int = query.execute()

            return result != 0

        except Exception:
            log.exception(" Exception caught in model method.")
            return False


Memories = MemoriesTable(DB)
