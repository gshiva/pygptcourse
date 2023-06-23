#!/usr/bin/python

import cv2

import face_recognition

shiva_image = face_recognition.load_image_file("shiva_face.jpg")
shiva_face_encoding = face_recognition.face_encodings(shiva_image)[0]

adil_image = face_recognition.load_image_file("adil_face.jpg")
adil_face_encoding = face_recognition.face_encodings(adil_image)[0]

video_capture = cv2.VideoCapture(0)
video_capture.set(3, 640)  # Set horizontal resolution
video_capture.set(4, 480)  # Set vertical resolution

counter = 0
face_names = []

center_x = 0
center_y = 0

face_center_x = 0
face_center_y = 0

while True:
    ret, image = video_capture.read()

    if not ret:
        break


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

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Because we made the image smaller, now need to multiply by 4 to get correct size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
        cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
        centerx = right - left
        centery = bottom - top

        name = name + ": r:" + str(right) + ", b:" + str(bottom) + ", l:" + str(left) + ", t:" + str(top)

        print(f"Name: {name}")

        # Draw a label with a name below the face
        cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        cv2.putText(image, name, (left + 6, bottom - 6),  cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 1)


    cv2.imshow('Video', image)
    counter += 1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
