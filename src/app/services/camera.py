import cv2
import os
import numpy as np
from pathlib import Path

class CameraCapture:
    def __init__(self, device_index=0):
        self.cap = cv2.VideoCapture(device_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera with index {device_index}")

    def capture_frame(self) -> "np.ndarray | None":
        ret, frame = self.cap.read()
        return frame if ret else None

    def save_frame(self, frame, filename: str):
        output_dir = Path(__file__).resolve().parent.parent / "temp"
        output_dir.mkdir(exist_ok=True)

        path = output_dir / filename
        cv2.imwrite(str(path), frame)
        print(f"Image captured and saved as {path}")

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
