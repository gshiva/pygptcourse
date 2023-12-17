import cv2

from pygptcourse.camera_control import CameraControl
from pygptcourse.camera_manager import CameraManager
from pygptcourse.face_detector import FaceDetector

# Initialize FaceDetector with a dictionary of known faces
face_detector = FaceDetector({"Shiva": "shiva_face.jpg", "Adil": "adil_face.jpg"})

# Initialize CameraControl and CameraManager
camera_control = CameraControl(simulation_mode=False)
camera_manager = CameraManager()

counter = 0
face_names = []

center_x = 0
center_y = 0

face_center_x = 0
face_center_y = 0

fire_count = 0

# Set the total time for moving from left to right and top to bottom
TOTAL_TIME_LR = 26
TOTAL_TIME_TB = 4

# Set the image resolution
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

# Set the initial position of the camera
current_camera_position = [TOTAL_TIME_LR, TOTAL_TIME_TB]
current_image_position = [IMAGE_WIDTH, IMAGE_HEIGHT]

# camera movement time increment
TIME_INCREMENT = 0.1
camera_control.move_camera_to_center()

video_capture = camera_manager.start()

try:
    while True:
        ret, image = video_capture.read()

        if not ret:
            break

        # Reduce face size to make calculations easier
        small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)

        # to save cpu, only do calculations once every 10 frames
        if counter % 3 == 0:
            face_locations, face_names = face_detector.detect_faces(small_frame)

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Because we made the image smaller, now need to multiply by 4 to get correct size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
            face_center = [(left + right) // 2, (top + bottom) // 2]

            face_name = name
            name = (
                name
                + " center:"
                + str(face_center)
                + " r:"
                + str(right)
                + ", b:"
                + str(bottom)
                + ", l:"
                + str(left)
                + ", t:"
                + str(top)
            )

            print(
                f"Name: {name}, drawing a label with coordinates: ({left}, {bottom - 35}), ({right}, {bottom})"
            )

            # Draw a label with a name below the face
            cv2.rectangle(
                image, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED
            )
            cv2.putText(
                image,
                name,
                (left + 6, bottom - 6),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (255, 255, 255),
                1,
            )

            face_bbox = [top, right, bottom, left]

            # Calculate the center of the face bounding box
            # The face_recognition library returns the bounding box of a face in an image as a tuple of
            # four values (top, right, bottom, left).
            # The following code calculates the center of the bounding box by taking the average of the
            # left and right values and
            # the average of the top and bottom values. This is done by adding the
            # right and left values and dividing by 2
            # to get the x-coordinate of the center, and adding the top and bottom values
            # and dividing by 2 to get the y-coordinate
            # of the center. The result is a list containing the x and y coordinates of the center of the bounding box.

            face_center = [
                (face_bbox[1] + face_bbox[3]) // 2,
                (face_bbox[0] + face_bbox[2]) // 2,
            ]

            camera_control.launch_if_aligned(face_center)

        cv2.imshow("Video", image)
        counter += 1
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
except Exception as e:
    print(f"Caught exception {e}")
finally:
    camera_manager.stop()
    camera_control.stop()
