import pygame

from core.board import Board
from core.hud import HUD
from exceptions import InvalidGameModeException
from game_modes import GAME_MODES, GameMode
from resources import Resources


class GameController:
    def __init__(self, game_mode: int = 1) -> None:
        selected_game_mode = GAME_MODES.get(game_mode)
        if selected_game_mode is None:
            raise InvalidGameModeException()

        self.game_mode = selected_game_mode

        self._is_running = True
        self._is_holding_mouse = False

        self._is_game_over = False
        self._player_has_exploded = False

        self._padding_x = 15
        self._padding_top = 100
        self._padding_bottom = 15

        self._hud = HUD(mine_count=self.game_mode["mines"])
        self._board = Board(
            rows=self.game_mode["rows"],
            columns=self.game_mode["columns"],
            cell_size=self.game_mode["cell_size"],
            mine_count=self.game_mode["mines"],
            padding_x=self._padding_x,
            padding_top=self._padding_top,
        )

    @property
    def game_mode(self) -> GameMode:
        return self._game_mode

    @game_mode.setter
    def game_mode(self, game_mode: GameMode) -> None:
        self._game_mode = game_mode

        self._columns = self._game_mode["columns"]
        self._rows = self._game_mode["rows"]
        self._cell_size = self._game_mode["cell_size"]

    def __update_screen(self) -> None:
        self._screen_width = self._cell_size * self._columns + self._padding_x * 2
        self._screen_height = (
            self._cell_size * self._rows + self._padding_top + self._padding_bottom
        )

        self._screen_width_limit = self._screen_width - self._padding_x
        self._screen_height_limit = self._screen_height - self._padding_bottom

        self._screen = pygame.display.set_mode(
            (self._screen_width, self._screen_height)
        )
        pygame.display.set_caption(f"Campo Minado ({self.game_mode['name']})")

    def __clear_screen(self) -> None:
        self._screen.blit(self._background, (0, 0))

    def __pull_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._is_running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.__reset()

    def __get_mouse_event(self) -> None:
        pressed_buttons = pygame.mouse.get_pressed()

        if not (pressed_buttons[0] or pressed_buttons[2]):
            self._is_holding_mouse = False
            return

        if self._is_holding_mouse:
            return

        self._is_holding_mouse = True
        mouse_x, mouse_y = pygame.mouse.get_pos()

        on_the_board = (
            self._padding_x < mouse_x < self._screen_width_limit
            and self._padding_top < mouse_y < self._screen_height_limit
        )
        if on_the_board and not self._is_game_over:
            self.__handle_board_mouse_event(mouse_x, mouse_y, pressed_buttons)
            return

        on_the_button = (
            self._screen_width / 2 - Resources.smile_face.width / 2
            < mouse_x
            < self._screen_width / 2 + Resources.smile_face.width / 2
            and 25 < mouse_y < 25 + Resources.smile_face.height
        )
        if on_the_button:
            self.__handle_ui_mouse_event(pressed_buttons)
            return

    def __handle_board_mouse_event(
        self, mouse_x: int, mouse_y: int, pressed_buttons: tuple[bool, bool, bool]
    ):
        column = (mouse_x - self._padding_x) // self._cell_size
        row = (mouse_y - self._padding_top) // self._cell_size
        target_index = row * self._columns + column
        target_cell = self._board.cells[target_index]

        if pressed_buttons[0]:
            if target_cell.is_revealed or target_cell.is_flagged:
                return

            if target_cell.has_mine:
                self._is_game_over = True

                target_cell.explode()
                self._player_has_exploded = True

                self._board.reveal_all_mines()
                Resources.lose_sound.play()

            if not self._board.are_mines_placed:
                Resources.start_sound.play()

                self._board.place_mines(start_index=target_index)
                self._hud.start_timer()

            self._board.reveal_neighbor_cells(target_index)
            if not target_cell.has_mine:
                Resources.click_sound.play()

            if self._board.are_all_safe_cells_revealed:
                Resources.win_sound.play()
                self._is_game_over = True
                self._board.reveal_all_mines()

        elif pressed_buttons[2]:
            if not self._board.are_mines_placed or target_cell.is_revealed:
                return

            if (
                not target_cell.is_flagged
                and self._board.flags_on_the_field < self.game_mode["mines"]
            ):
                target_cell.is_flagged = True
                self._board.flags_on_the_field += 1

            elif target_cell.is_flagged:
                target_cell.is_flagged = False
                self._board.flags_on_the_field -= 1

    def __handle_ui_mouse_event(self, pressed_buttons: tuple[bool, bool, bool]):
        if not pressed_buttons[0]:
            return

        if self._board.are_mines_placed:
            self.__reset()
            return

        self.game_mode = GAME_MODES.get((self.game_mode["id"] + 1) % len(GAME_MODES))
        Resources.change_game_mode(game_mode=self.game_mode)

        self._background = Resources.background
        self.__reset()

    def __reset(self) -> None:
        Resources.start_sound.stop()

        self._is_game_over = False
        self._player_has_exploded = False

        self.__update_screen()

        self._board.reset(
            rows=self.game_mode["rows"],
            columns=self.game_mode["columns"],
            cell_size=self.game_mode["cell_size"],
            mine_count=self.game_mode["mines"],
        )
        self._hud.reset(mine_count=self.game_mode["mines"])

    def run(self) -> None:
        clock = pygame.time.Clock()
        self.__update_screen()

        Resources.instanciate_resources(game_mode=self.game_mode)
        self._background = Resources.background
        self._board.populate()

        while self._is_running:
            self.__pull_events()
            self.__get_mouse_event()

            self.__clear_screen()

            self._board.render(screen=self._screen)
            self._hud.render(
                screen=self._screen,
                is_game_over=self._is_game_over,
                player_has_exploded=self._player_has_exploded,
                flags_count=self._board.flags_on_the_field,
            )

            pygame.display.flip()
            clock.tick(60)
