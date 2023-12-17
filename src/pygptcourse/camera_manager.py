import cv2


class CameraManager:
    def __init__(self, resolution=(640, 480)):
        self.video_capture = cv2.VideoCapture(0)
        self.video_capture.set(3, resolution[0])  # Horizontal resolution
        self.video_capture.set(4, resolution[1])  # Vertical resolution

    def start(self):
        # Additional logic for starting the camera can be added here
        return self.video_capture

    def stop(self):
        # Stop and release the video capture
        self.video_capture.release()
        cv2.destroyAllWindows()  # Close all OpenCV windows
