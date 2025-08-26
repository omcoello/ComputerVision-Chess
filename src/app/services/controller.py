import pygame
import cv2
import numpy as np
from checkers.constants import SQUARE_SIZE, FPS
from checkers.game import Game

from app.services.camera import CameraCapture
from app.services.calibrator import Calibrator
from app.services.board_mapper import BoardMapper
from app.services.selector import Selector
from app.ui.pygame_ui import init_pygame_window
from app.services.utils.board_utils import generate_game_board_dict

class GameController:
    def __init__(self, device_index=0, debug=True):
        # Configuración
        self.debug = debug
        self.win = init_pygame_window()
        self.camera = CameraCapture(device_index=device_index)
        self.calibrator = Calibrator()
        self.board_mapper = BoardMapper()
        self.selector = Selector()
        self.game = Game(self.win)

        # Captura inicial y calibración
        frame = self.camera.capture_frame()
        if frame is None:
            raise RuntimeError("No se pudo capturar la imagen de la cámara")
        self.camera.save_frame(frame, "capture.png")

        if not self.calibrator.process_image("capture.png"):
            raise RuntimeError("No se pudieron detectar las esquinas del tablero")

        # Generar rangos del tablero
        self.board_range = self.board_mapper.generate_board_range(
            self.calibrator.coord2D[-1]
        )

        # Diccionario para dwell time de cada celda
        self.selector.init_time_in_position(self.board_range)

        # Diccionario de posiciones de Pygame
        self.game_board = generate_game_board_dict(SQUARE_SIZE)

    def run(self):
        clock = pygame.time.Clock()
        run = True

        while run:
            clock.tick(FPS)

            # Verificar ganador
            if self.game.winner() is not None:
                print("Ganador:", self.game.winner())
                run = False
                break

            # Manejo de eventos Pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break

            # Captura frame
            frame = self.camera.capture_frame()
            if frame is None:
                continue

            # Procesamiento de frame para detección de color
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_green = np.array([40, 40, 40])
            upper_green = np.array([80, 255, 255])
            mask = cv2.inRange(hsv, lower_green, upper_green)

            # Encontrar centroides de contornos
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            centroids = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:
                    M = cv2.moments(contour)
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    centroids.append((cx, cy))
                    if self.debug:
                        cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

            # Actualizar selector con los centroides
            activated_cells = self.selector.update_positions(centroids, self.board_range, FPS)

            # Ejecutar selección en el juego
            for key in activated_cells:
                pos = self.game_board[key]
                row, col = int(pos[1]) // SQUARE_SIZE, int(pos[0]) // SQUARE_SIZE
                self.game.select(row, col)

            # Renderizado de debug
            if self.debug:
                cv2.imshow("Object Tracking", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    run = False

            # Actualizar Pygame
            self.game.update()

        pygame.quit()
        self.camera.release()
        cv2.destroyAllWindows()
