from pathlib import Path
import librosa
from transformers import pipeline

def transcribe_audio(audio_path: str) -> str:
    path = Path(audio_path)

    # 如果此路径不存在
    if not path.exists():
        raise FileNotFoundError(f"Audio not found: {path}")

    # librosa 架构会直接处理 w4a 文件
    audio_array, sampling_rate = librosa.load(str(path), sr=16000)

    # 语音转文字的管道
    transcriber = pipeline(
        task="automatic-speech-recognition",
        model="openai/whisper-small"
    )

    # 使用管道取出文本
    result = transcriber({"raw": audio_array, "sampling_rate": sampling_rate})
    return result["text"].strip()

if __name__ == "__main__":
    # 召唤 transcribe_audio 函数以返回转换后的文本
    BASE_DIR = Path(__file__).resolve().parent
    samples_dir = BASE_DIR / "samples"

    for audio_file in samples_dir.glob("*.m4a"):
        if audio_file.is_file() and not audio_file.name.startswith("."):
            print(f"\nProcessing: {audio_file.name}")
            text = transcribe_audio(audio_file)
            print(f"Transcript: {text}")