import argparse
import logging
import os
import traceback

import cv2  # type: ignore

# isort: off
from pygptcourse.camera_control import CameraControl
from pygptcourse.camera_manager import CameraManager
from pygptcourse.face_detector import FaceDetector
from pygptcourse.file_system_image_loader import FileSystemImageLoader
from pygptcourse.otel_decorators import otel_handler

# isort: on

logger = logging.getLogger(__name__)


# the above is required because the local isort adds a new line while default GHA (Github Actions)
# adds a new line
@otel_handler.trace
def detect_faces(face_detector, frame):
    return face_detector.detect_faces(frame)


def is_display_available():
    return "DISPLAY" in os.environ


@otel_handler.trace
def main():
    parser = argparse.ArgumentParser(description="Run the camera control system.")
    parser.add_argument(
        "--simulate", action="store_true", help="Run in simulation mode."
    )
    parser.add_argument("--headless", action="store_true", help="Run in headless mode.")
    args, unknown = parser.parse_known_args()
    logger.warning(f"Warning: {unknown} arguments passed")

    headless_mode = args.headless
    # if DISPLAY is not set then force headless mode
    if not is_display_available():
        logger.warning(
            f"Running where DISPLAY is not set. Forcing headless mode. Original headless mode: {headless_mode}"
        )
        headless_mode = True

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
    logger.info("Initializing CameraControl")
    camera_control = CameraControl(simulation_mode=args.simulate)
    logger.info("Initializing CameraManager")
    camera_manager = CameraManager()

    counter = 0
    face_names = []

    try:
        logger.info("Moving launcher to the center")
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
                face_locations, face_names = detect_faces(face_detector, small_frame)

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

                logger.info(
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

            if not headless_mode:
                # Note that if DISPLAY is not set or if OpenCV is not able to display the image
                # it just Aborts. It aborts with this error
                # qt.qpa.xcb: could not connect to display
                # qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in
                # "/root/.cache/pypoetry/virtualenvs/...py3.11/lib/python3.11/site-packages/cv2/qt/plugins"
                # even though it was found.
                # This application failed to start because no Qt platform plugin could be initialized.
                # Reinstalling the application may fix this problem.

                # Available platform plugins are: xcb.

                # Fatal Python error: Aborted

                # Thread 0x00007f5104a82700 (most recent call first):
                # File "/usr/local/lib/python3.11/selectors.py", line 415 in select
                # File "/usr/local/lib/python3.11/socketserver.py", line 233 in serve_forever
                # File "/usr/local/lib/python3.11/threading.py", line 982 in run
                # File "/usr/local/lib/python3.11/threading.py", line 1045 in _bootstrap_inner
                # File "/usr/local/lib/python3.11/threading.py", line 1002 in _bootstrap

                # Current thread 0x00007f511c95d740 (most recent call first):
                # File "/workspaces/pygptcourse/src/pygptcourse/main.py", line 172 in main
                # File "/workspaces/pygptcourse/src/pygptcourse/main.py", line 193 in <module>

                # Extension modules: numpy.core._multiarray_umath, numpy.core._multiarray_tests,
                # numpy.linalg._umath_linalg, numpy.fft._pocketfft_internal, numpy.random._common,
                # numpy.random.bit_generator, numpy.random._bounded_integers, numpy.random._mt19937,
                # numpy.random.mtrand, numpy.random._philox, numpy.random._pcg64,
                # numpy.random._sfc64, numpy.random._generator, PIL._imaging (total: 14)
                # Aborted (core dumped)
                # This cannot be handled using signal handlers as SIGABRT cannot be handled by python signal handlers
                # The way around it is to fork a child process for this and handle the signal there.
                # Please see:
                # https://discuss.python.org/t/how-can-i-handle-sigabrt-from-third-party-c-code-std-abort-call/22078/4
                # For now hacking it by checking DISPLAY env variable and not calling cv2.imshow function
                try:
                    cv2.imshow("Video", image)
                except Exception as e:
                    logger.error(
                        f"Unable to show image due to {e} and headless mode not set. \
                          Forcefully setting the mode to headless"
                    )
                    headless_mode = True

            counter += 1
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    except Exception as e:
        logger.error(f"Caught exception {e}")
        traceback.print_exc()
    finally:
        camera_manager.stop()
        camera_control.stop()


if __name__ == "__main__":
    main()
