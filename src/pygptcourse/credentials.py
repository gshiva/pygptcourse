# credentials.py

import base64
import logging
import os

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class OpenTelemetryCredentials:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file

        self.username = os.getenv("GRAFANA_OTLP_USERNAME")
        logger.info(f"Grafana OTLP username is: {self.username}")
        self.api_token = os.getenv("GRAFANA_OTLP_API_TOKEN")
        self.api_encoded_token = base64.b64encode(
            f"{self.username}:{self.api_token}".encode("utf-8")
        ).decode("utf-8")
        self.endpoint = os.getenv("GRAFANA_OTLP_ENDPOINT")
        if self.endpoint:
            self.traces_endpoint = self.endpoint + "/v1/traces"
            self.metrics_endpoint = self.endpoint + "/v1/metrics"
            self.logs_endpoint = self.endpoint + "/v1/logs"

    def is_configured(self):
        # Check if all the necessary variables are present
        return all([self.username, self.api_token, self.endpoint])
