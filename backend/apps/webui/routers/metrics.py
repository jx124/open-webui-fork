from fastapi import Depends
from typing import List, Optional, Dict

from fastapi import APIRouter

from apps.webui.models.metrics import Metrics, MetricModel, ChatMetricModel
from apps.webui.models.users import UserModel

from utils.utils import get_admin_user, get_admin_or_instructor

router = APIRouter()

############################
# GetRoles
############################


@router.get("/", response_model=List[MetricModel])
async def get_metrics(user: UserModel = Depends(get_admin_user)) -> List[MetricModel]:
    result: List[MetricModel] = Metrics.get_metrics()
    return result


@router.get("/chats", response_model=Dict[str, ChatMetricModel])
async def get_metrics_by_chats(user: UserModel = Depends(get_admin_or_instructor)) -> Dict[str, ChatMetricModel]:
    result: Dict[str, ChatMetricModel]

    if user.role == "admin":
        result = Metrics.get_metrics_by_chats(user.id)
    elif user.role == "instructor":
        result = Metrics.get_metrics_by_chats_and_instructor_id(user.id)

    return result


@router.get("/{chat_id}", response_model=Optional[ChatMetricModel])
async def get_metrics_by_chat_id(chat_id: str, user: UserModel = Depends(get_admin_or_instructor)) -> Optional[ChatMetricModel]:
    result: Optional[ChatMetricModel] = Metrics.get_metrics_by_chat_id(chat_id)
    return result
