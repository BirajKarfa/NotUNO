import React, { useEffect, useState, useRef, useCallback } from "react";
import API from "../api/config";
import "../components/GameBoard.css";

export default function GameBoard({ player }) {
  const [st, setSt] = useState(null);
  const poll = useRef(null);

  const fetchState = useCallback(async () => {
    try {
      const res = await fetch(`${API}/state?name=${encodeURIComponent(player)}`);
      const data = await res.json();
      setSt(data);
    } catch (e) {
      console.error("Polling error", e);
    }
  }, [player]);

  useEffect(() => {
    fetchState();
    poll.current = setInterval(fetchState, 3000);
    return () => clearInterval(poll.current);
  }, [fetchState]);

  if (!st) return <div className="board">Loading…</div>;

  const { started, players, hand, current_turn, top_discard, players_card_counts } = st;
  const isHost = player === players[0];
  const isMyTurn = current_turn === player;

  const startGame = async () => {
    await fetch(`${API}/start`, { method: "POST" });
    fetchState();
  };

  const play = async (card) => {
    if (!isMyTurn) return alert("Not your turn");
    let body = { name: player, card };
    if (card === "W") {
      const color = prompt("Choose color: R, G, B or Y").toUpperCase();
      body.color = color;
    }
    const res = await fetch(`${API}/play`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const data = await res.json();
    if (!res.ok) alert(data.error);
    fetchState();
  };

  const draw = async () => {
    if (!isMyTurn) return alert("Not your turn");
    await fetch(`${API}/draw`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: player })
    });
    fetchState();
  };

  return (
    <div className="board">
      <h2>Player: {player}</h2>
      <div className="players-bar">
        {players.map(p => (
          <div key={p} className="player-chip">
            {p} ({players_card_counts[p]})
          </div>
        ))}
      </div>

      {!started && isHost && (
        <button className="start-btn" onClick={startGame}>
          Start Game
        </button>
      )}

      {started && (
        <>
          <div className="info">
            <div>Turn: <b>{current_turn}</b></div>
            <div>
              Top: 
              <div className={`card ${top_discard[0]} top-card`}>
                {/* no number for wild or color-only */}
                {top_discard.length > 1 ? top_discard : ""}
              </div>
            </div>
          </div>

          <div className="hand">
            {hand.map((c,i) => (
              <div key={i} className={`card ${c[0]}`} onClick={()=>play(c)}>
                {/* show +2 or number, hide for color-only */}
                {c === "W" ? "W" : (c.length>1 ? c.slice(1) : "")}
              </div>
            ))}
          </div>

          <div className="draw-pile" onClick={draw}>NotUNO</div>
        </>
      )}
    </div>
  );
}
