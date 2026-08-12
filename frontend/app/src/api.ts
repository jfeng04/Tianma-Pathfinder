import type { Mission } from "./types";


const API_BASE_URL = "http://127.0.0.1:8000";


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