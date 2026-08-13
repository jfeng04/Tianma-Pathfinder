from functools import lru_cache
from pathlib import Path
import subprocess

import numpy as np
from transformers import pipeline


MODEL_NAME = "openai/whisper-small"
SAMPLE_RATE = 16000


@lru_cache(maxsize=1)
def get_transcriber():
    """
    一次性读取 ASR 模型，之后重复使用。
    """
    return pipeline(
        task="automatic-speech-recognition",
        model=MODEL_NAME,
    )


def decode_audio(audio_path: Path) -> np.ndarray:
    """
    使用 FFmpeg 将不同格式的音频统一转换为：
    - mono
    - 16 kHz
    - float32 waveform
    """

    command = [
        "ffmpeg",
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",

        "-i",
        str(audio_path),

        "-ac",
        "1",

        "-ar",
        str(SAMPLE_RATE),

        "-f",
        "f32le",

        "pipe:1",
    ]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    except FileNotFoundError as exc:
        raise RuntimeError(
            "FFmpeg is not installed or is not available on PATH."
        ) from exc

    except subprocess.CalledProcessError as exc:
        error_message = exc.stderr.decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"FFmpeg could not decode the audio:\n{error_message}"
        ) from exc

    audio_array = np.frombuffer(
        result.stdout,
        dtype=np.float32,
    ).copy()

    if audio_array.size == 0:
        raise ValueError(
            "Decoded audio contains no samples."
        )

    return audio_array


def transcribe_audio(audio_path: str) -> str:
    """
    语音转文字。
    """

    path = Path(audio_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Audio not found: {path}"
        )

    audio_array = decode_audio(path)

    transcriber = get_transcriber()

    result = transcriber(
        {
            "raw": audio_array,
            "sampling_rate": SAMPLE_RATE,
        }
    )

    return result["text"].strip()


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    samples_dir = base_dir / "samples"

    for audio_file in samples_dir.glob("*"):
        if (
            audio_file.is_file()
            and not audio_file.name.startswith(".")
        ):
            print(
                f"\nProcessing: {audio_file.name}"
            )

            text = transcribe_audio(
                str(audio_file)
            )

            print(
                f"Transcript: {text}"
            )