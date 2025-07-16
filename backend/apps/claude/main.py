from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse

import requests
import aiohttp
import asyncio
import json
import logging

from pydantic import BaseModel
from starlette.background import BackgroundTask

from apps.webui.models.models import Models
from apps.webui.models.users import Users
from apps.webui.models.metrics import Metrics, MetricForm
from apps.webui.models.prompts_classes import Prompts
from apps.webui.models.evaluations import Evaluations
from constants import ERROR_MESSAGES
from utils.utils import (
    get_current_user,
    get_verified_user,
    get_admin_user,
)
from config import (
    SRC_LOG_LEVELS,
    ENABLE_CLAUDE_API,
    CLAUDE_API_BASE_URLS,
    CLAUDE_API_KEYS,
    CACHE_DIR,
    ENABLE_MODEL_FILTER,
    MODEL_FILTER_LIST,
    AppConfig,
)
from typing import List, Optional

import iso8601

import hashlib
from pathlib import Path

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["CLAUDE"])

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.state.config = AppConfig()

app.state.config.ENABLE_MODEL_FILTER = ENABLE_MODEL_FILTER
app.state.config.MODEL_FILTER_LIST = MODEL_FILTER_LIST

app.state.config.ENABLE_CLAUDE_API = ENABLE_CLAUDE_API
app.state.config.CLAUDE_API_BASE_URLS = CLAUDE_API_BASE_URLS
app.state.config.CLAUDE_API_KEYS = CLAUDE_API_KEYS

app.state.MODELS = {}


@app.middleware("http")
async def check_url(request: Request, call_next):
    if len(app.state.MODELS) == 0:
        await get_all_models()
    else:
        pass

    response = await call_next(request)
    return response


@app.get("/config")
async def get_config(user=Depends(get_admin_user)):
    return {"ENABLE_CLAUDE_API": app.state.config.ENABLE_CLAUDE_API}


class ClaudeConfigForm(BaseModel):
    enable_claude_api: Optional[bool] = None


@app.post("/config/update")
async def update_config(form_data: ClaudeConfigForm, user=Depends(get_admin_user)):
    app.state.config.ENABLE_CLAUDE_API = form_data.enable_claude_api
    return {"ENABLE_CLAUDE_API": app.state.config.ENABLE_CLAUDE_API}


class UrlsUpdateForm(BaseModel):
    urls: List[str]


class KeysUpdateForm(BaseModel):
    keys: List[str]


@app.get("/urls")
async def get_claude_urls(user=Depends(get_admin_user)):
    return {"CLAUDE_API_BASE_URLS": app.state.config.CLAUDE_API_BASE_URLS}


@app.post("/urls/update")
async def update_claude_urls(form_data: UrlsUpdateForm, user=Depends(get_admin_user)):
    await get_all_models()
    app.state.config.CLAUDE_API_BASE_URLS = form_data.urls
    return {"CLAUDE_API_BASE_URLS": app.state.config.CLAUDE_API_BASE_URLS}


@app.get("/keys")
async def get_claude_keys(user=Depends(get_admin_user)):
    return {"CLAUDE_API_KEYS": app.state.config.CLAUDE_API_KEYS}


@app.post("/keys/update")
async def update_claude_key(form_data: KeysUpdateForm, user=Depends(get_admin_user)):
    app.state.config.CLAUDE_API_KEYS = form_data.keys
    return {"CLAUDE_API_KEYS": app.state.config.CLAUDE_API_KEYS}


# TODO: implement
@app.post("/audio/speech")
async def speech(request: Request, user=Depends(get_verified_user)):
    raise HTTPException(
        status_code=500, detail="Not Implemented"
    )
    idx = None
    try:
        idx = app.state.config.CLAUDE_API_BASE_URLS.index("https://api.anthropic.com/v1")
        body = await request.body()
        name = hashlib.sha256(body).hexdigest()

        SPEECH_CACHE_DIR = Path(CACHE_DIR).joinpath("./audio/speech/")
        SPEECH_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        file_path = SPEECH_CACHE_DIR.joinpath(f"{name}.mp3")
        file_body_path = SPEECH_CACHE_DIR.joinpath(f"{name}.json")

        # Check if the file already exists in the cache
        if file_path.is_file():
            return FileResponse(file_path)

        headers = {}
        headers["Authorization"] = f"Bearer {app.state.config.CLAUDE_API_KEYS[idx]}"
        headers["Content-Type"] = "application/json"
        if "openrouter.ai" in app.state.config.CLAUDE_API_BASE_URLS[idx]:
            headers["HTTP-Referer"] = "https://openwebui.com/"
            headers["X-Title"] = "Open WebUI"
        r = None
        try:
            r = requests.post(
                url=f"{app.state.config.CLAUDE_API_BASE_URLS[idx]}/audio/speech",
                data=body,
                headers=headers,
                stream=True,
            )

            r.raise_for_status()

            # Save the streaming content to a file
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            with open(file_body_path, "w") as f:
                json.dump(json.loads(body.decode("utf-8")), f)

            # Return the saved file
            return FileResponse(file_path)

        except Exception as e:
            log.exception(e)
            error_detail = "Open WebUI: Server Connection Error"
            if r is not None:
                try:
                    res = r.json()
                    if "error" in res:
                        error_detail = f"External: {res['error']}"
                except:
                    error_detail = f"External: {e}"

            raise HTTPException(
                status_code=r.status_code if r else 500, detail=error_detail
            )

    except ValueError:
        raise HTTPException(status_code=401, detail=ERROR_MESSAGES.CLAUDE_NOT_FOUND)


async def fetch_url(url, key):
    timeout = aiohttp.ClientTimeout(total=5)
    try:
        headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                return await response.json()
    except Exception as e:
        # Handle connection error here
        log.error(f"Connection error: {e}")
        return None


async def cleanup_response(
    response: Optional[aiohttp.ClientResponse],
    session: Optional[aiohttp.ClientSession],
):
    if response:
        response.close()
    if session:
        await session.close()


def rfc3339_to_unix(rfc3339_string):
    date = iso8601.parse_date(rfc3339_string)
    return int(date.timestamp())


def merge_models_lists(model_lists):
    log.debug(f"merge_models_lists {model_lists}")
    merged_list = []

    for idx, models in enumerate(model_lists):
        if models is not None and "error" not in models:
            merged_list.extend(
                [
                    {
                        "id": model["id"],
                        "object": model.get("type", "model"),
                        "created": rfc3339_to_unix(model.get("created_at", "2025-02-19T00:00:00Z")),
                        "name": model.get("display_name", model["id"]),
                        "owned_by": "anthropic",
                        "anthropic": model,
                        "urlIdx": idx,
                    }
                    for model in models
                    if "api.anthropic.com"
                    not in app.state.config.CLAUDE_API_BASE_URLS[idx]
                    or "claude" in model["id"]
                ]
            )

    return merged_list


async def get_all_models(raw: bool = False):
    log.info("get_all_models()")

    if (
        len(app.state.config.CLAUDE_API_KEYS) == 1
        and app.state.config.CLAUDE_API_KEYS[0] == ""
    ) or not app.state.config.ENABLE_CLAUDE_API:
        models = {"data": []}
    else:
        # Check if API KEYS length is same than API URLS length
        if len(app.state.config.CLAUDE_API_KEYS) != len(
            app.state.config.CLAUDE_API_BASE_URLS
        ):
            # if there are more keys than urls, remove the extra keys
            if len(app.state.config.CLAUDE_API_KEYS) > len(
                app.state.config.CLAUDE_API_BASE_URLS
            ):
                app.state.config.CLAUDE_API_KEYS = app.state.config.CLAUDE_API_KEYS[
                    : len(app.state.config.CLAUDE_API_BASE_URLS)
                ]
            # if there are more urls than keys, add empty keys
            else:
                app.state.config.CLAUDE_API_KEYS += [
                    ""
                    for _ in range(
                        len(app.state.config.CLAUDE_API_BASE_URLS)
                        - len(app.state.config.CLAUDE_API_KEYS)
                    )
                ]

        tasks = [
            fetch_url(f"{url}/models", app.state.config.CLAUDE_API_KEYS[idx])
            for idx, url in enumerate(app.state.config.CLAUDE_API_BASE_URLS)
        ]

        responses = await asyncio.gather(*tasks)
        log.debug(f"get_all_models:responses() {responses}")

        if raw:
            return responses

        models = {
            "data": merge_models_lists(
                list(
                    map(
                        lambda response: (
                            response["data"]
                            if (response and "data" in response)
                            else (response if isinstance(response, list) else None)
                        ),
                        responses,
                    )
                )
            )
        }

        log.debug(f"models: {models}")
        app.state.MODELS = {model["id"]: model for model in models["data"]}

    return models


# TODO: implement
@app.get("/models")
@app.get("/models/{url_idx}")
async def get_models(url_idx: Optional[int] = None, user=Depends(get_current_user)):
    raise HTTPException(
        status_code=500, detail="Not Implemented"
    )
    if url_idx is None:
        models = await get_all_models()
        if app.state.config.ENABLE_MODEL_FILTER:
            if user.role != "admin":
                models["data"] = list(
                    filter(
                        lambda model: model["id"] in app.state.config.MODEL_FILTER_LIST,
                        models["data"],
                    )
                )
                return models
        return models
    else:
        url = app.state.config.CLAUDE_API_BASE_URLS[url_idx]
        key = app.state.config.CLAUDE_API_KEYS[url_idx]

        headers = {}
        headers["Authorization"] = f"Bearer {key}"
        headers["Content-Type"] = "application/json"

        r = None

        try:
            r = requests.request(method="GET", url=f"{url}/models", headers=headers)
            r.raise_for_status()

            response_data = r.json()
            if "api.anthropic.com" in url:
                response_data["data"] = list(
                    filter(lambda model: "claude" in model["id"], response_data["data"])
                )

            return response_data
        except Exception as e:
            log.exception(e)
            error_detail = "Open WebUI: Server Connection Error"
            if r is not None:
                try:
                    res = r.json()
                    if "error" in res:
                        error_detail = f"External: {res['error']}"
                except:
                    error_detail = f"External: {e}"

            raise HTTPException(
                status_code=r.status_code if r else 500,
                detail=error_detail,
            )


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(path: str, request: Request, user=Depends(get_verified_user)):
    idx = 0

    body = await request.body()

    payload = None
    model_str = ""
    chat_id = ""
    is_eval = False

    try:
        if "chat/completions" in path:
            body = body.decode("utf-8")
            body = json.loads(body)

            payload = {**body}
            model_id: str

            if "model" in payload:
                model_str = payload["model"]
            if "chat_id" in payload:
                chat_id = payload["chat_id"]
                del payload["chat_id"]

            # Replace prompt command with prompt content so end users cannot see prompt
            if "profile_id" in payload:
                profile_id = payload["profile_id"]
                content = Prompts.get_prompt_content_by_id(profile_id)
                model_id = Prompts.get_prompt_selected_model_by_id(profile_id)
                payload["system"] = content

                del payload["profile_id"]

            # Replace evaluation id with evaluation content so end users cannot see prompt
            if "evaluation_id" in payload:
                profile_id = payload["evaluation_id"]
                evaluation = Evaluations.get_evaluation_by_id(profile_id)
                content = evaluation.content
                model_id = evaluation.selected_model_id
                payload["model"] = evaluation.selected_model_id
                payload["system"] = content

                is_eval = True
                del payload["evaluation_id"]

            model_info = Models.get_model_by_id(model_id)

            if model_info:
                print(model_info)
                if model_info.base_model_id:
                    payload["model"] = model_info.base_model_id
                    model_str = model_info.base_model_id

                model_info.params = model_info.params.model_dump()

                if model_info.params:
                    if model_info.params.get("temperature", None):
                        payload["temperature"] = int(
                            model_info.params.get("temperature")
                        )

                    if model_info.params.get("top_p", None):
                        payload["top_p"] = int(model_info.params.get("top_p", None))

                    if model_info.params.get("max_tokens", None):
                        payload["max_tokens"] = int(
                            model_info.params.get("max_tokens", None)
                        )

                    # if model_info.params.get("frequency_penalty", None):
                    #     payload["frequency_penalty"] = int(
                    #         model_info.params.get("frequency_penalty", None)
                    #     )

                    # if model_info.params.get("seed", None):
                    #     payload["seed"] = model_info.params.get("seed", None)

                    if model_info.params.get("stop", None):
                        payload["stop_sequences"] = (
                            [
                                bytes(stop, "utf-8").decode("unicode_escape")
                                for stop in model_info.params["stop"]
                            ]
                            if model_info.params.get("stop", None)
                            else None
                        )

            else:
                pass

            model = app.state.MODELS[payload.get("model")]

            idx = model["urlIdx"]

            if "pipeline" in model and model.get("pipeline"):
                payload["user"] = {"name": user.name, "id": user.id}

            # claude requires a max_token field
            if payload.get("max_tokens", None) is None:
                payload["max_tokens"] = 1024

            # Convert the modified body back to JSON
            payload = json.dumps(payload)

    except json.JSONDecodeError as e:
        log.error("Error loading request body into a dictionary:", e)

    url = app.state.config.CLAUDE_API_BASE_URLS[idx]
    key = app.state.config.CLAUDE_API_KEYS[idx]

    target_url = f"{url}/messages"

    headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
    headers["Content-Type"] = "application/json"

    r = None
    session = None
    streaming = False

    try:
        session = aiohttp.ClientSession()
        r = await session.request(
            method=request.method,
            url=target_url,
            data=payload if payload else body,
            headers=headers,
        )

        r.raise_for_status()

        # Check if response is SSE
        if "text/event-stream" in r.headers.get("Content-Type", ""):
            streaming = True
            return StreamingResponse(
                stream_token_counter(r.content, user.id, chat_id, model_str, is_eval),
                status_code=r.status,
                headers=dict(r.headers),
                background=BackgroundTask(
                    cleanup_response, response=r, session=session
                ),
            )
        else:
            response_data = await r.json()

            if response_data is not None and response_data.get("usage"):
                input_tokens = response_data["usage"]["input_tokens"]
                output_tokens = response_data["usage"]["output_tokens"]
                Metrics.update_metric_entry(
                        MetricForm(user_id=user.id,
                                   chat_id=chat_id,
                                   selected_model_id=model_str,
                                   input_tokens=input_tokens,
                                   output_tokens=output_tokens,
                                   message_count=1 if not is_eval else 0))
                Users.increment_user_token_count_by_id(user.id, input_tokens + output_tokens)

            return response_data
    except Exception as e:
        log.exception(e)
        error_detail = "Open WebUI: Server Connection Error"
        if r is not None:
            try:
                res = await r.json()
                if "error" in res:
                    error_detail = f"External: {res['error']['message'] if 'message' in res['error'] else res['error']}"
            except:
                error_detail = f"External: {e}"
        raise HTTPException(status_code=r.status if r else 500, detail=error_detail)
    finally:
        if not streaming and session:
            if r:
                r.close()
            await session.close()


async def stream_token_counter(stream, user_id, chat_id, model_id, is_eval):
    # reads stream and increments token count if usage found in stream
    async for line in stream:
        try:
            result = None
            if line.startswith(b"data: "):
                result = json.loads(line[6:])  # strip "data: " at the front of response

            if result is not None:
                if result.get("message") is not None:
                    input_tokens = result["message"]["usage"]["input_tokens"]
                    Metrics.update_metric_entry(
                            MetricForm(user_id=user_id,
                                       chat_id=chat_id,
                                       selected_model_id=model_id,
                                       input_tokens=input_tokens,
                                       output_tokens=0,
                                       message_count=1 if not is_eval else 0))
                    Users.increment_user_token_count_by_id(user_id, input_tokens)
                elif result.get("usage") is not None:
                    output_tokens = result["usage"]["output_tokens"]
                    Metrics.update_metric_entry(
                            MetricForm(user_id=user_id,
                                       chat_id=chat_id,
                                       selected_model_id=model_id,
                                       input_tokens=0,
                                       output_tokens=output_tokens,
                                       message_count=0))
                    Users.increment_user_token_count_by_id(user_id, output_tokens)

        except json.decoder.JSONDecodeError:
            pass
        finally:
            yield line

