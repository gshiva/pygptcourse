import face_recognition  # type: ignore

from pygptcourse.otel_decorators import otel_handler


class FaceDetector:
    def __init__(self, face_images, image_loader):
        self.image_loader = image_loader
        self.face_encodings = self.load_and_encode_faces(face_images)

    @otel_handler.trace
    def load_and_encode_faces(self, face_images):
        encodings = {}
        for name, image_path in face_images.items():
            full_image_path = self.image_loader.get_full_image_path(image_path)
            image = face_recognition.load_image_file(full_image_path)
            encodings[name] = face_recognition.face_encodings(image)[0]
        return encodings

    @otel_handler.trace
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
            otel_handler.faces_detected_count.add(1, {"name": name})

        return face_locations, face_names
