import functools
import logging
import os

import boto3

NAMESPACE = "TodoApi"

logger = logging.getLogger(__name__)


@functools.cache
def get_client():
    return boto3.client("cloudwatch", region_name=os.environ["AWS_REGION"])


def put_count(name, value=1):
    # Publicar una métrica nunca debe tumbar una petición de la API
    try:
        get_client().put_metric_data(
            Namespace=NAMESPACE,
            MetricData=[{"MetricName": name, "Value": value, "Unit": "Count"}],
        )
    except Exception:
        logger.exception("No se pudo publicar la métrica %s", name)
