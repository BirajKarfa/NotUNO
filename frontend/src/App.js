import React, { useState } from "react";
import JoinGame from "./components/JoinGame";
import GameBoard from "./components/GameBoard";
import "./App.css";

export default function App() {
  const [player, setPlayer] = useState(null);
  return (
    <div className="app">
      {!player ? (
        <JoinGame onJoin={name => setPlayer(name)} />
      ) : (
        <GameBoard player={player} />
      )}
    </div>
  );
}
