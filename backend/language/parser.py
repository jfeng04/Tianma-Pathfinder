from pydantic import ValidationError

from llm_client import request_mission_json
from schemas import Mission

class MissionParseError(Exception):
    pass

def parse_command(command: str) -> Mission:
    """
    JSON -> Mission 对象
    若有报错，直接呼叫 MissionParseError
    """
    raw_json = request_mission_json(command)

    try:
        mission = Mission.model_validate_json(raw_json)
    except ValidationError as exc:
        raise MissionParseError(
            f"The LLM produced an invalid mission:\n{raw_json}"
        ) from exc

    return mission