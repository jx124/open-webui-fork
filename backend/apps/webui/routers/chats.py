from collections import defaultdict
from fastapi import Depends, Request, HTTPException, status
from typing import Dict, List, Optional
from utils.utils import get_admin_or_instructor, get_current_user
from fastapi import APIRouter
from pydantic import BaseModel
import json
import logging

from apps.webui.models.prompts_classes import Classes
from apps.webui.models.users import Users
from apps.webui.models.chats import (
    ChatResponse,
    ChatTimingForm,
    ChatForm,
    ChatTitleIdResponse,
    ChatInfoResponse,
    Chats,
)


from apps.webui.models.tags import (
    TagModel,
    ChatIdTagModel,
    ChatIdTagForm,
    Tags,
)

from constants import ERROR_MESSAGES

from config import SRC_LOG_LEVELS, ENABLE_ADMIN_EXPORT

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

router = APIRouter()

############################
# GetChatList
############################


@router.get("/", response_model=List[ChatTitleIdResponse])
@router.get("/list", response_model=List[ChatTitleIdResponse])
async def get_session_user_chat_list(
    user=Depends(get_current_user)
):
    return Chats.get_chat_list_by_user_id(user.id)


############################
# DeleteAllChats
############################


@router.delete("/", response_model=bool)
async def delete_all_user_chats(request: Request, user=Depends(get_current_user)):

    if (
        user.role != "admin"
        and not request.app.state.config.USER_PERMISSIONS["chat"]["deletion"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    result = Chats.delete_chats_by_user_id(user.id)
    return result


############################
# GetUserChatList
############################


@router.get("/list/user/{user_id}", response_model=List[ChatInfoResponse])
async def get_user_chat_list_by_user_id(
    user_id: str, user=Depends(get_admin_or_instructor)
):
    chats = []
    if user.role == "admin":
        chats = Chats.get_chat_list_by_user_id(
            user_id, include_archived=True
        )
    elif user.role == "instructor":
        chats = Classes.get_chat_list_by_user_id_and_instructor(
            user_id, user.id, include_archived=True
        )

    # TODO: create a separate field in database for token_count? 
    results = []
    for chat in chats:
        token_count = 0
        usage = json.loads(chat.chat).get("usage")
        if usage is not None:
            token_count = usage.get("total_tokens", 0)

        results.append(ChatInfoResponse(**{**chat.model_dump(), "token_count": token_count}))

    return results


############################
# GetAssignmentChatsByUserId
############################


@router.get("/list/users", response_model=Dict[str, List[ChatInfoResponse]])
async def get_assignment_chats_by_user_id(
    user=Depends(get_admin_or_instructor)
):
    chats = []
    if user.role == "admin":
        chats = Chats.get_chats()
    elif user.role == "instructor":
        chats = Classes.get_chats_by_instructor(user.id)

    results = defaultdict(lambda: [])
    for chat in chats:
        token_count = 0
        usage = json.loads(chat.chat).get("usage")
        if usage is not None:
            token_count = usage.get("total_tokens", 0)

        results[chat.user_id].append(ChatInfoResponse(**{**chat.model_dump(), "token_count": token_count}))

    return results



############################
# CreateNewChat
############################


@router.post("/new", response_model=Optional[ChatResponse])
async def create_new_chat(form_data: ChatForm, user=Depends(get_current_user)):
    try:
        chat = Chats.insert_new_chat(user.id, form_data)
        Users.increment_user_chat_attempts_by_id(user.id)

        return ChatResponse(**{**chat.model_dump(), "chat": json.loads(chat.chat)})
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.DEFAULT()
        )


############################
# GetChats
############################


@router.get("/all", response_model=List[ChatResponse])
async def get_user_chats(user=Depends(get_current_user)):
    return [
        ChatResponse(**{**chat.model_dump(), "chat": json.loads(chat.chat)})
        for chat in Chats.get_chats_by_user_id(user.id)
    ]


############################
# GetArchivedChats
############################


@router.get("/all/archived", response_model=List[ChatResponse])
async def get_user_chats(user=Depends(get_current_user)):
    return [
        ChatResponse(**{**chat.model_dump(), "chat": json.loads(chat.chat)})
        for chat in Chats.get_archived_chats_by_user_id(user.id)
    ]


############################
# GetAllChatsInDB
############################


@router.get("/all/db", response_model=List[ChatResponse])
async def get_all_user_chats_in_db(user=Depends(get_admin_or_instructor)):
    if not ENABLE_ADMIN_EXPORT:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )
    
    if user.role == "admin":
        return [
            ChatResponse(**{**chat.model_dump(), "chat": json.loads(chat.chat)})
            for chat in Chats.get_chats()
        ]
    else:
        return [
            ChatResponse(**{**chat.model_dump(), "chat": json.loads(chat.chat)})
            for chat in Classes.get_chats_by_instructor(user.id)
        ]

############################
# GetArchivedChats
############################


@router.get("/archived", response_model=List[ChatTitleIdResponse])
async def get_archived_session_user_chat_list(
    user=Depends(get_current_user), skip: int = 0, limit: int = 50
):
    return Chats.get_archived_chat_list_by_user_id(user.id, skip, limit)


############################
# ArchiveAllChats
############################


@router.post("/archive/all", response_model=List[ChatTitleIdResponse])
async def archive_all_chats(user=Depends(get_current_user)):
    return Chats.archive_all_chats_by_user_id(user.id)


############################
# GetSharedChatById
############################


@router.get("/share/{share_id}", response_model=Optional[ChatResponse])
async def get_shared_chat_by_id(share_id: str, user=Depends(get_current_user)):
    if user.role == "admin" or user.role == "instructor":
        chat = Chats.get_chat_by_id(share_id)
    elif user.role == "instructor":
        chat = Classes.get_chat_by_id_and_instructor(user.id)
    else:
        chat = Chats.get_chat_by_share_id(share_id)

    if chat:
        return ChatResponse(**{**chat.model_dump(), "chat": json.loads(chat.chat)})
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_MESSAGES.NOT_FOUND
        )


############################
# GetChatsByTags
############################


class TagNameForm(BaseModel):
    name: str
    skip: Optional[int] = 0
    limit: Optional[int] = 50


@router.post("/tags", response_model=List[ChatTitleIdResponse])
async def get_user_chat_list_by_tag_name(
    form_data: TagNameForm, user=Depends(get_current_user)
):

    chat_ids = [
        chat_id_tag.chat_id
        for chat_id_tag in Tags.get_chat_ids_by_tag_name_and_user_id(
            form_data.name, user.id
        )
    ]

    chats = Chats.get_chat_list_by_chat_ids(chat_ids, form_data.skip, form_data.limit)

    if len(chats) == 0:
        Tags.delete_tag_by_tag_name_and_user_id(form_data.name, user.id)

    return chats


############################
# GetAllTags
############################


@router.get("/tags/all", response_model=List[TagModel])
async def get_all_tags(user=Depends(get_current_user)):
    try:
        tags = Tags.get_tags_by_user_id(user.id)
        return tags
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.DEFAULT()
        )


############################
# GetChatById
############################


@router.get("/{id}", response_model=Optional[ChatResponse])
async def get_chat_by_id(id: str, user=Depends(get_current_user)):
    chat = Chats.get_chat_by_id_and_user_id(id, user.id)

    if chat:
        Chats.increment_chat_visits(id, user.id)
        return ChatResponse(**{**chat.model_dump(), "chat": json.loads(chat.chat)})
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_MESSAGES.NOT_FOUND
        )


############################
# UpdateChatById
############################


@router.post("/{id}", response_model=Optional[ChatResponse])
async def update_chat_by_id(
    id: str, form_data: ChatForm, user=Depends(get_current_user)
):
    chat = Chats.get_chat_by_id_and_user_id(id, user.id)
    if chat:
        updated_chat = {**json.loads(chat.chat), **form_data.chat}

        chat = Chats.update_chat_by_id(id, updated_chat)
        return ChatResponse(**{**chat.model_dump(), "chat": json.loads(chat.chat)})
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )


############################
# UpdateChatSessionTimes
############################


@router.post("/session/times", response_model=bool)
async def update_chat_session_times(
    timings: ChatTimingForm, user=Depends(get_current_user)
):
    result = Chats.update_chat_session_times(user.id, timings)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )
    
    total_time = 0
    for _, value in timings.timings.items():
        total_time += value

    result = Users.increment_user_session_time_by_id(user.id, total_time)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    return True


############################
# DeleteChatById
############################


@router.delete("/{id}", response_model=bool)
async def delete_chat_by_id(request: Request, id: str, user=Depends(get_current_user)):

    if user.role == "admin":
        result = Chats.delete_chat_by_id(id)
        return result
    else:
        if not request.app.state.config.USER_PERMISSIONS["chat"]["deletion"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
            )

        result = Chats.delete_chat_by_id_and_user_id(id, user.id)
        return result


############################
# CloneChat
############################


@router.get("/{id}/clone", response_model=Optional[ChatResponse])
async def clone_chat_by_id(id: str, user=Depends(get_current_user)):
    chat = Chats.get_chat_by_id_and_user_id(id, user.id)
    if chat:

        chat_body = json.loads(chat.chat)
        updated_chat = {
            **chat_body,
            "originalChatId": chat.id,
            "branchPointMessageId": chat_body["history"]["currentId"],
            "title": f"Clone of {chat.title}",
        }

        chat = Chats.insert_new_chat(user.id, ChatForm(**{"chat": updated_chat}))
        return ChatResponse(**{**chat.model_dump(), "chat": json.loads(chat.chat)})
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_MESSAGES.DEFAULT()
        )


############################
# ArchiveChat
############################


@router.get("/{id}/archive", response_model=Optional[ChatResponse])
async def archive_chat_by_id(id: str, user=Depends(get_current_user)):
    chat = Chats.get_chat_by_id_and_user_id(id, user.id)
    if chat:
        chat = Chats.toggle_chat_archive_by_id(id)
        return ChatResponse(**{**chat.model_dump(), "chat": json.loads(chat.chat)})
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_MESSAGES.DEFAULT()
        )


############################
# ShareChatById
############################


@router.post("/{id}/share", response_model=Optional[ChatResponse])
async def share_chat_by_id(id: str, user=Depends(get_current_user)):
    chat = Chats.get_chat_by_id_and_user_id(id, user.id)
    if chat:
        if chat.share_id:
            shared_chat = Chats.update_shared_chat_by_chat_id(chat.id)
            return ChatResponse(
                **{**shared_chat.model_dump(), "chat": json.loads(shared_chat.chat)}
            )

        shared_chat = Chats.insert_shared_chat_by_chat_id(chat.id)
        if not shared_chat:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR_MESSAGES.DEFAULT(),
            )

        return ChatResponse(
            **{**shared_chat.model_dump(), "chat": json.loads(shared_chat.chat)}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )


############################
# DeletedSharedChatById
############################


@router.delete("/{id}/share", response_model=Optional[bool])
async def delete_shared_chat_by_id(id: str, user=Depends(get_current_user)):
    chat = Chats.get_chat_by_id_and_user_id(id, user.id)
    if chat:
        if not chat.share_id:
            return False

        result = Chats.delete_shared_chat_by_chat_id(id)
        update_result = Chats.update_chat_share_id_by_id(id, None)

        return result and update_result != None
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )


############################
# GetChatTagsById
############################


@router.get("/{id}/tags", response_model=List[TagModel])
async def get_chat_tags_by_id(id: str, user=Depends(get_current_user)):
    tags = Tags.get_tags_by_chat_id_and_user_id(id, user.id)

    if tags != None:
        return tags
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_MESSAGES.NOT_FOUND
        )


############################
# AddChatTagById
############################


@router.post("/{id}/tags", response_model=Optional[ChatIdTagModel])
async def add_chat_tag_by_id(
    id: str, form_data: ChatIdTagForm, user=Depends(get_current_user)
):
    tags = Tags.get_tags_by_chat_id_and_user_id(id, user.id)

    if form_data.tag_name not in tags:
        tag = Tags.add_tag_to_chat(user.id, form_data)

        if tag:
            return tag
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.NOT_FOUND,
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_MESSAGES.DEFAULT()
        )


############################
# DeleteChatTagById
############################


@router.delete("/{id}/tags", response_model=Optional[bool])
async def delete_chat_tag_by_id(
    id: str, form_data: ChatIdTagForm, user=Depends(get_current_user)
):
    result = Tags.delete_tag_by_tag_name_and_chat_id_and_user_id(
        form_data.tag_name, id, user.id
    )

    if result:
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_MESSAGES.NOT_FOUND
        )


############################
# DeleteAllChatTagsById
############################


@router.delete("/{id}/tags/all", response_model=Optional[bool])
async def delete_all_chat_tags_by_id(id: str, user=Depends(get_current_user)):
    result = Tags.delete_tags_by_chat_id_and_user_id(id, user.id)

    if result:
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_MESSAGES.NOT_FOUND
        )
