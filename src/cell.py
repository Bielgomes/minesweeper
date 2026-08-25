import pygame

from resources import Resources

ADJACENT_MINE_TEXT_COLORS = [
    "#0000FD",
    "#017E04",
    "#FD0100",
    "#010180",
    "#810103",
    "#00807E",
    "#000000",
    "#808080",
]


class Cell:
    def __init__(
        self,
        pos: pygame.Vector2,
        cell_size: int,
        has_mine: bool = False,
        is_flagged: bool = False,
        is_revealed: bool = False,
        is_exploded: bool = False,
    ):
        self._pos: pygame.Vector2 = pos
        self._cell_size = cell_size
        self._sprite = Resources.cell_sprite
        self._adjacent_mines_count = 0

        self._has_mine = has_mine
        self._is_flagged = is_flagged
        self._is_revealed = is_revealed
        self._is_exploded = is_exploded

        self._flag_sprite_x = (
            self._pos[0] + self._cell_size / 2 - Resources.flag_sprite.width / 2
        )
        self._flag_sprite_y = (
            self._pos[1] + self._cell_size / 2 - Resources.flag_sprite.height / 2
        )

        self._mine_sprite_x = (
            self._pos[0] + self._cell_size / 2 - Resources.mine_sprite.width / 2
        )
        self._mine_sprite_y = (
            self._pos[1] + self._cell_size / 2 - Resources.mine_sprite.height / 2
        )

    @property
    def has_mine(self) -> bool:
        return self._has_mine

    @property
    def is_flagged(self) -> bool:
        return self._is_flagged

    @property
    def is_revealed(self) -> bool:
        return self._is_revealed

    @property
    def adjacent_mines_count(self) -> int:
        return self._adjacent_mines_count

    @has_mine.setter
    def has_mine(self, has_mine: bool) -> None:
        self._has_mine = has_mine

    @is_flagged.setter
    def is_flagged(self, is_flagged: bool) -> None:
        self._is_flagged = is_flagged

    @is_revealed.setter
    def is_revealed(self, is_revealed: bool) -> None:
        if self._is_exploded:
            return

        self._is_revealed = is_revealed
        self._is_flagged = False
        self._sprite = Resources.revealed_cell_sprite

        if self.adjacent_mines_count > 0:
            text_color = ADJACENT_MINE_TEXT_COLORS[self.adjacent_mines_count - 1]
            self._adjacent_mine_count_text = Resources.default_font.render(
                text=str(self.adjacent_mines_count),
                antialias=True,
                color=text_color,
            )
            self._adjacent_mine_count_text_x = (
                self._pos[0]
                + self._cell_size / 2
                - self._adjacent_mine_count_text.width / 2
            )
            self._adjacent_mine_count_text_y = (
                self._pos[1]
                + self._cell_size / 2
                - self._adjacent_mine_count_text.height / 2
                + 2
            )

    @adjacent_mines_count.setter
    def adjacent_mines_count(self, adjacent_mines_count) -> None:
        self._adjacent_mines_count = adjacent_mines_count

    def explode(self) -> None:
        self._is_exploded = True
        self._is_revealed = True
        self._sprite = Resources.exploded_cell_sprite

    def render(self, surface: pygame.Surface):
        surface.blit(self._sprite, self._pos)

        if self.is_flagged:
            surface.blit(
                Resources.flag_sprite,
                (
                    self._flag_sprite_x,
                    self._flag_sprite_y,
                ),
            )
        elif self.has_mine and self.is_revealed:
            surface.blit(
                Resources.mine_sprite,
                (
                    self._mine_sprite_x,
                    self._mine_sprite_y,
                ),
            )
        elif self.adjacent_mines_count > 0 and not self.has_mine and self.is_revealed:
            surface.blit(
                self._adjacent_mine_count_text,
                (
                    self._adjacent_mine_count_text_x,
                    self._adjacent_mine_count_text_y,
                ),
            )
