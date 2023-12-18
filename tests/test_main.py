import unittest
from unittest.mock import MagicMock, patch

from PIL import Image  # type: ignore

from pygptcourse.main import main  # type: ignore


class TestMain(unittest.TestCase):
    @patch(
        "face_recognition.load_image_file", return_value=Image.new("RGB", (100, 100))
    )
    @patch("main.FileSystemImageLoader.get_full_image_path", return_value=MagicMock())
    @patch("os.environ.get", return_value=None)
    @patch(
        "main.FaceDetector.load_and_encode_faces",
        return_value={"Shiva": "mock_encoding", "Adil": "mock_encoding"},
    )
    @patch("pygptcourse.camera_control.CameraControl")
    @patch("pygptcourse.camera_control.Launcher")  # Adjusted path
    @patch("pygptcourse.camera_control.SimulatedLauncher")  # Adjusted path
    @patch("cv2.waitKey", return_value=ord("q"))
    def test_main_default_image_dir(
        self,
        mock_press_wait_key,
        mock_simulated_launcher,
        mock_launcher,
        mock_camera_control,
        mock_encode_faces,
        mock_environ_get,
        mock_file_system_loader,
        mock_face_recognition,
    ):
        # Test main function with default image directory (CWD)

        # Execute the main function
        main()

        # Assertions to ensure mocks are used
        mock_encode_faces.assert_called()
        mock_launcher.assert_called()


if __name__ == "__main__":
    unittest.main()
