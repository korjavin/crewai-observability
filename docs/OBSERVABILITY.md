# Observability: Tracing the Crew

This document explains how to set up and leverage the observability stack for this project. The goal is to gain deep visibility into the `crewai` workflow using **OpenTelemetry** and **Jaeger**.

## 1. Why Observability?

In a complex agentic system, it can be difficult to understand what's happening under the hood. Observability allows us to answer key questions:
-   Where did a workflow fail?
-   How long did each agent or tool take to execute?
-   What exact data was passed from one agent to another?
-   How many tokens did the LLM calls consume for a specific task?

By tracing our application, we move from a "black box" to a "glass box."

## 2. The Stack

-   **OpenTelemetry (OTel)**: An open-source, vendor-neutral standard for collecting telemetry data (traces, metrics, logs). We will use the Python SDK to automatically instrument our `crewai` application.
-   **Jaeger**: An open-source, end-to-end distributed tracing system. We will run Jaeger locally in a Docker container to receive the telemetry data from our application and visualize it.

## 3. Setup and Configuration

### Step 1: Install Dependencies

Add the necessary OpenTelemetry packages to your `requirements.txt` and install them:

```
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
```

### Step 2: Run Jaeger

Run a local Jaeger instance using Docker. This command exposes the necessary ports for receiving data and for viewing the Jaeger UI.

```bash
docker run -d --name jaeger \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  jaegertracing/all-in-one:latest
```

-   `16686`: Jaeger UI port.
-   `4317`: OTLP gRPC receiver port.

### Step 3: Configure the Application

In your `main.py`, before you initialize your crew, you need to configure the OpenTelemetry SDK. `crewai` looks for this configuration to automatically start sending traces.

A simple helper function can manage this:

```python
# In main.py or a helper module
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

def setup_opentelemetry():
    """Initializes OpenTelemetry for the application."""
    provider = TracerProvider()
    processor = BatchSpanProcessor(OTLPSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
```

You would then call `setup_opentelemetry()` at the start of your `main.py`.

Alternatively, `crewai` is moving towards a more seamless integration. The primary method will be to set environment variables in your `.env` file:

```
# .env file
OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
OTEL_SERVICE_NAME="crewai-scheduling-assistant"
```

`crewai` will detect these and configure the exporter automatically.

## 4. Interpreting the Traces

Once you run your `main.py` script, the crew will execute, and traces will be sent to Jaeger.

1.  **Open the Jaeger UI**: Navigate to `http://localhost:16686` in your browser.
2.  **Select Service**: In the top-left dropdown, select the `crewai-scheduling-assistant` service.
3.  **Find Traces**: Click "Find Traces." You should see a list of recent traces. Each trace corresponds to one full run of a `crew`.

### What a Trace Looks Like

When you click on a trace, you will see a timeline of operations, known as **spans**.

-   **Root Span (`Crew.kickoff`)**: This is the parent span representing the entire workflow.
    -   **Task Spans**: Nested within the root span, you will see a span for each `Task` in your crew. This shows you how long each task took.
        -   **Agent Spans**: Inside a task, you'll see the `Agent` execution span.
            -   **Tool Spans**: If an agent used a tool, you will see a span for that `Tool` call (e.g., `read_emails`). The attributes of this span will contain the exact parameters passed to the tool.
            -   **LLM Spans**: `crewai` also creates spans for calls to the Language Model. You can inspect these to see the prompt, the response, and even token usage metrics.

This hierarchical view is incredibly powerful for debugging. If an agent returns an unexpected output, you can inspect the trace to see the LLM call that produced it and the tool outputs it had as context.

