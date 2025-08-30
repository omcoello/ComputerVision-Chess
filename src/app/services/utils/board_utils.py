from typing import Dict, List, Tuple
from core.constants import SQUARE_SIZE

Square = Dict[str, List[float]]

def generate_game_board_dict(size=SQUARE_SIZE) -> Square:
    """Generates the center positions of each square for pygame."""
    d: Square = {}
    counter = 0
    for i in range(8):
        for j in range(8):
            d[f"s{counter}"] = [j*size + size/2, i*size + size/2]
            counter += 1
    print("initial dictionary data:", d)
    return d

def get_row_col_from_mouse(pos: Tuple[int, int]) -> Tuple[int,int]:
    """Convert mouse position to board row and column."""
    x, y = pos
    return y // SQUARE_SIZE, x // SQUARE_SIZE