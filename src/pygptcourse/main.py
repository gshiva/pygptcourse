import argparse
import os
import traceback

import cv2  # type: ignore

# isort: off
from prometheus_client import Summary, start_http_server

from pygptcourse.camera_control import CameraControl
from pygptcourse.camera_manager import CameraManager
from pygptcourse.face_detector import FaceDetector
from pygptcourse.file_system_image_loader import FileSystemImageLoader

# isort: on

# the above is required because the local isort adds a new line while default GHA (Github Actions)
# adds a new line
# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary("face_detection_seconds", "Time spent detecting faces")


@REQUEST_TIME.time()
def detect_faces(face_detector, frame):
    return face_detector.detect_faces(frame)


def main():
    parser = argparse.ArgumentParser(description="Run the camera control system.")
    parser.add_argument(
        "--simulate", action="store_true", help="Run in simulation mode."
    )
    args, unknown = parser.parse_known_args()

    print(f"Warning: {unknown} arguments passed")

    # Retrieve environment variable or default to where this script is located
    image_dir = os.environ.get(
        "FACE_IMAGE_DIR", os.path.dirname(os.path.abspath(__file__))
    )

    # Initialize the image loader with the directory
    image_loader = FileSystemImageLoader(base_dir=image_dir)

    # Initialize FaceDetector with a dictionary of known faces
    face_images = {"Shiva": "shiva_face.jpg", "Adil": "adil_face.jpg"}
    face_detector = FaceDetector(face_images, image_loader)

    # Initialize CameraControl and CameraManager
    print("Initializing CameraControl")
    camera_control = CameraControl(simulation_mode=args.simulate)
    print("Initializing CameraManager")
    camera_manager = CameraManager()

    counter = 0
    face_names = []

    try:
        print("Moving launcher to the center")
        camera_control.start()
        camera_control.move_camera_to_center()

        video_capture = camera_manager.start()

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
                    face_name
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
                # of the center. The result is a list containing the x and y coordinates of the
                # center of the bounding box.

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
        traceback.print_exc()
    finally:
        camera_manager.stop()
        camera_control.stop()


if __name__ == "__main__":
    # Start up the server to expose the metrics.
    start_http_server(8000)
    main()
