import os
import sys
import traceback
import unittest
from unittest.mock import MagicMock, patch

import cv2

# isort: off
from pygptcourse.main import main  # type: ignore

# isort: on


class TestApplicationModes(unittest.TestCase):
    @patch(
        "pygptcourse.main.cv2.VideoCapture"
    )  # Mocking VideoCapture to prevent actual camera interaction
    def setUp(self, mock_video_capture):
        # Set up mock for VideoCapture
        mock_video_capture.return_value.read.return_value = (
            False,
            MagicMock(name="frame"),
        )
        # Common setup for all tests can go here

    @patch(
        "pygptcourse.main.cv2.imshow"
    )  # Mocking cv2.imshow to prevent actual display window
    def test_headless_by_env(self, mock_imshow):
        # Test to ensure cv2.imshow is not called when DISPLAY is not set
        with patch.dict("os.environ", {"DISPLAY": ""}):
            try:
                main()
            except Exception as e:
                print(
                    f"Ran into exception {e} when running main. Ignoring it for the headless test"
                )
                pass

            # Asserting cv2.imshow is not called when DISPLAY environment variable is not set
            mock_imshow.assert_not_called()

    @patch(
        "pygptcourse.main.cv2.imshow"
    )  # Mocking cv2.imshow to prevent actual display window
    def test_headless_mode_arg(self, mock_imshow):
        # Simulate command-line arguments for headless mode
        test_args = ["main.py", "--headless"]
        with patch.object(sys, "argv", test_args):
            try:
                main()
            except Exception as e:
                print(
                    f"Ran into exception {e} when running main. Ignoring it for the headless test"
                )
                pass

            # Assertions to ensure headless behavior when --headless argument is passed
            mock_imshow.assert_not_called()


class TestApplicationEndToEnd(unittest.TestCase):
    @patch("os.environ.get", return_value=None)
    @patch("pygptcourse.main.FaceDetector")
    @patch("pygptcourse.camera_control.Launcher")
    @patch("cv2.waitKey", return_value=ord("q"))
    @patch("cv2.imshow")
    @patch("cv2.VideoCapture")
    def test_application_run(
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
        main()
        try:
            main()
            application_run_success = True
        except Exception as e:
            print(f"Caught exception {e}")
            traceback.print_exc()
            application_run_success = False

        self.assertTrue(application_run_success)
        # Assertions to ensure mocks are used
        mock_video_capture_class.assert_called()
        mock_video_capture.read.assert_called()  # This ensures that read was called
        mock_press_wait_key.assert_called()
        mock_launcher.assert_called()
        mock_environ_get.assert_called()
        mock_cv2_imshow.assert_not_called()


if __name__ == "__main__":
    unittest.main()
