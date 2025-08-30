import cv2
import numpy as np
from pathlib import Path

TEMP_DIR = Path(__file__).resolve().parent.parent / "temp"

class Calibrator:
    def __init__(self, chessboard_size=(7,7)):
        self.chessboard_size = chessboard_size
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.objp = np.zeros((chessboard_size[0]*chessboard_size[1],3), np.float32)
        self.objp[:,:2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1,2)
        self.coord2D = []
        self.coord3D = []

    def process_image(self, filepath: str) -> bool:
        path = Path(TEMP_DIR / filepath)
        img = cv2.imread(str(path))
        if img is None:
            return False
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size, None)
        if not ret:
            return False
        
        corners_opt = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), self.criteria)
        self.coord2D.append(corners_opt)
        self.coord3D.append(self.objp.copy())

        # Draw corners (Optional for debugging)
        img_drawn = cv2.drawChessboardCorners(img, self.chessboard_size, corners_opt, ret)
        cv2.namedWindow('calibration', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('calibration', 800, 600)
        cv2.imshow('calibration', img_drawn)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return True

    def get_last_four_points(self) -> np.ndarray:
        if not self.coord2D:
            return np.array([])
        corners_opt = self.coord2D[-1]
        points = corners_opt[-4:]
        points = np.concatenate((points, corners_opt[-11:-7]), axis=0)
        return points

