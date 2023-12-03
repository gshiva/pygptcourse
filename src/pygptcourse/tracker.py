import cv2
import face_recognition

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

shiva_image = face_recognition.load_image_file("shiva_face.jpg")
shiva_face_encoding = face_recognition.face_encodings(shiva_image)[0]

adil_image = face_recognition.load_image_file("adil_face.jpg")
adil_face_encoding = face_recognition.face_encodings(adil_image)[0]

video_capture = cv2.VideoCapture(0)
video_capture.set(3, 640)  # Set horizontal resolution
video_capture.set(4, 480)  # Set vertical resolution

counter = 0
face_names = []

def move_camera_to_center():
    global current_camera_position
    print("Moving camera to center")
    # in our camera coordinate system,  in alignment with image coordinate system
    # See https://pyimagesearch.com/2021/01/20/opencv-getting-and-setting-pixels/
    # top left is 0,0 and top right is TOTAL_TIME_TB, 0
    # bottom left is 0,TOTAL_TIME_TB and bottom right is TOTAL_TIME_TB, TOTAL_TIME_TB
    # first move it to bottom left (0,TOTAL_TIME_TB)
    move_camera("LEFT", TOTAL_TIME_LR)
    move_camera("DOWN", TOTAL_TIME_TB)

    # set the current position to the known bottom left position
    current_camera_position = [0,TOTAL_TIME_TB]

    # we are sure that the camera is on the bottom left
    # now move it to the center (13,2)
    move_camera("RIGHT", TOTAL_TIME_LR/2)
    move_camera("UP", TOTAL_TIME_TB/2)

counter = 0

def detect_faces():
    global counter
    face_locations = []
    face_encodings  = []

    ret, image = video_capture.read()
    print(f"Video captured")

    if not ret:
        return []

    # Reduce face size to make calculations easier
    small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)

    # to save cpu, only do calculations once every 10 frames
    if counter % 3 == 0:
        face_locations = face_recognition.face_locations(small_frame)
        face_encodings = face_recognition.face_encodings(small_frame, face_locations)

        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            match = face_recognition.compare_faces([shiva_face_encoding, adil_face_encoding], face_encoding)
            name = "Unknown"

            if match[0]:
                name = "shiva"
            elif match[1]:
                name = "adil"

            face_names.append(name)
    print(f"Face names: {face_names}")
    cv2.imshow('Video', image)

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Because we made the image smaller, now need to multiply by 4 to get correct size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
        cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)

        name = name + ": r:" + str(right) + ", b:" + str(bottom) + ", l:" + str(left) + ", t:" + str(top)
        print(f"Name: {name}")

        # Draw a label with a name below the face
        cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        cv2.putText(image, name, (left + 6, bottom - 6),  cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 1)


        cv2.imshow('Video', image)
        counter += 1

        return [[top, right, bottom, left]]


def move_camera(direction, duration):
    global current_camera_position

    prev_current_camera_position = current_camera_position.copy()
    print(f"Previous camera position: {prev_current_camera_position}")

    # Update the current position based on the direction
    if direction == "LEFT":
        current_camera_position[0] -= duration
    elif direction == "RIGHT":
        current_camera_position[0] += duration
    elif direction == "UP":
        current_camera_position[1] -= duration
    elif direction == "DOWN":
        current_camera_position[1] += duration

    # Make sure the current position is within the image bounds
    # Explanation from ChatGPT
    # These lines of code ensure that the current position of the camera is within the bounds of the image.
    # The current_camera_position variable is a list that stores the x and y coordinates of the current position of the camera.
    # The first line of code sets the x coordinate of current_camera_position to be within the range [0, TOTAL_TIME_LR],
    # and the second line sets the y coordinate to be within the range [0, TOTAL_TIME_LR].
    # The max and min functions are used to achieve this.
    # The min function takes two arguments and returns the smaller of the two.
    # In this case, it is used to ensure that the x and y coordinates of current_camera_position
    # do not exceed TOTAL_TIME_LR and TOTAL_TIME_LR, respectively.
    # The max function takes two arguments and returns the larger of the two.
    # In this case, it is used to ensure that the x and y coordinates of current_camera_position do not fall below 0.
    # For example, if current_camera_position[0] is greater than TOTAL_TIME_LR,
    # then min(current_camera_position[0], TOTAL_TIME_LR) will return TOTAL_TIME_LR, ensuring that the x coordinate of current_camera_position
    # does not exceed the camera left to right limits. Similarly, if current_camera_position[1] is less than 0, then
    # max(0, current_camera_position[1]) will return 0, ensuring that the y coordinate of current_camera_position does not fall below 0.

    current_camera_position[0] = max(0, min(current_camera_position[0], TOTAL_TIME_LR))
    current_camera_position[1] = max(0, min(current_camera_position[1], TOTAL_TIME_TB))

    print(f"Previous position: {prev_current_camera_position} Calculated current position: {current_camera_position}, Direction: {direction}, Duration: {duration}")

    if prev_current_camera_position == current_camera_position:
        # nothing to do
        print(f"Nothing to do. Current position: {current_camera_position} is same as previous position {prev_current_camera_position}.")
        return
    print(f"Moving to position: {current_camera_position}, Direction: {direction}, Duration: {duration}")
    # TODO: issue usb move command


def track_face():
    global current_camera_position

    # Detect faces in the frame using OpenCV (this code is just an example and needs to be updated with your own face detection code)
    faces = detect_faces()

    # If a face was detected, track it using the track_face function
    if faces and len(faces) > 0:
        face_bbox = faces[0]

        # Calculate the center of the face bounding box
        # The face_recognition library returns the bounding box of a face in an image as a tuple of four values (top, right, bottom, left).
        # The following code calculates the center of the bounding box by taking the average of the left and right values and
        # the average of the top and bottom values. This is done by adding the right and left values and dividing by 2
        # to get the x-coordinate of the center, and adding the top and bottom values and dividing by 2 to get the y-coordinate
        # of the center. The result is a list containing the x and y coordinates of the center of the bounding box.

        face_center = [(face_bbox[1] + face_bbox[3]) // 2, (face_bbox[0] + face_bbox[2]) // 2]

        # Calculate the distance from the face center to the image center
        dx = face_center[0] - (IMAGE_WIDTH/2)
        dy = face_center[1] - (IMAGE_HEIGHT/2)

        # emprical calculations which came to 120 pixels both along the height and width
        # from the center of the image
        # That is 60 pixels in either direction
        # to keep it more image resolution friendly using 5:4 aspect ratio
        # based on more feedback with different resolutions this can be improved upon.
        # CENTERX_MIN = round((IMAGE_WIDTH/2) - (IMAGE_WIDTH/(5*2)))
        # CENTERX_MAX = round((IMAGE_WIDTH/2) + (IMAGE_WIDTH/(4*2)))

        TOLERANCE = (IMAGE_HEIGHT / (4*2)) # for 480 it is 60

        # Move the camera in small steps in the x direction based on the distance from the face center
        while abs(dx) > TOLERANCE or abs(dy) > TOLERANCE:
            print(f"face center: {face_center} face_bbox = {face_bbox} dx: {dx}, dy: {dy}")
            if dx > TOLERANCE:
                while dx > TOLERANCE:
                    move_camera("RIGHT", TIME_INCREMENT)
                    # Recalculate the face bounding box and update dx and dy accordingly
                    faces = detect_faces()
                    if faces and len(faces) > 0:
                        face_bbox = faces[0]
                        face_center = [(face_bbox[1] + face_bbox[3]) // 2, (face_bbox[0] + face_bbox[2]) // 2]
                        dx = face_center[0] - (IMAGE_WIDTH/2)
                        dy = face_center[1] - (IMAGE_HEIGHT/2)
                        print(f"face center: {face_center} face_bbox = {face_bbox} dx: {dx}, dy: {dy}")

            elif dx < -TOLERANCE:
                while dx < -TOLERANCE:
                    move_camera("LEFT", TIME_INCREMENT)

                    # Recalculate the face bounding box and update dx and dy accordingly
                    faces = detect_faces()
                    if faces and len(faces) > 0:
                        face_bbox = faces[0]
                        face_center = [(face_bbox[1] + face_bbox[3]) // 2, (face_bbox[0] + face_bbox[2]) // 2]
                        dx = face_center[0] - (IMAGE_WIDTH/2)
                        dy = face_center[1] - (IMAGE_HEIGHT/2)
                        print(f"face center: {face_center} face_bbox = {face_bbox} dx: {dx}, dy: {dy}")
            # Move the camera in small steps in the y direction based on the distance from the face center
            if dy > TOLERANCE:
                print(f"face center: {face_center} face_bbox = {face_bbox} dx: {dx}, dy: {dy}")
                while dy > TOLERANCE:
                    move_camera("DOWN", TIME_INCREMENT)

                    # Recalculate the face bounding box and update dx and dy accordingly
                    faces = detect_faces()
                    if faces and len(faces) > 0:
                        face_bbox = faces[0]
                        face_center = [(face_bbox[1] + face_bbox[3]) // 2, (face_bbox[0] + face_bbox[2]) // 2]
                        dx = face_center[0] - (IMAGE_WIDTH/2)
                        dy = face_center[1] - (IMAGE_HEIGHT/2)
                        print(f"face center: {face_center} face_bbox = {face_bbox} dx: {dx}, dy: {dy}")
            if dy < -TOLERANCE:
                print(f"face center: {face_center} face_bbox = {face_bbox} dx: {dx}, dy: {dy}")
                while dy < -TOLERANCE:
                    move_camera("UP", TIME_INCREMENT)

                    # Recalculate the face bounding box and update dx and dy accordingly
                    faces = detect_faces()
                    if faces and len(faces) > 0:
                        face_bbox = faces[0]
                        face_center = [(face_bbox[1] + face_bbox[3]) // 2, (face_bbox[0] + face_bbox[2]) // 2]
                        dx = face_center[0] - (IMAGE_WIDTH/2)
                        dy = face_center[1] - (IMAGE_HEIGHT/2)
                        print(f"face center: {face_center} face_bbox = {face_bbox} dx: {dx}, dy: {dy}")

move_camera_to_center()
while True:
    # Track the face in the frame using the track_face function
    track_face()

    # Check if the 'q' key was pressed
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()