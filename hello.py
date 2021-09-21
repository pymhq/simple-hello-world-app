import boto3
from flask import Flask
import os
import time
import json 
import requests

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry.sdk.extension.aws.trace import AwsXRayIdGenerator

from opentelemetry import propagate
from opentelemetry.sdk.extension.aws.trace.propagation.aws_xray_format import AwsXRayFormat

from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

from opentelemetry.sdk.extension.aws.trace.propagation.aws_xray_format import (
    TRACE_ID_DELIMITER,
    TRACE_ID_FIRST_PART_LENGTH,
    TRACE_ID_VERSION,
)


otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.set_tracer_provider(TracerProvider(active_span_processor=span_processor, id_generator=AwsXRayIdGenerator()))

propagate.set_global_textmap(AwsXRayFormat())

app = Flask(__name__)

BotocoreInstrumentor().instrument()
# Initialize `Instrumentor` for the `requests` library
RequestsInstrumentor().instrument()
# Initialize `Instrumentor` for the `flask` web framework
FlaskInstrumentor().instrument_app(app)

def convert_otel_trace_id_to_xray(otel_trace_id_decimal):
    otel_trace_id_hex = "{:032x}".format(otel_trace_id_decimal)
    x_ray_trace_id = TRACE_ID_DELIMITER.join(
        [
            TRACE_ID_VERSION,
            otel_trace_id_hex[:TRACE_ID_FIRST_PART_LENGTH],
            otel_trace_id_hex[TRACE_ID_FIRST_PART_LENGTH:],
        ]
    )
    return '{{"traceId": "{}"}}'.format(x_ray_trace_id)

@app.route('/')
def hello_world():
    return 'Hello World! App Runner'
@app.route('/health')
def health_check():
    return 'health check'

# Test HTTP instrumentation
@app.route("/outgoing-http-call")
def call_http():
    requests.get("https://aws.amazon.com/")

    return app.make_response(
        convert_otel_trace_id_to_xray(
            trace.get_current_span().get_span_context().trace_id
        )
    )


if __name__ == '__main__':
    app.run(threaded=True, host="0.0.0.0", debug=True, port=int(os.environ.get("PORT", 8000)))
    

    
