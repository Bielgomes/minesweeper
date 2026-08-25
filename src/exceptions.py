class MinesweeperException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class InvalidGameModeException(MinesweeperException):
    def __init__(self):
        super().__init__(message="Game mode inválido")
