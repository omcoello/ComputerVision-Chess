from typing import Dict
import numpy as np
import cv2

SquareRange = Dict[str, np.ndarray]

class BoardMapper:
    def __init__(self):
        self.board_range: SquareRange = {}

    @staticmethod
    def calculate_upper_lower_corners(points: np.ndarray, upper=True) -> np.ndarray:
        # Aquí puedes mantener la lógica trigonométrica por ahora
        final_points = []
        for i in range(1, 7):
            data = points[i][0] - points[i-1][0]
            arg = data[1]/data[0]            
            radians = np.arccos(arg) if -1 <= arg <= 1 else np.arctan(arg)
            yLength = np.cos(radians)*data[0] if -1 <= arg <= 1 else np.cos(radians)*data[1]
            xLength = np.sin(radians)*data[0] if -1 <= arg <= 1 else np.sin(radians)*data[1]

            if upper:
                if i == 1:
                    final_points.append([-xLength + (yLength + points[i-1][0][0]), -yLength + (-xLength + points[i-1][0][1])])
                    final_points.append([yLength + points[i-1][0][0], -xLength + points[i-1][0][1]])
                final_points.append([yLength + points[i][0][0], -xLength + points[i][0][1]])
                if i == 6:
                    final_points.append([xLength + (yLength + points[i][0][0]), yLength + (-xLength + points[i][0][1])])
            else:
                if i == 1:
                    final_points.append([-xLength + (yLength + points[i-1][0][0]), yLength + (xLength + points[i-1][0][1])])
                    final_points.append([yLength + points[i-1][0][0], xLength + points[i-1][0][1]])
                final_points.append([yLength + points[i][0][0], xLength + points[i][0][1]])
                if i == 6:
                    final_points.append([xLength + (yLength + points[i][0][0]), -yLength + (xLength + points[i][0][1])])
        return np.array(final_points, dtype=int)

    def add_data(self, data: np.ndarray, counter: int, times: int):
        for i in range(-8, -1):
            key = f"s{counter}"
            if key not in self.board_range:
                self.board_range[key] = [data[i-1], data[i]]
            else:
                self.board_range[key].append(data[i])
                self.board_range[key].append(data[i+1])
                self.board_range[key] = np.array(self.board_range[key])
            counter += 1

    def generate_board_range(self, corners: np.ndarray):
        # Divide los puntos y llena board_range
        i = 7
        data = self.calculate_upper_lower_corners(corners[:i])
        self.add_data(data, 0, 1)

        slices = [(i, i+7), (i+7, i+14), (i+14, i+21), (i+21, i+28), (i+28, i+35)]
        start_counter = 0
        for s in slices:
            data = self.calculate_upper_lower_corners(corners[s[0]:s[1]])
            self.add_data(data, start_counter, 2)
            start_counter += 8

        # Últimos dos bloques inferiores
        data = self.calculate_upper_lower_corners(corners[28:], upper=False)
        self.add_data(data, 48, 2)
        data = self.calculate_upper_lower_corners(corners[35:], upper=False)
        self.add_data(data, 56, 1)

        return self.board_range

    @staticmethod
    def draw_points(img, points: np.ndarray, color=(0,0,255), radius=3):
        for p in points:
            cv2.circle(img, tuple(p), radius=radius, color=color, thickness=-1)