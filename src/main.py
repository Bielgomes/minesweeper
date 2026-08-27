import pygame

from core.game_controller import GameController


def main():
    pygame.init()
    pygame.mixer.init()

    game_controller = GameController()
    game_controller.run()

    pygame.quit()


if __name__ == "__main__":
    main()
