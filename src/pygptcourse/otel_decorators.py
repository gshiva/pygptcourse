# otel_decorators.py
import logging
import sys
from functools import wraps

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.metrics import get_meter_provider, set_meter_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import get_tracer_provider, set_tracer_provider

# isort: off
from pygptcourse.credentials import OpenTelemetryCredentials

# isort: on

logging.getLogger().setLevel(logging.INFO)


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
    def __init__(self, trace_interval_minutes=5):
        self.creds = OpenTelemetryCredentials()
        self.enabled = self.creds.is_configured()
        self.last_trace_time = 0
        self.trace_interval_seconds = trace_interval_minutes * 60

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

                # Setup Tracing
                # Initialize the tracer provider and trace exporter
                self.otlp_trace_exporter = OTLPSpanExporter(
                    endpoint=f"{self.creds.traces_endpoint}",
                    headers={"authorization": f"Basic {self.creds.api_encoded_token}"},
                )
                trace_provider = TracerProvider(resource=self.resource)
                trace_provider.add_span_processor(
                    BatchSpanProcessor(self.otlp_trace_exporter)
                )

                # Set the fully configured tracer provider globally
                set_tracer_provider(trace_provider)
                self.tracer = get_tracer_provider().get_tracer(service_name, VERSION)

                # Set up logger provider with resource attributes

                # Configure OTLP log exporter
                self.otlp_logs_exporter = OTLPLogExporter(
                    endpoint=f"{self.creds.logs_endpoint}",
                    headers={"authorization": f"Basic {self.creds.api_encoded_token}"},
                )
                logger_provider = LoggerProvider(resource=self.resource)
                self.logger_provider = set_logger_provider(logger_provider)
                logger_provider.add_log_record_processor(
                    BatchLogRecordProcessor(self.otlp_logs_exporter)
                )

                # Create and attach OTLP logging handler to root logger
                handler = LoggingHandler(
                    level=logging.NOTSET, logger_provider=logger_provider
                )
                logging.getLogger().addHandler(handler)

                # Add the stdout logging handler also
                handler = logging.StreamHandler(sys.stdout)
                handler.setLevel(logging.INFO)
                logging.getLogger().addHandler(handler)

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
                logging.error(f"OpenTelemetry initialization failed: {e}")

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
            if not self.enabled:  # Skip all tracing if OTLP is not configured
                return func(*args, **kwargs)

            # Use the stored tracer instance
            with self.tracer.start_as_current_span(func.__name__) as span:
                # Capture and log function arguments
                span.set_attribute("arguments", str(args) + " " + str(kwargs))

                try:
                    # Execute the wrapped function
                    result = func(*args, **kwargs)

                    # Capture and log the return value
                    span.set_attribute("return_value", str(result))
                    return result
                except Exception as e:
                    # Capture and log the exception details
                    logging.error(f"Exception in {func.__name__}: {e}", exc_info=True)
                    span.set_attribute("error", True)
                    span.record_exception(e)
                    raise

        return wrapper


# Global instance of the handler
otel_handler = OpenTelemetryHandler(trace_interval_minutes=1)
