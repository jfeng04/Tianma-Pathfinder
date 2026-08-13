import type { Mission, TranscriptionResponse } from "./types";


const API_BASE_URL = "http://127.0.0.1:8000";

/**
 * 通过 API 路线获取 LLM 的回复
 * @param command 
 * @returns response.json()
 */
export async function parseMission(
  command: string
): Promise<Mission> {

  const response = await fetch(
    `${API_BASE_URL}/api/missions/parse`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        command: command,
      }),
    }
  );


  if (!response.ok) {
    const errorBody = await response
      .json()
      .catch(() => null);

    const message =
      typeof errorBody?.detail === "string"
        ? errorBody.detail
        : `Request failed with status ${response.status}`;

    throw new Error(message);
  }


  return response.json();
}

/**
 * 获取语音的扩展名
 * @param mimeType 
 * @returns String
 */
function getAudioExtension(
  mimeType: string
): string {

  if (mimeType.includes("mp4")) {
    return "m4a";
  }

  if (mimeType.includes("ogg")) {
    return "ogg";
  }

  if (mimeType.includes("wav")) {
    return "wav";
  }

  return "webm";
}

/**
 * 将语音转为文字
 * @param audioBlob 
 * @returns 
 */
export async function transcribeAudio(
  audioBlob: Blob
): Promise<string> {

  const formData = new FormData();

  const extension =
    getAudioExtension(audioBlob.type);

  formData.append(
    "audio",
    audioBlob,
    `command.${extension}`,
  );

  const response = await fetch(
    `${API_BASE_URL}/api/speech/transcribe`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!response.ok) {
    const errorBody = await response
      .json()
      .catch(() => null);

    const message =
      typeof errorBody?.detail === "string"
        ? errorBody.detail
        : `Request failed with status ${response.status}`;

    throw new Error(message);
  }

  const result:
    TranscriptionResponse =
      await response.json();

  return result.text;
}