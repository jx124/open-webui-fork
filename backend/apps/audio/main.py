import os
import aiohttp
import logging
from fastapi import (
    FastAPI,
    Request,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
)

from fastapi.responses import StreamingResponse, JSONResponse, FileResponse

from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
from pydantic import BaseModel


import requests
import hashlib
from pathlib import Path
import json


from constants import ERROR_MESSAGES
from utils.utils import (
    decode_token,
    get_current_user,
    get_verified_user,
    get_admin_user,
)
from utils.misc import calculate_sha256

from config import (
    SRC_LOG_LEVELS,
    CACHE_DIR,
    UPLOAD_DIR,
    WHISPER_MODEL,
    WHISPER_MODEL_DIR,
    WHISPER_MODEL_AUTO_UPDATE,
    DEVICE_TYPE,
    AUDIO_OPENAI_API_BASE_URL,
    AUDIO_OPENAI_API_KEY,
    AUDIO_OPENAI_API_MODEL,
    AUDIO_OPENAI_API_VOICE,
    ELEVENLABS_API_KEY,
    ELEVENLABS_API_BASE_URL,
    AppConfig,
)

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["AUDIO"])

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.config = AppConfig()
app.state.config.OPENAI_API_BASE_URL = AUDIO_OPENAI_API_BASE_URL
app.state.config.OPENAI_API_KEY = AUDIO_OPENAI_API_KEY
app.state.config.OPENAI_API_MODEL = AUDIO_OPENAI_API_MODEL
app.state.config.OPENAI_API_VOICE = AUDIO_OPENAI_API_VOICE

# setting device type for whisper model
whisper_device_type = DEVICE_TYPE if DEVICE_TYPE and DEVICE_TYPE == "cuda" else "cpu"
log.info(f"whisper_device_type: {whisper_device_type}")

SPEECH_CACHE_DIR = Path(CACHE_DIR).joinpath("./audio/speech/")
SPEECH_CACHE_DIR.mkdir(parents=True, exist_ok=True)


class OpenAIConfigUpdateForm(BaseModel):
    url: str
    key: str
    model: str
    speaker: str


@app.get("/config")
async def get_openai_config(user=Depends(get_admin_user)):
    return {
        "OPENAI_API_BASE_URL": app.state.config.OPENAI_API_BASE_URL,
        "OPENAI_API_KEY": app.state.config.OPENAI_API_KEY,
        "OPENAI_API_MODEL": app.state.config.OPENAI_API_MODEL,
        "OPENAI_API_VOICE": app.state.config.OPENAI_API_VOICE,
    }


@app.get("/voices")
async def get_audio_voices(user=Depends(get_admin_user)):
    # get elevenlabs audio voices. TODO: add other services.
    timeout = aiohttp.ClientTimeout(total=5)
    try:
        headers = {"xi-api-key": ELEVENLABS_API_KEY}
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"{ELEVENLABS_API_BASE_URL}/v2/voices?page_size=100", headers=headers) as response:
                return await response.json()
    except Exception as e:
        # Handle connection error here
        log.error(f"Connection error: {e}")
        return None


@app.get("/models")
async def get_audio_models(user=Depends(get_admin_user)):
    # get elevenlabs audio models. TODO: add other services.
    timeout = aiohttp.ClientTimeout(total=5)
    try:
        headers = {"xi-api-key": ELEVENLABS_API_KEY}
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"{ELEVENLABS_API_BASE_URL}/v1/models", headers=headers) as response:
                return await response.json()
    except Exception as e:
        # Handle connection error here
        log.error(f"Connection error: {e}")
        return None


@app.post("/config/update")
async def update_openai_config(
    form_data: OpenAIConfigUpdateForm, user=Depends(get_admin_user)
):
    if form_data.key == "":
        raise HTTPException(status_code=400, detail=ERROR_MESSAGES.API_KEY_NOT_FOUND)

    app.state.config.OPENAI_API_BASE_URL = form_data.url
    app.state.config.OPENAI_API_KEY = form_data.key
    app.state.config.OPENAI_API_MODEL = form_data.model
    app.state.config.OPENAI_API_VOICE = form_data.speaker

    return {
        "status": True,
        "OPENAI_API_BASE_URL": app.state.config.OPENAI_API_BASE_URL,
        "OPENAI_API_KEY": app.state.config.OPENAI_API_KEY,
        "OPENAI_API_MODEL": app.state.config.OPENAI_API_MODEL,
        "OPENAI_API_VOICE": app.state.config.OPENAI_API_VOICE,
    }


@app.post("/speech/openai")
async def openai_speech(request: Request, user=Depends(get_verified_user)):
    body = await request.body()
    name = hashlib.sha256(body).hexdigest()

    # For now, just save every request to cache. TODO: delete least recently used files to not exceed cache size.
    file_path = SPEECH_CACHE_DIR.joinpath(f"{name}.mp3")
    file_body_path = SPEECH_CACHE_DIR.joinpath(f"{name}.json")

    # Check if the file already exists in the cache
    if file_path.is_file():
        return FileResponse(file_path)

    headers = {}
    headers["Authorization"] = f"Bearer {app.state.config.OPENAI_API_KEY}"
    headers["Content-Type"] = "application/json"

    r = None
    try:
        r = requests.post(
            url=f"{app.state.config.OPENAI_API_BASE_URL}/audio/speech",
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
                    error_detail = f"External: {res['error']['message']}"
            except:
                error_detail = f"External: {e}"

        raise HTTPException(
            status_code=r.status_code if r != None else 500,
            detail=error_detail,
        )


@app.post("/speech/elevenlabs")
async def elevenlabs_speech(request: Request, user=Depends(get_verified_user)):
    body = await request.json()
    name = hashlib.sha256(json.dumps(body).encode()).hexdigest()

    # For now, just save every request to cache. TODO: delete least recently used files to not exceed cache size.
    file_path = SPEECH_CACHE_DIR.joinpath(f"{name}.mp3")
    file_body_path = SPEECH_CACHE_DIR.joinpath(f"{name}.json")

    # Check if the file already exists in the cache
    if file_path.is_file():
        return FileResponse(file_path)

    headers = {}
    headers["xi-api-key"] = ELEVENLABS_API_KEY
    headers["Content-Type"] = "application/json"

    r = None
    try:
        voice_id = body['voice_id']
        del body['voice_id']

        r = requests.post(
            url=f"{ELEVENLABS_API_BASE_URL}/v1/text-to-speech/{voice_id}/stream?output_format=mp3_22050_32",
            data=json.dumps(body).encode(),
            headers=headers,
        )

        r.raise_for_status()

        # Save the streaming content to a file
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        body['voice_id'] = voice_id
        with open(file_body_path, "w") as f:
            json.dump(body, f)

        # Return the saved file
        return FileResponse(file_path)

    except Exception as e:
        log.exception(e)
        error_detail = "Open WebUI: Server Connection Error"
        if r is not None:
            try:
                res = r.json()
                if "error" in res:
                    error_detail = f"External: {res['error']['message']}"
            except:
                error_detail = f"External: {e}"

        raise HTTPException(
            status_code=r.status_code if r != None else 500,
            detail=error_detail,
        )


@app.post("/transcription/whisper")
def transcribe_whisper(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    log.info(f"file.content_type: {file.content_type}")

    if file.content_type not in ["audio/mpeg", "audio/wav"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.FILE_NOT_SUPPORTED,
        )

    try:
        filename = file.filename
        file_path = f"{UPLOAD_DIR}/{filename}"
        contents = file.file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
            f.close()

        whisper_kwargs = {
            "model_size_or_path": WHISPER_MODEL,
            "device": whisper_device_type,
            "compute_type": "int8",
            "download_root": WHISPER_MODEL_DIR,
            "local_files_only": not WHISPER_MODEL_AUTO_UPDATE,
        }

        log.debug(f"whisper_kwargs: {whisper_kwargs}")

        try:
            model = WhisperModel(**whisper_kwargs)
        except:
            log.warning(
                "WhisperModel initialization failed, attempting download with local_files_only=False"
            )
            whisper_kwargs["local_files_only"] = False
            model = WhisperModel(**whisper_kwargs)

        segments, info = model.transcribe(file_path, beam_size=5)
        log.info(
            "Whisper speech-to-text: detected language '%s' with probability %f"
            % (info.language, info.language_probability)
        )

        transcript = "".join([segment.text for segment in list(segments)])
        log.info(f"Whisper speech-to-text: {transcript.strip()}")

        return {"text": transcript.strip()}

    except Exception as e:
        log.exception(e)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(e),
        )


@app.post("/transcription/elevenlabs")
def transcribe_elevenlabs(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    if file.content_type not in ["audio/mpeg", "audio/wav"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.FILE_NOT_SUPPORTED,
        )

    try:
        filename = file.filename
        contents = file.file.read()

        headers = {}
        headers["xi-api-key"] = ELEVENLABS_API_KEY

        r = requests.post(
            url=f"{ELEVENLABS_API_BASE_URL}/v1/speech-to-text",
            headers=headers,
            data={
                "model_id": "scribe_v1"
            },
            files={
                "file": (filename, contents)
            }
        )

        r.raise_for_status()

        response = r.json()

        log.info(
            "ElevenLabs speech-to-text: detected language '%s' with probability %f"
            % (response['language_code'], response['language_probability'])
        )
        log.info(f"ElevenLabs speech-to-text: {response['text']}")

        return {"text": response['text']}

    except Exception as e:
        log.exception(e)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(e),
        )
