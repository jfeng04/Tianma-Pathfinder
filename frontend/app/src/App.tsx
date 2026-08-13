import { useRef, useState, type FormEvent } from "react";

import { parseMission, transcribeAudio } from "./api";
import type { Mission } from "./types";

import "./App.css";

/**
 * 构建前端 UI ，组织对象参数并显示在 UI 里
 */
function App() {
  const [command, setCommand] = useState("");

  const [mission, setMission] =
    useState<Mission | null>(null);

  const [error, setError] =
    useState<string | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [isRecording, setIsRecording] =
    useState(false);

  const [isTranscribing, setIsTranscribing] = 
    useState(false);

  const mediaRecorderRef =
    useRef<MediaRecorder | null>(null);

  const mediaStreamRef =
    useRef<MediaStream | null>(null);

  const audioChunksRef =
    useRef<Blob[]>([]);

  /**
   * 将 command 的 state 转借给 runCommand(command) 函数进行处理
   * @param event 
   */
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    await runCommand(command);
  }

  /**
   * 处理键盘输入和语音转文字的请求
   * @param text 
   */
  async function runCommand(text: string) {
    const trimmedCommand = text.trim();

    if (!trimmedCommand) {
      return;
    }

    setLoading(true);
    setError(null);
    setMission(null);

    try {
      const result =
        await parseMission(trimmedCommand);

      setMission(result);

    } catch (err) {

      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Unknown error.");
      }

    } finally {
      setLoading(false);
    }
  }
  /**
   * 清理麦克风流
   */
  function stopMicrophoneStream() {
    mediaStreamRef.current
      ?.getTracks()
      .forEach((track) => {
        track.stop();
      });

    mediaStreamRef.current = null;
  }

  /**
   * 开始录音频
   */
  async function startRecording() {
    setError(null);

    try {
      const stream =
        await navigator.mediaDevices.getUserMedia({
          audio: true,
        });

      mediaStreamRef.current = stream;

      const recorder =
        new MediaRecorder(stream);

      mediaRecorderRef.current = recorder;

      audioChunksRef.current = [];

      recorder.ondataavailable = (
        event: BlobEvent
      ) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(
            event.data
          );
        }
      };

      recorder.onstop = async () => {
        const mimeType =
          recorder.mimeType ||
          audioChunksRef.current[0]?.type ||
          "audio/webm";

        const audioBlob = new Blob(
          audioChunksRef.current,
          {
            type: mimeType,
          }
        );

        stopMicrophoneStream();

        mediaRecorderRef.current = null;

        setIsRecording(false);
        setIsTranscribing(true);

        try {
          const transcript =
            await transcribeAudio(
              audioBlob
            );

          setCommand(transcript);

          setIsTranscribing(false);

          await runCommand(
            transcript
          );

        } catch (err) {

          if (err instanceof Error) {
            setError(err.message);
          } else {
            setError(
              "Voice command failed."
            );
          }

        } finally {
          setIsTranscribing(false);
        }
      };

      recorder.start();

      setIsRecording(true);

    } catch (err) {

      stopMicrophoneStream();

      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(
          "Could not access microphone."
        );
      }
    }
  }

  /**
   * 停止录音频
   */
  function stopRecording() {
    const recorder = mediaRecorderRef.current;

    if (
      recorder &&
      recorder.state !== "inactive"
    ) {
      recorder.stop();
    }
  }

  return (
    <main className="app">
      <header>
        <p className="eyebrow">
          TIANMA / PATHFINDER
        </p>

        <h1>Mission Console</h1>

        <p className="subtitle">
          Natural-language mission interpretation
        </p>
      </header>


      <section className="panel">
        <h2>Command</h2>

        <form onSubmit={handleSubmit}>
          <textarea
            value={command}
            onChange={(event) =>
              setCommand(event.target.value)
            }
            placeholder="Proceed to the red cylinder at the far end and stop two meters away."
            rows={5}
          />

          <div className="button-row">
            <button
              type="submit"
              disabled={
                loading ||
                isRecording ||
                isTranscribing ||
                !command.trim()
              }
            >
              {loading
                ? "Parsing..."
                : "Parse Mission"}
            </button>


            {!isRecording ? (

              <button
                type="button"
                onClick={startRecording}
                disabled={
                  loading ||
                  isTranscribing
                }
              >
                Start Voice Command
              </button>

            ) : (

              <button
                type="button"
                onClick={stopRecording}
              >
                Stop Recording
              </button>

            )}

          </div>

          {isRecording && (
            <p className="status">
              Recording...
            </p>
          )}

          {isTranscribing && (
            <p className="status">
              Transcribing...
            </p>
          )}
        </form>
      </section>


      {error && (
        <section className="panel error">
          <h2>Command Rejected</h2>
          <p>{error}</p>
        </section>
      )}


      {mission && (
        <section className="panel">
          <h2>Validated Mission</h2>

          <div className="mission-grid">
            <span>Action</span>
            <strong>{mission.action}</strong>

            <span>Object</span>
            <strong>
              {mission.target?.object_type ?? "—"}
            </strong>

            <span>Color</span>
            <strong>
              {mission.target?.color ?? "—"}
            </strong>

            <span>Spatial Hint</span>
            <strong>
              {mission.target?.spatial_hint ?? "—"}
            </strong>

            <span>Stop Distance</span>
            <strong>
              {mission.stop_distance_m} m
            </strong>

            <span>Constraints</span>
            <strong>
              {mission.constraints.length > 0
                ? mission.constraints.join(", ")
                : "None"}
            </strong>
          </div>
        </section>
      )}
    </main>
  );
}


export default App;