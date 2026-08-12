from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.language.parser import MissionParseError, parse_command
from backend.language.schemas import Mission

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