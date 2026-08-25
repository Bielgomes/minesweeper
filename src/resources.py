import pygame

from game_modes import GameMode


class Resources:
    default_font: pygame.Font | None = None
    mine_sprite: pygame.Surface | None = None
    flag_sprite: pygame.Surface | None = None

    cell_sprite: pygame.Surface | None = None
    revealed_cell_sprite: pygame.Surface | None = None
    exploded_cell_sprite: pygame.Surface | None = None

    smile_face: pygame.Surface | None = None
    sad_face: pygame.Surface | None = None
    sunglasses_face: pygame.Surface | None = None

    background: pygame.Surface | None = None

    click_sound: pygame.Sound | None = None
    lose_sound: pygame.Sound | None = None

    @classmethod
    def instanciate_resources(cls, game_mode: GameMode) -> None:
        cell_size = game_mode["cell_size"]
        background = game_mode["background"]

        cls.default_font = pygame.font.Font("src/fonts/GROSTE.ttf", 20)
        cls.ui_font = pygame.font.Font("src/fonts/Digital Dismay.otf", 68)

        cls.mine_sprite = pygame.transform.smoothscale(
            pygame.image.load("src/sprites/mine.png").convert_alpha(),
            (cell_size, cell_size),
        )
        cls.flag_sprite = pygame.transform.smoothscale(
            pygame.image.load("src/sprites/flag.png").convert_alpha(),
            (cell_size, cell_size),
        )

        cls.cell_sprite = pygame.transform.smoothscale(
            pygame.image.load("src/sprites/cell.png").convert_alpha(),
            (cell_size, cell_size),
        )
        cls.revealed_cell_sprite = pygame.transform.smoothscale(
            pygame.image.load("src/sprites/revealed-cell.png").convert_alpha(),
            (cell_size, cell_size),
        )
        cls.exploded_cell_sprite = pygame.transform.smoothscale(
            pygame.image.load("src/sprites/exploded-cell.png").convert_alpha(),
            (cell_size, cell_size),
        )

        cls.smile_face = pygame.image.load("src/sprites/smile-face.png").convert_alpha()
        cls.sad_face = pygame.image.load("src/sprites/sad-face.png").convert_alpha()
        cls.sunglasses_face = pygame.image.load(
            "src/sprites/sunglasses-face.png"
        ).convert_alpha()

        cls.background = pygame.image.load(f"src/sprites/{background}").convert_alpha()

        cls.start_sound = pygame.mixer.Sound("src/sounds/start.mp3")
        cls.start_sound.set_volume(0.2)
        cls.start_sound.fadeout(1000)

        cls.win_sound = pygame.mixer.Sound("src/sounds/win.mp3")
        cls.win_sound.set_volume(0.2)
        cls.win_sound.fadeout(1000)

        cls.click_sound = pygame.mixer.Sound("src/sounds/click.wav")
        cls.click_sound.set_volume(0.2)
        cls.click_sound.fadeout(1000)

        cls.lose_sound = pygame.mixer.Sound("src/sounds/lose.wav")
        cls.lose_sound.set_volume(0.5)
        cls.lose_sound.fadeout(1000)

    @classmethod
    def change_game_mode(cls, game_mode: GameMode) -> None:
        cell_size = game_mode["cell_size"]
        background = game_mode["background"]

        cls.mine_sprite = pygame.transform.smoothscale(
            pygame.image.load("src/sprites/mine.png").convert_alpha(),
            (cell_size, cell_size),
        )
        cls.flag_sprite = pygame.transform.smoothscale(
            pygame.image.load("src/sprites/flag.png").convert_alpha(),
            (cell_size, cell_size),
        )

        cls.cell_sprite = pygame.transform.smoothscale(
            pygame.image.load("src/sprites/cell.png").convert_alpha(),
            (cell_size, cell_size),
        )
        cls.revealed_cell_sprite = pygame.transform.smoothscale(
            pygame.image.load("src/sprites/revealed-cell.png").convert_alpha(),
            (cell_size, cell_size),
        )
        cls.exploded_cell_sprite = pygame.transform.smoothscale(
            pygame.image.load("src/sprites/exploded-cell.png").convert_alpha(),
            (cell_size, cell_size),
        )

        cls.background = pygame.image.load(f"src/sprites/{background}").convert_alpha()
