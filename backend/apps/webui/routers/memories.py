from fastapi import Request
from fastapi import Depends, HTTPException
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel
import logging

from apps.webui.models.memories import Memories, MemoryModel
from apps.webui.models.users import UserModel

from utils.utils import get_verified_user

from constants import ERROR_MESSAGES

from config import SRC_LOG_LEVELS, CHROMA_CLIENT

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

router = APIRouter()


@router.get("/ef")
async def get_embeddings(request: Request):
    return {"result": request.app.state.EMBEDDING_FUNCTION("hello world")}


############################
# GetMemories
############################


@router.get("/", response_model=List[MemoryModel])
async def get_memories(user: UserModel = Depends(get_verified_user)) -> List[MemoryModel]:
    result: List[MemoryModel] = Memories.get_memories_by_user_id(user.id)
    return result


############################
# AddMemory
############################


class AddMemoryForm(BaseModel):
    content: str


@router.post("/add", response_model=Optional[MemoryModel])
async def add_memory(
    request: Request, form_data: AddMemoryForm, user: UserModel = Depends(get_verified_user)
) -> Optional[MemoryModel]:
    memory = Memories.insert_new_memory(user.id, form_data.content)
    if memory is None:
        raise HTTPException(status_code=400, detail=ERROR_MESSAGES.DEFAULT())

    memory_embedding = request.app.state.EMBEDDING_FUNCTION(memory.content)

    collection = CHROMA_CLIENT.get_or_create_collection(name=f"user-memory-{user.id}")
    collection.upsert(
        documents=[memory.content],
        ids=[memory.id],
        embeddings=[memory_embedding],
        metadatas=[{"created_at": memory.created_at}],
    )

    return memory


############################
# QueryMemory
############################


class QueryMemoryForm(BaseModel):
    content: str


@router.post("/query")
async def query_memory(
    request: Request, form_data: QueryMemoryForm, user: UserModel = Depends(get_verified_user)
):
    query_embedding = request.app.state.EMBEDDING_FUNCTION(form_data.content)
    collection = CHROMA_CLIENT.get_or_create_collection(name=f"user-memory-{user.id}")

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1,  # how many results to return
    )

    return results


############################
# ResetMemoryFromVectorDB
############################
@router.get("/reset", response_model=bool)
async def reset_memory_from_vector_db(
    request: Request, user: UserModel = Depends(get_verified_user)
) -> bool:
    CHROMA_CLIENT.delete_collection(f"user-memory-{user.id}")
    collection = CHROMA_CLIENT.get_or_create_collection(name=f"user-memory-{user.id}")

    memories = Memories.get_memories_by_user_id(user.id)
    for memory in memories:
        memory_embedding = request.app.state.EMBEDDING_FUNCTION(memory.content)
        collection.upsert(
            documents=[memory.content],
            ids=[memory.id],
            embeddings=[memory_embedding],
        )
    return True


############################
# DeleteMemoriesByUserId
############################


@router.delete("/user", response_model=bool)
async def delete_memory_by_user_id(user: UserModel = Depends(get_verified_user)) -> bool:
    result = Memories.delete_memories_by_user_id(user.id)

    if result:
        try:
            CHROMA_CLIENT.delete_collection(f"user-memory-{user.id}")
        except Exception as e:
            log.error(e)
        return True

    return False


############################
# DeleteMemoryById
############################


@router.delete("/{memory_id}", response_model=bool)
async def delete_memory_by_id(memory_id: str, user: UserModel = Depends(get_verified_user)) -> bool:
    result = Memories.delete_memory_by_id_and_user_id(memory_id, user.id)

    if result:
        collection = CHROMA_CLIENT.get_or_create_collection(
            name=f"user-memory-{user.id}"
        )
        collection.delete(ids=[memory_id])
        return True

    return False
