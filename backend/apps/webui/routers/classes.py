from collections import defaultdict
import os
import shutil
import tempfile
from fastapi import BackgroundTasks, Depends, HTTPException, status
from typing import Dict, List, Optional

from fastapi import APIRouter
from fastapi.responses import FileResponse

from apps.webui.models.prompts_classes import ClassForm, ClassModel, ClassPrompts, Classes
from apps.webui.models.users import Users, UserModel
from apps.webui.models.chats import ChatModel
from utils.utils import get_admin_or_instructor, get_current_user
from constants import ERROR_MESSAGES

router = APIRouter()

############################
# GetClasses
############################


@router.get("/", response_model=List[ClassModel])
async def get_classes(user: UserModel = Depends(get_current_user)) -> List[ClassModel]:
    result: List[ClassModel] = Classes.get_classes(user.id, user.role)
    return result


############################
# CreateNewClass
############################


@router.post("/create", response_model=Optional[ClassModel])
async def create_new_class(
    form_data: ClassForm, user: UserModel = Depends(get_admin_or_instructor)
) -> Optional[ClassModel]:
    class_ = Classes.get_class_by_name(form_data.name)
    if class_ is None:
        class_ = Classes.insert_new_class(form_data)
        if class_:
            return class_

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(),
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ERROR_MESSAGES.CLASS_NAME_TAKEN(form_data.name),
    )


############################
# GetClassById
############################


@router.get("/{class_id}", response_model=Optional[ClassModel])
async def get_class_by_id(class_id: int, user: UserModel = Depends(get_admin_or_instructor)) -> Optional[ClassModel]:
    class_ = Classes.get_class_by_id(user.id, user.role, class_id)

    if class_:
        return class_

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
    )


############################
# getAssignmentSubmissions
############################


@router.get("/{class_id}/assignments/list", response_model=Dict[int, bool])
async def get_assignment_submissions(class_id: int, user: UserModel = Depends(get_current_user)) -> Dict[int, bool]:
    submissions: Dict[int, bool] = ClassPrompts.get_assignment_submission_by_class_and_user_id(class_id, user.id)
    return submissions

###########################
# UpdateClass
###########################


@router.post("/update", response_model=bool)
async def update_class_by_id(
    form_data: ClassForm, user: UserModel = Depends(get_admin_or_instructor)
) -> bool:
    # check if authorized
    class_ = Classes.get_class_by_id(user.id, user.role, form_data.id)
    if class_ is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    # check for name collision
    class_ = Classes.get_class_by_name(form_data.name)
    if class_ is None or class_.id == form_data.id:
        result: bool = Classes.update_class_by_id(form_data)
        if result:
            return result

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(),
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ERROR_MESSAGES.CLASS_NAME_TAKEN(form_data.name),
    )


############################
# DeleteClass
############################


@router.delete("/delete/{class_id}", response_model=bool)
async def delete_class_by_id(class_id: int, user: UserModel = Depends(get_admin_or_instructor)) -> bool:
    # check if authorized
    class_ = Classes.get_class_by_id(user.id, user.role, class_id)
    if class_ is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    result = Classes.delete_class_by_id(class_id)
    if result:
        return True

    raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(),
        )


############################
# DownloadChatsByClassId
############################

def cleanup(path: str) -> None:
    print("Deleting temporary directory", path)
    shutil.rmtree(path)


@router.get("/{class_id}/download")
async def download_chats_by_class_id(
    class_id: str, bg_tasks: BackgroundTasks, user: UserModel = Depends(get_admin_or_instructor)
) -> FileResponse:
    chats = []
    if user.role == "admin":
        chats = Classes.get_chats_by_class_id(class_id)
    elif user.role == "instructor":
        chats = Classes.get_chats_by_class_id_and_instructor(class_id, user.id)

    users = Users.get_user_names()
    name = Classes.get_class_name(class_id)
    class_name = "Unknown Class" if name is None else name

    user_attempts: defaultdict[str, List[ChatModel]] = defaultdict(lambda: [])

    for chat in chats:
        user_id = users.get(chat.user_id, "Deleted User")
        user_attempts[user_id].append(chat)

    tmp = tempfile.mkdtemp()
    print("Creating temporary directory", tmp)
    class_dir = os.path.join(tmp, f"{class_name}")
    os.makedirs(class_dir)

    for user_id in user_attempts:
        user_dir = os.path.join(class_dir, user_id)
        os.makedirs(user_dir)

        attempts = user_attempts[user]
        for attempt in attempts:
            with open(os.path.join(user_dir, f"{attempt.title}.json"), "w") as f:
                f.write(attempt.chat)

    base_name = os.path.join(tmp, f"{class_name}-export")
    out_file = shutil.make_archive(base_name, "zip", class_dir)
    bg_tasks.add_task(cleanup, tmp)

    headers = {'Access-Control-Expose-Headers': 'Content-Disposition'}

    return FileResponse(out_file, filename=f"{class_name}-export.zip", background=bg_tasks, headers=headers)
