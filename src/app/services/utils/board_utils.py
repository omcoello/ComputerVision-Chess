from typing import Dict, List, Tuple
from checkers.constants import SQUARE_SIZE

Square = Dict[str, List[float]]

def generate_game_board_dict(size=SQUARE_SIZE) -> Square:
    """Genera las posiciones centrales de cada cuadrado para pygame."""
    d: Square = {}
    counter = 0
    for i in range(8):
        for j in range(8):
            d[f"s{counter}"] = [j*size + size/2, i*size + size/2]
            counter += 1
    return d

def get_row_col_from_mouse(pos: Tuple[int, int]) -> Tuple[int,int]:
    """Convierte posición de mouse a fila y columna del tablero."""
    x, y = pos
    return y // SQUARE_SIZE, x // SQUARE_SIZE