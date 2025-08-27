import pygame
import cv2
import numpy as np
from core.constants import SQUARE_SIZE, FPS
from core.game import Game

from services.camera import CameraCapture
from services.calibrator import Calibrator
from services.board_mapper import BoardMapper
from services.selector import Selector
from ui.pygame_ui import init_pygame_window
from services.utils.board_utils import generate_game_board_dict

class GameController:
    def __init__(self, device_index=0, debug=True):
        self.debug = debug
        self.win = init_pygame_window()
        self.camera = CameraCapture(device_index=device_index)
        self.calibrator = Calibrator()
        self.board_mapper = BoardMapper()
        self.selector = Selector()
        self.game = Game(self.win)

        # Initial capture and board calibration
        frame = self.camera.capture_frame()
        if frame is None:
            raise RuntimeError("Could not capture camera image")
        self.camera.save_frame(frame, "capture.png")

        if not self.calibrator.process_image("capture.png"):
            raise RuntimeError("Could not detect board corners")

        # Generate board ranges
        self.board_range = self.board_mapper.generate_board_range(
            self.calibrator.coord2D[-1]
        )

        # Dict for dwell time per cell
        self.selector.init_time_in_position(self.board_range)

        # Dict for Pygame positions
        self.game_board = generate_game_board_dict(SQUARE_SIZE)

    def run(self):
        clock = pygame.time.Clock()
        run = True

        while run:
            clock.tick(FPS)

            # Check winner
            if self.game.winner() is not None:
                print("Winner:", self.game.winner())
                run = False
                break

            # Pygame events handler
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break

            # Frame capture
            frame = self.camera.capture_frame()
            if frame is None:
                continue

            # Frame processing for color detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_green = np.array([40, 40, 40])
            upper_green = np.array([80, 255, 255])
            mask = cv2.inRange(hsv, lower_green, upper_green)

            # Finding centroids of contours
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

            # Update selector with centroids
            activated_cells = self.selector.update_positions(centroids, self.board_range, FPS)

            # Execute selection in game 
            for key in activated_cells:
                pos = self.game_board[key]
                row, col = int(pos[1]) // SQUARE_SIZE, int(pos[0]) // SQUARE_SIZE
                self.game.select(row, col)

            # Debug rendering
            if self.debug:
                cv2.imshow("Object Tracking", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    run = False

            # Actualizar Pygame
            self.game.update()

        pygame.quit()
        self.camera.release()
        cv2.destroyAllWindows()
