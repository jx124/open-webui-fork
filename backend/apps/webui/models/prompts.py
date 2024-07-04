from pydantic import BaseModel
from peewee import *
from playhouse.shortcuts import model_to_dict
from typing import List, Union, Optional
import time

from utils.utils import decode_token
from utils.misc import get_gravatar_url

from apps.webui.internal.db import DB

import json

####################
# Prompts DB Schema
####################


class Prompt(Model):
    command = CharField(unique=True)
    user_id = CharField()
    title = TextField()
    content = TextField()
    timestamp = BigIntegerField()
    is_visible = BooleanField(default=True)
    additional_info = TextField(default="")

    class Meta:
        database = DB


class PromptModel(BaseModel):
    command: str
    user_id: str
    title: str
    content: str
    timestamp: int  # timestamp in epoch
    is_visible: bool   # whether prompt is visible to others
    additional_info: str

####################
# Forms
####################


class PromptForm(BaseModel):
    command: str
    title: str
    content: str
    is_visible: bool
    additional_info: str


class PromptsTable:

    def __init__(self, db):
        self.db = db
        self.db.create_tables([Prompt])

    def insert_new_prompt(
        self, user_id: str, form_data: PromptForm
    ) -> Optional[PromptModel]:
        prompt = PromptModel(
            **{
                "user_id": user_id,
                "command": form_data.command,
                "title": form_data.title,
                "content": form_data.content,
                "timestamp": int(time.time()),
                "is_visible": form_data.is_visible,
                "additional_info": form_data.additional_info
            }
        )

        try:
            result = Prompt.create(**prompt.model_dump())
            if result:
                return prompt
            else:
                return None
        except:
            return None

    def get_prompt_by_command(self, user_id: str, command: str) -> Optional[PromptModel]:
        try:
            prompt = None
            if (user_id):
                prompt = Prompt.get(Prompt.command == command).where((Prompt.is_visible == True) | (Prompt.user_id == user_id))
            else:
                # If no user_id is provided, return all prompts
                # This is needed to prevent collisions when creating prompts
                prompt = Prompt.get(Prompt.command == command)
            return PromptModel(**model_to_dict(prompt))
        except:
            return None

    def get_prompts(self, user_id: str) -> List[PromptModel]:
        return [
            PromptModel(**model_to_dict(prompt))
            for prompt in Prompt.select().where((Prompt.is_visible == True) | (Prompt.user_id == user_id))
            # .limit(limit).offset(skip)
        ]

    def update_prompt_by_command(
        self, user_id: str, command: str, form_data: PromptForm
    ) -> Optional[PromptModel]:
        try:
            query = Prompt.update(
                title=form_data.title,
                content=form_data.content,
                timestamp=int(time.time()),
                is_visible=form_data.is_visible,
                additional_info=form_data.additional_info
            ).where(Prompt.command == command, (Prompt.is_visible == True) | (Prompt.user_id == user_id))

            query.execute()

            prompt = Prompt.get(Prompt.command == command, Prompt.user_id == user_id)
            return PromptModel(**model_to_dict(prompt))
        except:
            return None

    def delete_prompt_by_command(self, user_id: str, command: str) -> bool:
        try:
            query = Prompt.delete().where(
                Prompt.command == command,
                (Prompt.is_visible == True) | (Prompt.user_id == user_id)
            )
            query.execute()  # Remove the rows, return number of rows removed.

            return True
        except:
            return False


Prompts = PromptsTable(DB)
