from typing import Dict
import numpy as np
import cv2

SquareRange = Dict[str, np.ndarray]

class BoardMapper:
    def __init__(self):
        self.board_range: SquareRange = {}

    @staticmethod
    def calculate_upper_lower_corners(points: np.ndarray, upper=True) -> np.ndarray:
        final_points = []
        for i in range(1, 7):
            data = points[i][0] - points[i-1][0]
            arg = data[1]/data[0]
            radians = np.arccos(arg) if -1 <= arg <= 1 else np.arctan(arg)

            if upper:
                yLength = np.cos(radians)*data[0] if -1 <= arg <= 1 else np.cos(radians)*data[1]
                xLength = np.sin(radians)*data[0] if -1 <= arg <= 1 else np.sin(radians)*data[1]
            else:
                yLength = np.cos(np.pi - radians)*data[0] if -1 <= arg <= 1 else np.cos(np.pi - radians)*data[1]
                xLength = np.sin(np.pi - radians)*data[0] if -1 <= arg <= 1 else np.sin(np.pi - radians)*data[1]

            if upper:
                if i == 1:
                    print("Calculating initial left point...")
                    print(f"data: {data}")
                    print(f"yLength: {xLength}")
                    print(f"xLength: {yLength}")
                    print(f"points reference: {points[i]}")
                    print(f"points[0] reference: {points[i][0]}")
                    print(f"data to add as first point: {[-xLength + (yLength + points[i-1][0][0]), -yLength + (-xLength + points[i-1][0][1])]}")
                    print(f"data to add as second point: {[yLength + points[i-1][0][0], -xLength + points[i-1][0][1]]}")
                    final_points.append([-xLength + (yLength + points[i-1][0][0]),
                                        -yLength + (-xLength + points[i-1][0][1])])
                    final_points.append([yLength + points[i-1][0][0], -xLength + points[i-1][0][1]])
                final_points.append([yLength + points[i][0][0], -xLength + points[i][0][1]])
                if i == 6:
                    final_points.append([xLength + (yLength + points[i][0][0]),
                                        yLength + (-xLength + points[i][0][1])])
            else:
                if i == 1:
                    final_points.append([-xLength + (yLength + points[i-1][0][0]),
                                        yLength + (xLength + points[i-1][0][1])])
                    final_points.append([yLength + points[i-1][0][0], xLength + points[i-1][0][1]])
                final_points.append([yLength + points[i][0][0], xLength + points[i][0][1]])
                if i == 6:
                    final_points.append([xLength + (yLength + points[i][0][0]),
                                        -yLength + (xLength + points[i][0][1])])
        return np.array(final_points, dtype=int)


    def add_data(self, data: np.ndarray, counter: int, times: int):
        for i in range(-8, -1):
            key = f"s{counter}"
            if key not in self.board_range:
                if i == -8:
                    self.board_range[key] = [data[i-1], data[i]]
                    if times == 2:
                        # duplicamos hacia abajo
                        self.board_range[f"s{counter+8}"] = [data[i-1], data[i]]
                    counter += 1
                key = f"s{counter}"
                self.board_range[key] = [data[i], data[i+1]]
                if times == 2:
                    self.board_range[f"s{counter+8}"] = [data[i], data[i+1]]
            else:
                if i == -8:
                    self.board_range[key].append(data[i-1])
                    self.board_range[key].append(data[i])
                    if times == 2:
                        self.board_range[f"s{counter+8}"] = [data[i-1], data[i]]
                    counter += 1
                key = f"s{counter}"
                self.board_range[key].append(data[i])
                self.board_range[key].append(data[i+1])
                if times == 2:
                    self.board_range[f"s{counter+8}"] = [data[i], data[i+1]]
                self.board_range[key] = np.array(self.board_range[key])
            counter += 1


    def generate_board_range(self, corners: np.ndarray):
        # Divide the points and fill board_range
        i = 7
        data = self.calculate_upper_lower_corners(corners[:i])
        self.add_data(data, 0, 1)

        data = np.concatenate((data, self.calculate_upper_lower_corners(corners[i:])), axis=0)
        self.add_data(data, 0, 2)

        data = np.concatenate((data, self.calculate_upper_lower_corners(corners[i+7:])), axis=0)
        self.add_data(data, 8, 2)

        data = np.concatenate((data, self.calculate_upper_lower_corners(corners[i+14:])), axis=0)
        self.add_data(data, 16, 2)

        data = np.concatenate((data, self.calculate_upper_lower_corners(corners[i+21:])), axis=0)
        self.add_data(data, 24, 2)

        data = np.concatenate((data, self.calculate_upper_lower_corners(corners[i+28:])), axis=0)
        self.add_data(data, 32, 2)

        data = np.concatenate((data, self.calculate_upper_lower_corners(corners[i+35:])), axis=0)
        self.add_data(data, 40, 2)

        data = np.concatenate((data, self.calculate_upper_lower_corners(corners[i+28:], upper=False)), axis=0)
        self.add_data(data, 48, 2)

        data = np.concatenate((data, self.calculate_upper_lower_corners(corners[i+35:], upper=False)), axis=0)
        self.add_data(data, 56, 1)

        print("This is the board generated", self.board_range)
        return self.board_range


    @staticmethod
    def draw_points(img, points: np.ndarray, color=(0,0,255), radius=3):
        for p in points:
            cv2.circle(img, tuple(p), radius=radius, color=color, thickness=-1)