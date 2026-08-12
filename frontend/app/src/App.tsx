import { useState, type FormEvent } from "react";

import { parseMission } from "./api";
import type { Mission } from "./types";

import "./App.css";


function App() {
  const [command, setCommand] = useState("");

  const [mission, setMission] =
    useState<Mission | null>(null);

  const [error, setError] =
    useState<string | null>(null);

  const [loading, setLoading] =
    useState(false);


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    const trimmedCommand = command.trim();

    if (!trimmedCommand) {
      return;
    }

    setLoading(true);
    setError(null);
    setMission(null);

    try {
      const result = await parseMission(
        trimmedCommand
      );

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

          <button
            type="submit"
            disabled={
              loading || !command.trim()
            }
          >
            {loading
              ? "Parsing..."
              : "Parse Mission"}
          </button>
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