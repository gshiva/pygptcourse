import unittest
from unittest.mock import patch

# isort: off

from pygptcourse.main import main  # type: ignore

# isort: on


class TestMain(unittest.TestCase):
    @patch("os.environ.get", return_value=None)
    @patch(
        "pygptcourse.main.FaceDetector.load_and_encode_faces",
        return_value={"Shiva": "mock_encoding", "Adil": "mock_encoding"},
    )
    @patch("pygptcourse.camera_control.Launcher")
    @patch("cv2.waitKey", return_value=ord("q"))
    def test_main_default_image_dir(
        self,
        mock_press_wait_key,
        mock_launcher,
        mock_encode_faces,
        mock_environ_get,
    ):
        # Test main function with default image directory (CWD)

        # Execute the main function
        main()

        # Assertions to ensure mocks are used
        mock_press_wait_key.assert_called()
        mock_launcher.assert_called()
        mock_encode_faces.assert_called()
        mock_environ_get.assert_called()


if __name__ == "__main__":
    unittest.main()
