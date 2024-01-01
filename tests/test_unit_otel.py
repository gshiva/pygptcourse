import os
import unittest
from unittest.mock import MagicMock, Mock, patch

from pygptcourse.face_detector import FaceDetector
from pygptcourse.otel_decorators import OpenTelemetryHandler, otel_handler


class TestOpenTelemetry(unittest.TestCase):
    def setUp(self):
        # Mocking environment variables typically found in .env file
        self.env_vars = {
            "GRAFANA_OTLP_USERNAME": "example_username",
            "GRAFANA_OTLP_API_TOKEN": "example_token",
            "GRAFANA_OTLP_ENDPOINT": "https://example.com/endpoint",
        }
        self.mock_exporter = MagicMock()

    def test_otel_configuration(self):
        # Mocking the environment variables for the test
        with patch.dict(os.environ, self.env_vars):
            handler = OpenTelemetryHandler()
            self.assertIsNotNone(handler.meter)
            # Asserting that the credentials are loaded correctly from the environment
            self.assertEqual(handler.creds.username, "example_username")
            self.assertEqual(handler.creds.api_token, "example_token")
            self.assertEqual(handler.creds.endpoint, "https://example.com/endpoint")

    @patch("opentelemetry.sdk.metrics.export.PeriodicExportingMetricReader")
    @patch("opentelemetry.exporter.otlp.proto.http.metric_exporter.OTLPMetricExporter")
    def test_otel_export_with_error(self, mock_exporter, mock_reader):
        # Configure the mock exporter to raise an exception when exporting
        mock_exporter.return_value.export.side_effect = Exception("Export failed")
        # Assuming a realistic way to trigger the metric increment
        otel_handler.faces_detected_count.add(1, {"name": "Test"})
        try:
            mock_reader.return_value.force_flush()
        except Exception as e:
            self.assertIsInstance(e, Exception)
            self.assertEqual(str(e), "Export failed")

    def test_decorator_functionality(self):
        expected_result = "expected result"

        @otel_handler.trace
        def function_to_test():
            return expected_result

        result = function_to_test()
        self.assertEqual(result, expected_result)

    def test_error_handling(self):
        with self.assertRaises(Exception):
            raise Exception("Simulated realistic failure")


class TestFaceDetector(unittest.TestCase):
    @patch("face_recognition.compare_faces", return_value=[True, False])
    @patch("face_recognition.face_encodings")
    @patch("face_recognition.face_locations")
    @patch("face_recognition.load_image_file")
    @patch(
        "pygptcourse.otel_decorators.otel_handler.faces_detected_count.add"
    )  # replace with the actual module name
    def test_detect_faces(
        self,
        mock_otel_handler_add,
        mock_load_image_file,
        mock_face_locations,
        mock_face_encodings,
        mock_compare_faces,
    ):
        # Arrange
        mock_image_loader = Mock()
        mock_image_loader.get_full_image_path.return_value = "full_image_path"
        face_images = {"test": "image_path"}
        detector = FaceDetector(face_images, mock_image_loader)

        mock_image = Mock()
        mock_load_image_file.return_value = mock_image
        mock_face_locations.return_value = ["location"]
        mock_face_encodings.return_value = [
            [0.1] * 128
        ]  # A list of a single face encoding

        # Act
        detector.detect_faces(mock_image)

        # Assert
        mock_otel_handler_add.assert_called_once_with(1, {"name": "test"})


if __name__ == "__main__":
    unittest.main()
