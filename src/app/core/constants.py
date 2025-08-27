from pathlib import Path
import pygame
import os

# Video setup
FPS = 60

# Board setup
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH//COLS

# RGB
RED = (191, 55, 60)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREY = (128,128,128)

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "ui" / "assets"
CROWN_PATH = ASSETS_DIR / "crown.png"
CROWN = pygame.transform.scale(
    pygame.image.load(str(CROWN_PATH)),
    (44, 25)
)
