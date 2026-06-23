import asyncio
from dataclasses import dataclass, field


@dataclass
class UserRecord:
    id: str
    username: str
    hashed_password: str


class Store:
    def __init__(self) -> None:
        self.users: dict[str, UserRecord] = {}      # id → UserRecord
        self.usernames: dict[str, str] = {}         # username → id
        self.sessions: dict[str, str] = {}          # token → user_id
        self.scores: list[dict] = []
        self.games: dict[str, dict] = {}            # game_id → game dict

        # SSE subscriber queues
        self.all_games_queues: list[asyncio.Queue] = []
        self.game_queues: dict[str, list[asyncio.Queue]] = {}

    def reset(self) -> None:
        self.__init__()


store = Store()
