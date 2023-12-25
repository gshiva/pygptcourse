import unittest
from unittest.mock import patch

from pygptcourse.camera_control import CameraControl  # type: ignore


class TestCameraControlIntegration(unittest.TestCase):
    @patch("pygptcourse.camera_control.CameraControl.move_camera")
    def test_face_movement_triggers_camera_right(self, mock_move_camera):
        # Creating an instance of CameraControl
        camera_control = CameraControl(simulation_mode=True)

        # Mocking the behavior of face detection to simulate face movement
        # Assuming face_center returns (x, y) coordinates of the face
        face_center_moved_right = (
            CameraControl.IMAGE_WIDTH / 2 + 100,
            CameraControl.IMAGE_HEIGHT / 2,
        )  # Simulate face moving right

        # Triggering the method that checks and moves the camera based on face position
        camera_control.check_and_move_camera(face_center_moved_right)

        # Asserting that move_camera was called with the RIGHT direction as a result of the face movement to the right
        mock_move_camera.assert_called_with("RIGHT", CameraControl.TIME_INCREMENT)


if __name__ == "__main__":
    unittest.main()
