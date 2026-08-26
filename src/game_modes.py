from typing import TypedDict


class GameMode(TypedDict):
    id: int
    name: str
    columns: int
    rows: int
    cell_size: int
    mines: int


GAME_MODES = {
    0: GameMode(
        {
            "id": 0,
            "name": "Fácil",
            "columns": 10,
            "rows": 8,
            "cell_size": 40,
            "mines": 10,
            "background": "background-01.png",
        }
    ),
    1: GameMode(
        {
            "id": 1,
            "name": "Médio",
            "columns": 18,
            "rows": 16,
            "cell_size": 30,
            "mines": 40,
            "background": "background-02.png",
        }
    ),
    2: GameMode(
        {
            "id": 2,
            "name": "Dificil",
            "columns": 26,
            "rows": 24,
            "cell_size": 26,
            "mines": 99,
            "background": "background-03.png",
        }
    ),
}
