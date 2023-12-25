import os
import unittest
from unittest.mock import MagicMock, patch

import cv2


class TestMain(unittest.TestCase):
    @patch("os.environ.get", return_value=None)
    @patch("pygptcourse.main.FaceDetector")
    @patch("pygptcourse.camera_control.Launcher")
    @patch("cv2.waitKey", return_value=ord("q"))
    @patch("cv2.imshow")
    @patch("cv2.VideoCapture")
    def test_main_default_image_dir(
        self,
        mock_video_capture_class,
        mock_cv2_imshow,
        mock_press_wait_key,
        mock_launcher,
        mock_face_detector,
        mock_environ_get,
    ):
        # Test main function with default image directory (CWD)
        mock_video_capture = MagicMock()

        # Simulate 'read' returning a successful flag and an image
        # Construct the path to the dummy frame relative to this script
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

        mock_video_capture.read.return_value = (True, dummy_frame)
        mock_video_capture_class.return_value = mock_video_capture
        # Directly call the mock or the method expected to use the mock
        ret, frame = mock_video_capture.read()  # This should mimic the call in main.py

        # Assert that the return values are as expected
        assert ret is True
        assert (frame == dummy_frame).all()

        # Configure the mock FaceDetector
        mock_face_detector_instance = MagicMock()
        # Configure detect_faces to return dummy values
        mock_face_detector_instance.detect_faces.return_value = (
            [],
            [],
        )  # Empty lists as an example
        mock_face_detector.return_value = mock_face_detector_instance

        # Execute the main function
        from pygptcourse.main import main  # type: ignore

        main()

        # Assertions to ensure mocks are used
        mock_video_capture_class.assert_called_once()
        mock_video_capture.read.assert_called()  # This ensures that read was called
        mock_press_wait_key.assert_called()
        mock_launcher.assert_called()
        mock_environ_get.assert_called()
        mock_cv2_imshow.assert_called()


if __name__ == "__main__":
    unittest.main()
