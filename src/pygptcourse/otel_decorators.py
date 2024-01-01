# otel_decorators.py

from functools import wraps

from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.metrics import get_meter_provider, set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from pygptcourse.credentials import OpenTelemetryCredentials


class DummyMetric:
    def __init__(self):
        self.counts = {}  # Dictionary to hold counts for different label combinations

    def add(self, value, labels=None):
        # Convert labels to a frozenset to use as a key in the counts dictionary
        label_key = frozenset(labels.items()) if labels else frozenset()

        # If this set of labels hasn't been seen before, initialize its count
        if label_key not in self.counts:
            self.counts[label_key] = 0

        # Add the value to the count for this set of labels
        self.counts[label_key] += value

    def get_count(self, labels=None):
        # Method to retrieve the count for specific labels for debugging
        label_key = frozenset(labels.items()) if labels else frozenset()
        return self.counts.get(label_key, 0)


class OpenTelemetryHandler:
    def __init__(self):
        self.creds = OpenTelemetryCredentials()
        self.enabled = self.creds.is_configured()

        if self.enabled:
            try:
                # Initialize OpenTelemetry components here
                VERSION = "0.1.2"
                service_name = "TShirtLauncherControl"
                self.resource = Resource.create({SERVICE_NAME: service_name})
                self.otlp_metrics_exporter = OTLPMetricExporter(
                    endpoint=f"{self.creds.metrics_endpoint}",
                    headers={"authorization": f"Basic {self.creds.api_encoded_token}"},
                )
                self.metric_reader = PeriodicExportingMetricReader(
                    exporter=self.otlp_metrics_exporter,
                    export_interval_millis=10000,
                    export_timeout_millis=2000,
                )
                self.meter_provider = MeterProvider(
                    resource=self.resource, metric_readers=[self.metric_reader]
                )
                set_meter_provider(self.meter_provider)

                self.meter = get_meter_provider().get_meter(service_name, VERSION)

                # Metric definitions
                self.usb_failures = self.meter.create_counter(
                    "usb_connection_failures",
                    description="Count of USB connection failures",
                    unit="int",
                )
                self.launch_count = self.meter.create_counter(
                    "launch_count", description="Total number of launches", unit="int"
                )
                self.faces_detected_count = self.meter.create_counter(
                    "faces_detected",
                    description="Total number of faces detected",
                    unit="int",
                )
            except Exception as e:
                # Handle initialization failure by disabling OpenTelemetry and using dummy metrics
                self.enabled = False
                print(f"OpenTelemetry initialization failed: {e}")

                # Initializing dummy metrics
                self._initialize_dummy_metrics()
        else:
            # Use dummy metrics if not enabled
            self._initialize_dummy_metrics()

    def _initialize_dummy_metrics(self):
        # Method to initialize all dummy metrics
        self.usb_failures = DummyMetric()
        self.launch_count = DummyMetric()
        self.faces_detected_count = DummyMetric()

    def trace(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.enabled:
                # If OTLP is enabled, do something before the function (e.g., start a span)

                # Execute the function
                result = func(*args, **kwargs)

                # Do something after the function (e.g., end the span)

                return result
            else:
                # If OTLP is not enabled, just execute the function
                return func(*args, **kwargs)

        return wrapper


# Global instance of the handler
otel_handler = OpenTelemetryHandler()
