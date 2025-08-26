import pygame
from checkers.constants import WIDTH, HEIGHT

def init_pygame_window(title="Checkers"):
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(title)
    return win
