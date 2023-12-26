import os
import unittest
from unittest.mock import MagicMock

import cv2

# isort: off

from pygptcourse.face_detector import FaceDetector  # type: ignore

# isort: on


class TestFaceDetector(unittest.TestCase):
    def setUp(self):
        self.image_loader = MagicMock()
        base_dir = os.path.dirname(__file__)  # Directory of this script (test_main.py)
        resources_dir = os.path.join(
            base_dir, "resources"
        )  # Path to the resources folder
        dummy_frame_path = os.path.join(
            resources_dir, "shiva_init_face.jpg"
        )  # Path to the initial image
        dummy_frame = cv2.imread(dummy_frame_path)  # Load the image as a numpy array
        if dummy_frame is None:
            raise FileNotFoundError(f"Test image not found: {dummy_frame_path}")

        self.image_loader.get_full_image_path.return_value = dummy_frame_path
        self.mock_face_images = {"shiva": dummy_frame_path}

    def test_load_and_encode_faces(self):
        face_detector = FaceDetector(self.mock_face_images, self.image_loader)
        encoded_faces = face_detector.load_and_encode_faces(self.mock_face_images)
        self.assertIn("shiva", encoded_faces)


if __name__ == "__main__":
    unittest.main()
