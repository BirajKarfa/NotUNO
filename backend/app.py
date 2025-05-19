from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

players = []
game_state = {
    "started": False,
    "players": {},      # name → hand list
    "turn_index": 0,    # index in players[]
    "discard_pile": [], # list, last element is top
    "draw_pile": []     # remaining deck
}

def init_deck():
    colors = ["R","G","B","Y"]
    # Number cards 0–9 ×2
    deck = [f"{c}{n}" for c in colors for n in range(10)] * 2
    # +2 cards ×2 each color
    deck += [f"{c}+2" for c in colors for _ in range(2)]
    # Wild cards (colorless) ×4
    deck += ["W"] * 4
    random.shuffle(deck)
    return deck

@app.route("/join", methods=["POST"])
def join():
    if game_state["started"]:
        return jsonify(error="Game already started"), 403
    name = request.get_json().get("name","").strip()
    if not name:
        return jsonify(error="No name provided"), 400
    if name in players:
        return jsonify(error="Name already taken"), 400
    if len(players) >= 4:
        return jsonify(error="Game is full"), 403

    players.append(name)
    game_state["players"][name] = []
    return jsonify(message=f"{name} joined", players=players)

@app.route("/start", methods=["POST"])
def start():
    if game_state["started"]:
        return jsonify(error="Game already started"), 400
    if len(players) < 2:
        return jsonify(error="At least 2 players required"), 400

    deck = init_deck()
    # Deal 7 to each
    for p in players:
        game_state["players"][p] = [deck.pop() for _ in range(7)]
    # One to discard
    game_state["discard_pile"] = [deck.pop()]
    game_state["draw_pile"] = deck
    game_state["turn_index"] = 0
    game_state["started"] = True
    return jsonify(message="Game started", players=players)

@app.route("/state", methods=["GET"])
def state():
    name = request.args.get("name","").strip()
    if name not in players:
        return jsonify(error="Invalid player"), 400

    top = game_state["discard_pile"][-1] if game_state["discard_pile"] else None
    counts = {p: len(h) for p,h in game_state["players"].items()}
    return jsonify(
        started=game_state["started"],
        players=players,
        hand=game_state["players"][name],
        current_turn=players[game_state["turn_index"]],
        top_discard=top,
        players_card_counts=counts
    )

@app.route("/play", methods=["POST"])
def play():
    data = request.get_json()
    name = data.get("name","").strip()
    card = data.get("card","")
    if name not in players or not card:
        return jsonify(error="Invalid play"), 400
    # must be your turn
    if players[game_state["turn_index"]] != name:
        return jsonify(error="Not your turn"), 403

    hand = game_state["players"][name]
    if card not in hand:
        return jsonify(error="You don't have that card"), 400

    # Wild special handling
    if card == "W":
        chosen = data.get("color","").strip().upper()
        if chosen not in ["R","G","B","Y"]:
            return jsonify(error="Invalid wild color"), 400
        # remove wild from hand
        hand.remove("W")
        # play as color-only card (no number)
        game_state["discard_pile"].append(chosen)
    else:
        # Normal or +2
        top = game_state["discard_pile"][-1]
        top_color, top_num = top[0], top[1:]
        color, num = card[0], card[1:]
        # match color or number or +2 logic
        if not (color == top_color or num == top_num):
            return jsonify(error="Card does not match top discard"), 400
        hand.remove(card)
        game_state["discard_pile"].append(card)

    # Winner check
    if len(hand) == 0:
        winner = name
        # reset game
        players.clear()
        game_state.update({
            "started": False,
            "players": {},
            "turn_index": 0,
            "discard_pile": [],
            "draw_pile": []
        })
        return jsonify(message=f"{winner} wins!")

    # Advance turn
    game_state["turn_index"] = (game_state["turn_index"] + 1) % len(players)
    return jsonify(message=f"{name} played {card}")

@app.route("/draw", methods=["POST"])
def draw():
    name = request.get_json().get("name","").strip()
    if name not in players:
        return jsonify(error="Invalid draw"), 400
    if players[game_state["turn_index"]] != name:
        return jsonify(error="Not your turn"), 403
    if not game_state["draw_pile"]:
        return jsonify(error="No cards to draw"), 400

    card = game_state["draw_pile"].pop()
    game_state["players"][name].append(card)
    game_state["turn_index"] = (game_state["turn_index"] + 1) % len(players)
    return jsonify(message=f"{name} drew a card", card=card)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
