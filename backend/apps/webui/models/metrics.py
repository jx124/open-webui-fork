from pydantic import BaseModel
from typing import List, Optional, Dict
import peewee as pw
from playhouse.shortcuts import model_to_dict

import datetime

from apps.webui.internal.db import DB
from apps.webui.models.chats import Chat
from apps.webui.models.prompts_classes import Class

import logging
from config import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])


####################
# Metric DB Schema
####################


class Metric(pw.Model):
    id = pw.AutoField()
    user_id = pw.CharField()
    chat_id = pw.CharField()  # Not using foreign key since we want to save metric even when chat is deleted
    model_id = pw.TextField()  # Using TextField for consistency
    date = pw.DateField()

    input_tokens = pw.BigIntegerField(default=0)
    output_tokens = pw.BigIntegerField(default=0)
    message_count = pw.BigIntegerField(default=0)

    class Meta:
        database = DB


class MetricModel(BaseModel):
    id: int
    user_id: str
    chat_id: str
    selected_model_id: str  # prevent namespace collision
    date: datetime.date

    input_tokens: int = 0
    output_tokens: int = 0
    message_count: int = 0


class ChatMetricModel(BaseModel):
    chat_id: str

    input_tokens: int = 0
    output_tokens: int = 0
    message_count: int = 0


####################
# Forms
####################


class MetricForm(BaseModel):
    user_id: str
    chat_id: str

    selected_model_id: str  # prevent namespace collision
    input_tokens: int = 0
    output_tokens: int = 0
    message_count: int = 0


def metric_to_metricmodel(metric: Metric) -> MetricModel:
    metric_dict = model_to_dict(metric)
    model_id = metric_dict.get("model_id")

    return MetricModel(**metric_dict, selected_model_id=model_id)


class MetricsTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([Metric])

    def get_metrics(self) -> List[MetricModel]:
        try:
            query = Metric.select()
            return [metric_to_metricmodel(metric) for metric in query]

        except Exception:
            log.exception(" Exception caught in model method.")
            return []

    def get_metrics_by_chats(self, instructor_id: str) -> Dict[str, ChatMetricModel]:
        try:
            query = Metric.select(Metric.chat_id,
                                  pw.fn.SUM(Metric.input_tokens).alias("input_tokens"),
                                  pw.fn.SUM(Metric.output_tokens).alias("output_tokens"),
                                  pw.fn.SUM(Metric.message_count).alias("message_count"))\
                .group_by(Metric.chat_id)

            results = {}
            for result in query:
                results[result.chat_id] = ChatMetricModel(chat_id=result.chat_id,
                                                          input_tokens=result.input_tokens,
                                                          output_tokens=result.output_tokens,
                                                          message_count=result.message_count)
            return results

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_metrics_by_chats_and_instructor_id(self, instructor_id: str) -> Dict[str, ChatMetricModel]:
        try:
            query = Metric.select(Metric.chat_id,
                                  pw.fn.SUM(Metric.input_tokens).alias("input_tokens"),
                                  pw.fn.SUM(Metric.output_tokens).alias("output_tokens"),
                                  pw.fn.SUM(Metric.message_count).alias("message_count"))\
                .join(Chat, on=(Metric.chat_id == Chat.id))\
                .join(Class, pw.JOIN.LEFT_OUTER, on=(Chat.class_id == Class.id))\
                .where((Class.instructor == instructor_id) | (Class.id.is_null() & (Chat.user_id == instructor_id)))\
                .group_by(Metric.chat_id)

            results = {}
            for result in query:
                results[result.chat_id] = ChatMetricModel(chat_id=result.chat_id,
                                                          input_tokens=result.input_tokens,
                                                          output_tokens=result.output_tokens,
                                                          message_count=result.message_count)
            return results

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def get_metrics_by_chat_id(self, chat_id) -> Optional[ChatMetricModel]:
        try:
            result = Metric.select(Metric.chat_id,
                                   pw.fn.SUM(Metric.input_tokens).alias("input_tokens"),
                                   pw.fn.SUM(Metric.output_tokens).alias("output_tokens"),
                                   pw.fn.SUM(Metric.message_count).alias("message_count"))\
                .where(Metric.chat_id == chat_id)\
                .group_by(Metric.chat_id).get()

            print("get_metrics_by_chat_id", model_to_dict(result))

            return ChatMetricModel(chat_id=chat_id,
                                   input_tokens=result.input_tokens,
                                   output_tokens=result.output_tokens,
                                   message_count=result.message_count)

        except Exception:
            log.exception(" Exception caught in model method.")
            return None

    def update_metric_entry(self, form: MetricForm) -> Optional[bool]:
        try:
            result, _ = Metric.get_or_create(user_id=form.user_id,
                                             chat_id=form.chat_id,
                                             model_id=form.selected_model_id,
                                             date=datetime.date.today())
            if result:
                query = Metric.update(input_tokens=Metric.input_tokens + form.input_tokens,
                                      output_tokens=Metric.output_tokens + form.output_tokens,
                                      message_count=Metric.message_count + form.message_count
                                      ).where(Metric.id == result.id)
                query.execute()
                return True
            else:
                return None

        except Exception:
            log.exception(" Exception caught in model method.")
            return None


Metrics = MetricsTable(DB)
