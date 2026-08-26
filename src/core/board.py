import secrets

import pygame

from core.cell import Cell


class Board:
    def __init__(
        self,
        rows: int,
        columns: int,
        cell_size: int,
        mine_count: int,
        padding_x: int = 15,
        padding_top: int = 100,
    ) -> None:
        self._rows = rows
        self._columns = columns
        self._cell_size = cell_size
        self._mine_count = mine_count
        self._padding_x = padding_x
        self._padding_top = padding_top

        self._cells: list[Cell] = []
        self._max_cell_index = (self._rows * self._columns) - 1

        self._are_mines_placed = False
        self._flags_on_the_field = 0

    @property
    def are_mines_placed(self) -> bool:
        return self._are_mines_placed

    @property
    def flags_on_the_field(self) -> int:
        return self._flags_on_the_field

    @flags_on_the_field.setter
    def flags_on_the_field(self, flags_on_the_field: int) -> None:
        self._flags_on_the_field = flags_on_the_field

    @property
    def are_all_safe_cells_revealed(self) -> bool:
        return all(cell.has_mine or cell.is_revealed for cell in self.cells)

    @property
    def cells(self) -> list[Cell]:
        return self._cells

    @cells.setter
    def cells(self, cells: list[Cell]) -> None:
        self._cells = cells

    def reset(
        self,
        rows: int,
        columns: int,
        cell_size: int,
        mine_count: int,
    ) -> None:
        self._rows = rows
        self._columns = columns
        self._cell_size = cell_size
        self._mine_count = mine_count

        self.flags_on_the_field = 0
        self._are_mines_placed = False

        self._max_cell_index = (self._rows * self._columns) - 1
        self.populate()

    def populate(self) -> None:
        self.cells = [
            Cell(
                pos=pygame.Vector2(
                    x=(column * self._cell_size) + self._padding_x,
                    y=(row * self._cell_size) + self._padding_top,
                ),
                cell_size=self._cell_size,
            )
            for row in range(self._rows)
            for column in range(self._columns)
        ]

    def reveal_neighbor_cells(self, index: int):
        current_cell = self.cells[index]
        if current_cell.is_flagged:
            self._flags_on_the_field -= 1

        current_cell.is_revealed = True
        if current_cell.adjacent_mines_count > 0:
            return

        row = index // self._columns
        col = index % self._columns

        for direction_row in [-1, 0, 1]:
            for direction_col in [-1, 0, 1]:
                if direction_row == 0 and direction_col == 0:
                    continue

                neighbor_row = row + direction_row
                neighbor_col = col + direction_col

                if 0 <= neighbor_row < self._rows and 0 <= neighbor_col < self._columns:
                    neighbor_index = neighbor_row * self._columns + neighbor_col
                    if not self.cells[neighbor_index].is_revealed:
                        self.reveal_neighbor_cells(neighbor_index)

    def reveal_all_mines(self) -> None:
        for index in range(self._max_cell_index + 1):
            target = self.cells[index]
            if target.has_mine and not target.is_flagged:
                target.is_revealed = True

    def __calculate_safe_cells(self, start_index: int) -> list[int]:
        safe_cells = [start_index]

        row = start_index // self._columns
        col = start_index % self._columns

        for direction_row in [-1, 0, 1]:
            for direction_col in [-1, 0, 1]:
                if direction_row == 0 and direction_col == 0:
                    continue

                neighbor_row = row + direction_row
                neighbor_col = col + direction_col

                if 0 <= neighbor_row < self._rows and 0 <= neighbor_col < self._columns:
                    neighbor_index = neighbor_row * self._columns + neighbor_col
                    safe_cells.append(neighbor_index)

        return safe_cells

    def place_mines(self, start_index: int) -> None:
        mines_to_place = self._mine_count
        safe_cells = self.__calculate_safe_cells(start_index)

        while mines_to_place > 0:
            index = secrets.randbelow(self._max_cell_index + 1)
            cell = self.cells[index]
            if cell.has_mine or cell.is_revealed or index in safe_cells:
                continue

            row = index // self._columns
            col = index % self._columns

            for direction_row in [-1, 0, 1]:
                for direction_col in [-1, 0, 1]:
                    if direction_row == 0 and direction_col == 0:
                        continue

                    neighbor_row = row + direction_row
                    neighbor_col = col + direction_col

                    if (
                        0 <= neighbor_row < self._rows
                        and 0 <= neighbor_col < self._columns
                    ):
                        neighbor_index = neighbor_row * self._columns + neighbor_col
                        self.cells[neighbor_index].adjacent_mines_count += 1

            cell.has_mine = True
            mines_to_place -= 1

        self._are_mines_placed = True

    def render(self, screen: pygame.Surface) -> None:
        for cell in self.cells:
            cell.render(surface=screen)
