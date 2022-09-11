import pygame
from constants import *
from game import Game
from pygame_widgets.button import Button
import pygame_widgets

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)

icon = pygame.image.load(ICON_PATH_PNG)
pygame.display.set_icon(icon)

screen.fill(WHITE)

game = Game(screen)

reset_btn = Button(screen, 0, 0, 100, 50, text="Reset", onClick=lambda: game.reset(), colour=GREY, fontSize=30)

def get_mouse_row_col(pos):
    x, y = pos
    row = y // SQUARE_SIZE - 1
    col = x // SQUARE_SIZE - 1
    return int(row), int(col)

def main():
    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_mouse_row_col(pos)
                if -1 < row < 8 and -1 < col < 8:
                    game.select(row, col)
                else:
                    game.valid_moves = []
                    game.select_frame = None

        game.update()
        pygame_widgets.update(events)
        pygame.display.flip()

if __name__ == "__main__":
    main()