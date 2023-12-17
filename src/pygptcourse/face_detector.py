import face_recognition  # type: ignore


class FaceDetector:
    def __init__(self, face_images):
        self.face_encodings = self.load_and_encode_faces(face_images)

    def load_and_encode_faces(self, face_images):
        encodings = {}
        for name, image_path in face_images.items():
            image = face_recognition.load_image_file(image_path)
            encodings[name] = face_recognition.face_encodings(image)[0]
        return encodings

    def detect_faces(self, image):
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(
                list(self.face_encodings.values()), face_encoding
            )
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = list(self.face_encodings.keys())[first_match_index]

            face_names.append(name)

        return face_locations, face_names
