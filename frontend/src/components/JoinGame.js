import React, { useState } from "react";
import API from "../api/config";
import "../components/JoinGame.css";

export default function JoinGame({ onJoin }) {
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  const handleJoin = async () => {
    const res = await fetch(`${API}/join`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name })
    });
    const data = await res.json();
    if (res.ok) onJoin(name, data.players);
    else setError(data.error);
  };

  return (
    <div className="join-container">
      <h2>Join NotUNO</h2>
      <input
        value={name}
        onChange={e => setName(e.target.value)}
        placeholder="Your name"
      />
      <button onClick={handleJoin}>Join</button>
      {error && <div className="error">{error}</div>}
    </div>
  );
}
