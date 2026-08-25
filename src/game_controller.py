import secrets
import time
from datetime import datetime

import pygame

from cell import Cell
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
        self._are_bombs_placed = False

        self._is_game_over = False
        self._player_has_exploded = False

        self._padding_x = 15
        self._padding_top = 100
        self._padding_bottom = 15

        self._flags_on_the_field = 0
        self._start_time: datetime | None = None

        self._cells: list[Cell] = []

    @property
    def is_game_over(self) -> bool:
        return self._is_game_over

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def game_mode(self) -> GameMode:
        return self._game_mode

    @property
    def columns(self) -> int:
        return self._columns

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cells(self) -> list[Cell]:
        return self._cells

    @is_game_over.setter
    def is_game_over(self, is_game_over: bool) -> None:
        self._is_game_over = is_game_over

    @is_running.setter
    def is_running(self, is_running: bool) -> None:
        self._is_running = is_running

    @cells.setter
    def cells(self, cells: list[Cell]) -> None:
        self._cells = cells

    @game_mode.setter
    def game_mode(self, game_mode: GameMode) -> None:
        self._game_mode = game_mode

        self._columns = self._game_mode["columns"]
        self._rows = self._game_mode["rows"]
        self._cell_size = self._game_mode["cell_size"]

    def __update_screen(self) -> None:
        self._screen_width = self._cell_size * self.columns + self._padding_x * 2
        self._screen_height = (
            self._cell_size * self.rows + self._padding_top + self._padding_bottom
        )

        self._screen_width_limit = self._screen_width - self._padding_x
        self._screen_height_limit = self._screen_height - self._padding_bottom

        self._screen = pygame.display.set_mode(
            (self._screen_width, self._screen_height)
        )
        pygame.display.set_caption(f"Campo Minado ({self.game_mode['name']})")

    def __clear_screen(self) -> None:
        self._screen.blit(self._background, (0, 0))

    def __calculate_safe_cells(self, start_index: int) -> list[int]:
        safe_cells = [start_index]

        row = start_index // self.columns
        col = start_index % self.columns

        for direction_row in [-1, 0, 1]:
            for direction_col in [-1, 0, 1]:
                if direction_row == 0 and direction_col == 0:
                    continue

                neighbor_row = row + direction_row
                neighbor_col = col + direction_col

                if 0 <= neighbor_row < self.rows and 0 <= neighbor_col < self.columns:
                    neighbor_index = neighbor_row * self.columns + neighbor_col
                    safe_cells.append(neighbor_index)
        return safe_cells

    def __place_bombs(self, start_index: int) -> None:
        bombs_to_place = self.game_mode["bombs"]
        safe_cells = self.__calculate_safe_cells(start_index)

        while bombs_to_place > 0:
            index = secrets.randbelow(self.max_cell_index)
            cell = self.cells[index]
            if cell.has_mine or cell.is_revealed or index in safe_cells:
                continue

            row = index // self.columns
            col = index % self.columns

            for direction_row in [-1, 0, 1]:
                for direction_col in [-1, 0, 1]:
                    if direction_row == 0 and direction_col == 0:
                        continue

                    neighbor_row = row + direction_row
                    neighbor_col = col + direction_col

                    if (
                        0 <= neighbor_row < self.rows
                        and 0 <= neighbor_col < self.columns
                    ):
                        neighbor_index = neighbor_row * self.columns + neighbor_col
                        self.cells[neighbor_index].adjacent_mines_count += 1

            cell.has_mine = True
            bombs_to_place -= 1

        self._are_bombs_placed = True
        self._start_time = time.perf_counter()

    def __populate_cell_list(self) -> None:
        self.max_cell_index = self.rows * self.columns - 1

        self.cells = [
            Cell(
                pos=pygame.Vector2(
                    x=(column * self._cell_size) + self._padding_x,
                    y=(row * self._cell_size) + self._padding_top,
                ),
                cell_size=self._cell_size,
            )
            for row in range(self.rows)
            for column in range(self.columns)
        ]

    def __render_cells(self) -> None:
        for cell in self.cells:
            cell.render(surface=self._screen)

    def __pull_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.__reset()

    def __reveal_neighbor_cells(self, index: int):
        current_cell = self.cells[index]
        if current_cell.is_flagged:
            self._flags_on_the_field -= 1

        current_cell.is_revealed = True
        if current_cell.adjacent_mines_count > 0:
            return

        row = index // self.columns
        col = index % self.columns

        for direction_row in [-1, 0, 1]:
            for direction_col in [-1, 0, 1]:
                if direction_row == 0 and direction_col == 0:
                    continue

                neighbor_row = row + direction_row
                neighbor_col = col + direction_col

                if 0 <= neighbor_row < self.rows and 0 <= neighbor_col < self.columns:
                    neighbor_index = neighbor_row * self.columns + neighbor_col
                    if not self.cells[neighbor_index].is_revealed:
                        self.__reveal_neighbor_cells(neighbor_index)

    def __reveal_all_mines(self) -> None:
        for index in range(self.max_cell_index):
            target = self.cells[index]
            if target.has_mine and not target.is_flagged:
                target.is_revealed = True

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
        if on_the_board and not self.is_game_over:
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
        target_index = row * self.columns + column
        target_cell = self.cells[target_index]

        if pressed_buttons[0]:
            if target_cell.is_revealed or target_cell.is_flagged:
                return

            if target_cell.has_mine:
                self.is_game_over = True
                target_cell.explode()
                self._player_has_exploded = True

                self.__reveal_all_mines()
                Resources.lose_sound.play()

            if not self._are_bombs_placed:
                Resources.start_sound.play()
                self.__place_bombs(start_index=target_index)

            self.__reveal_neighbor_cells(target_index)
            if not target_cell.has_mine:
                Resources.click_sound.play()

            if all(cell.has_mine or cell.is_revealed for cell in self.cells):
                Resources.win_sound.play()
                self.is_game_over = True
                self.__reveal_all_mines()

        elif pressed_buttons[2]:
            if not self._are_bombs_placed or target_cell.is_revealed:
                return

            if (
                not target_cell.is_flagged
                and self._flags_on_the_field < self.game_mode["bombs"]
            ):
                target_cell.is_flagged = True
                self._flags_on_the_field += 1

            elif target_cell.is_flagged:
                target_cell.is_flagged = False
                self._flags_on_the_field -= 1

    def __handle_ui_mouse_event(self, pressed_buttons: tuple[bool, bool, bool]):
        if not pressed_buttons[0]:
            return

        if self._are_bombs_placed:
            self.__reset()
            return

        self.game_mode = GAME_MODES.get((self.game_mode["id"] + 1) % len(GAME_MODES))
        Resources.change_game_mode(game_mode=self.game_mode)

        self._background = Resources.background
        self.__reset()

    def __update_ui(self) -> None:
        if not self.is_game_over:
            self.elapsed_seconds = (
                int(time.perf_counter() - self._start_time) if self._start_time else 0
            )

        elapsed_seconds_text = Resources.ui_font.render(
            text=f"{min(self.elapsed_seconds, 999):03}",
            antialias=True,
            color="red",
        )
        flags_text = Resources.ui_font.render(
            text=f"{self.game_mode['bombs'] - self._flags_on_the_field:03}",
            antialias=True,
            color="red",
        )

        face = (
            Resources.smile_face
            if not self.is_game_over
            else Resources.sad_face
            if self._player_has_exploded
            else Resources.sunglasses_face
        )
        self._screen.blits(
            (
                (
                    elapsed_seconds_text,
                    (self._screen_width - elapsed_seconds_text.width - 23, 17),
                ),
                (flags_text, (27, 17)),
                (
                    face,
                    (self._screen_width / 2 - face.width / 2, 25),
                ),
            )
        )

    def __reset(self) -> None:
        self._are_bombs_placed = False
        self._flags_on_the_field = 0
        self._start_time = None
        self.is_game_over = False
        self._player_has_exploded = False

        self.__populate_cell_list()
        self.__update_screen()

    def run(self) -> None:
        clock = pygame.time.Clock()
        self.__update_screen()

        Resources.instanciate_resources(game_mode=self.game_mode)
        self._background = Resources.background

        self.__populate_cell_list()

        while self.is_running:
            self.__pull_events()
            self.__get_mouse_event()

            self.__clear_screen()
            self.__render_cells()

            self.__update_ui()

            pygame.display.flip()

            clock.tick(60)
