import time

import pygame

from resources import Resources


class HUD:
    def __init__(self, mine_count: int):
        self._elapsed_seconds = 0.0
        self._start_time: float | None = None

        self._elapsed_seconds_text_width: int | None = None
        self._face_width: int | None = None

        self._mine_count = mine_count

    def reset(self, mine_count: int) -> None:
        self._elapsed_seconds = 0.0
        self._start_time = None

        self._elapsed_seconds_text_width = None
        self._face_width = None

        self._mine_count = mine_count

    def start_timer(self) -> None:
        self._start_time = time.perf_counter()

    def render(
        self,
        screen: pygame.Surface,
        is_game_over: bool,
        player_has_exploded: bool,
        flags_count: int,
    ) -> None:
        if not is_game_over:
            self._elapsed_seconds = (
                int(time.perf_counter() - self._start_time) if self._start_time else 0
            )

        elapsed_seconds_text = Resources.ui_font.render(
            text=f"{min(self._elapsed_seconds, 999):03}",
            antialias=True,
            color="red",
        )
        flags_text = Resources.ui_font.render(
            text=f"{self._mine_count - flags_count:03}",
            antialias=True,
            color="red",
        )

        face = (
            Resources.smile_face
            if not is_game_over
            else Resources.sad_face
            if player_has_exploded
            else Resources.sunglasses_face
        )

        if self._elapsed_seconds_text_width is None:
            self._elapsed_seconds_text_width = (
                screen.width - elapsed_seconds_text.width - 23
            )
        if self._face_width is None:
            self._face_width = screen.width / 2 - face.width / 2

        screen.blits(
            (
                (
                    elapsed_seconds_text,
                    (self._elapsed_seconds_text_width, 17),
                ),
                (flags_text, (27, 17)),
                (
                    face,
                    (self._face_width, 25),
                ),
            )
        )
