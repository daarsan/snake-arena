import time
import uuid

from .database import DbGame, DbScore, DbUser, SessionLocal
from .security import hash_password


def _now_ms() -> int:
    return int(time.time() * 1000)


def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(DbUser).count() > 0:
            return

        users_data = [
            ("alice", "alice1234"),
            ("bob",   "bob12345"),
            ("carol", "carol123"),
        ]
        rows: list[DbUser] = []
        for username, password in users_data:
            uid = str(uuid.uuid4())
            row = DbUser(id=uid, username=username, hashed_password=hash_password(password))
            db.add(row)
            rows.append(row)
        db.flush()

        alice, bob, carol = rows

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
            db.add(DbScore(
                id=str(uuid.uuid4()),
                user_id=user.id,
                username=user.username,
                mode=mode,
                score=score,
                created_at=_now_ms(),
            ))

        gs = 20
        cx, cy = gs // 2, gs // 2
        db.add(DbGame(
            id=str(uuid.uuid4()),
            user_id=alice.id,
            username=alice.username,
            mode="walls",
            score=30,
            snake=[{"x": cx, "y": cy}, {"x": cx - 1, "y": cy}, {"x": cx - 2, "y": cy}],
            food={"x": cx + 3, "y": cy + 2},
            grid_size=gs,
            alive=True,
            updated_at=_now_ms(),
        ))
        db.add(DbGame(
            id=str(uuid.uuid4()),
            user_id=bob.id,
            username=bob.username,
            mode="wrap",
            score=50,
            snake=[{"x": 5, "y": 8}, {"x": 5, "y": 7}, {"x": 5, "y": 6}, {"x": 5, "y": 5}],
            food={"x": 12, "y": 3},
            grid_size=gs,
            alive=True,
            updated_at=_now_ms(),
        ))

        db.commit()
    finally:
        db.close()
