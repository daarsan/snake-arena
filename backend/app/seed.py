import time
import uuid

from .security import hash_password
from .store import UserRecord, store


def _now_ms() -> int:
    return int(time.time() * 1000)


def seed() -> None:
    # ── Users ────────────────────────────────────────────────────────────────
    users = [
        ("alice", "alice1234"),
        ("bob",   "bob12345"),
        ("carol", "carol123"),
    ]
    records: list[UserRecord] = []
    for username, password in users:
        uid = str(uuid.uuid4())
        rec = UserRecord(id=uid, username=username, hashed_password=hash_password(password))
        store.users[uid] = rec
        store.usernames[username] = uid
        records.append(rec)

    alice, bob, carol = records

    # ── Scores ───────────────────────────────────────────────────────────────
    raw_scores = [
        (alice, "walls", 420),
        (alice, "walls", 310),
        (alice, "wrap",  540),
        (bob,   "walls", 380),
        (bob,   "walls", 290),
        (bob,   "wrap",  610),
        (bob,   "wrap",  480),
        (carol, "walls", 520),
        (carol, "wrap",  390),
        (carol, "wrap",  270),
    ]
    for user, mode, score in raw_scores:
        store.scores.append({
            "id": str(uuid.uuid4()),
            "userId": user.id,
            "username": user.username,
            "mode": mode,
            "score": score,
            "createdAt": _now_ms(),
        })

    # ── Active games ─────────────────────────────────────────────────────────
    gs = 20
    cx, cy = gs // 2, gs // 2

    alice_game_id = str(uuid.uuid4())
    alice_game = {
        "id": alice_game_id,
        "userId": alice.id,
        "username": alice.username,
        "mode": "walls",
        "score": 30,
        "snake": [
            {"x": cx,     "y": cy},
            {"x": cx - 1, "y": cy},
            {"x": cx - 2, "y": cy},
        ],
        "food": {"x": cx + 3, "y": cy + 2},
        "gridSize": gs,
        "alive": True,
        "updatedAt": _now_ms(),
    }
    store.games[alice_game_id] = alice_game
    store.game_queues[alice_game_id] = []

    bob_game_id = str(uuid.uuid4())
    bob_game = {
        "id": bob_game_id,
        "userId": bob.id,
        "username": bob.username,
        "mode": "wrap",
        "score": 50,
        "snake": [
            {"x": 5, "y": 8},
            {"x": 5, "y": 7},
            {"x": 5, "y": 6},
            {"x": 5, "y": 5},
        ],
        "food": {"x": 12, "y": 3},
        "gridSize": gs,
        "alive": True,
        "updatedAt": _now_ms(),
    }
    store.games[bob_game_id] = bob_game
    store.game_queues[bob_game_id] = []
