import os
import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from backend.language.parser import MissionParseError, parse_command
from backend.language.schemas import Mission
from backend.speech.asr import transcribe_audio

# -------------------------
# Mission 路线
# -------------------------
router = APIRouter(
    prefix="/missions",
    tags=["missions"],
)

class ParseMissionRequest(BaseModel):
    command: str = Field(
        min_length=1,
        max_length=1000,
    )

@router.post("/parse", response_model=Mission)
def parse_mission(request: ParseMissionRequest) -> Mission:
    command = request.command.strip()

    if not command:
        raise HTTPException(
            status_code=422,
            detail="Command cannot be empty."
        )

    try:
        return parse_command(command)

    except MissionParseError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

# -------------------------
# 语音路线
# -------------------------

speech_router = APIRouter(
    prefix="/speech",
    tags=["speech"],
)

class TranscriptionResponse(BaseModel):
    text: str

@speech_router.post("/transcribe", 
    response_model=TranscriptionResponse,
)
def transcribe_speech(audio: UploadFile = File(...)) -> TranscriptionResponse:
    if (audio.content_type and not audio.content_type.startswith("audio/")):
        raise HTTPException(
            status_code=415,
            detail="uploaded file must be audio.",
        )
    suffix = Path(audio.filename or "").suffix or ".webm"

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix,) as temp_file:
            shutil.copyfileobj(audio.file,temp_file,)

            temp_path = temp_file.name

        text = transcribe_audio(temp_path)

        if not text:
            raise HTTPException(
                status_code=422,
                detail="No speech was detected.",
            )

        return TranscriptionResponse(text=text)

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Audio transcription failed: "
                f"{exc}"
            ),
        ) from exc
    
    finally:
        audio.file.close()
        if (temp_path and os.path.exists(temp_path)):
            os.remove(temp_path)
        