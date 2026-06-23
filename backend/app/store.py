import asyncio


class Store:
    def __init__(self) -> None:
        # SSE subscriber queues — intentionally in-memory (ephemeral, per-process)
        self.all_games_queues: list[asyncio.Queue] = []
        self.game_queues: dict[str, list[asyncio.Queue]] = {}

    def reset(self) -> None:
        self.__init__()


store = Store()
