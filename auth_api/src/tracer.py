from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from core.config import jaeger_config


def configure_tracer() -> None:
    trace.set_tracer_provider(TracerProvider(
        resource=Resource.create({SERVICE_NAME: "fastapi_auth"}))
    )
    trace_exporter = JaegerExporter(
        agent_host_name=jaeger_config.agent_host_name,
        agent_port=int(jaeger_config.agent_port),
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(trace_exporter)
    )
    trace.get_tracer_provider(). \
        add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
