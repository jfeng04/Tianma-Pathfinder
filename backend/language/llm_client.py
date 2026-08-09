import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

MODEL = os.getenv("OPENAI_MODEL")

SYSTEM_PROMPT = """
You convert natural-language rover commands into JSON.

Return JSON only. Do not include Markdown or explanations.
Use only the exact enum strings listed below. Never create synonyms.

Allowed actions:
- navigate
- inspect
- stop
- return_to_start

Allowed object types:
- cylinder
- box
- gate

Allowed colors:
- red
- blue
- green
- yellow

Allowed spatial hints:
- nearest
- farthest
- far_end
- left
- right

Allowed constraints:
- avoid_obstacles
- remain_in_course
- do_not_enter_restricted_zone

Map phrases such as:
- "do not enter the restricted zone"
- "avoid the restricted area"
- "stay outside the restricted zone"

to exactly:
"do_not_enter_restricted_zone"

Required JSON format:

{
  "action": "navigate",
  "target": {
    "object_type": "cylinder",
    "color": "red",
    "spatial_hint": "far_end"
  },
  "stop_distance_m": 1.5,
  "constraints": [
    "avoid_obstacles",
    "do_not_enter_restricted_zone"
  ]
}

For stop and return_to_start commands, target must be null. If the user does not specify a stopping distance, omit stop_distance_m.
Never return null for stop_distance_m.
"""

def request_mission_json(command: str) -> str:
    """
    向大语言模型发出自然语言命令

    返回：
        模型生成的纯 JSON 字串
    """

    if not command.strip():
        raise ValueError("Command cannot be empty.")

    response = client.responses.create(
        model=MODEL,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": command,
            },
        ],
    )

    return response.output_text.strip()