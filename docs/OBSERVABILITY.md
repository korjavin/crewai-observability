## **III. Observability and Traceability Architecture**

This section details the implementation of the observability stack, which is the primary non-functional requirement of this project. The architecture is based on OpenTelemetry, a vendor-neutral, open-source standard for observability data.

### **3.1. Instrumentation with OpenLLMetry**

The foundation of observability is instrumentation—the process of generating telemetry data from the application code. OpenLLMetry provides a simple yet powerful way to achieve this for `crewai` applications with minimal code changes.

**Implementation Steps:**

**Install Dependencies**: The necessary Python packages are installed via `pip`. This includes the core SDK and the specific instrumentation for `crewai`.  
pip install traceloop-sdk opentelemetry-instrumentation-crewai

1. 

**Initialize in Application**: A single initialization call is added to the main entry point of the application (e.g., `main.py`). This call must be executed before any `crewai` or LLM code is run.  
# main.py

from traceloop.sdk import Traceloop

import os

# Configure the exporter endpoint to point to the OTel Collector

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"

Traceloop.init(app_name="crewai_scheduling_assistant")

#... rest of the application logic...

2. 

This simple initialization automatically "patches" key libraries at runtime to intercept and record their operations. The data captured includes:

* **`crewai` Spans**: A trace is created for the entire `crew.kickoff()` execution. Within this trace, separate spans are generated for each `task.execute()` call and for the internal thought processes of each agent, providing a hierarchical view of the crew's operation.  
* **LLM Spans**: All calls to large language models made through `LiteLLM` (the library `crewai` uses internally) are captured. These spans are enriched with critical attributes for debugging and analysis, such as `llm.prompt`, `llm.completion`, `llm.token.usage`, and `llm.model_name`. This directly fulfills the requirement for deep LLM prompt traceability.  
* **Tool Spans**: Each time an agent utilizes a custom tool, a span is created. This span records the name of the tool, its input parameters, and its output, making it easy to debug interactions with external APIs.

### **3.2. Telemetry Pipeline: The OpenTelemetry Collector**

The OpenTelemetry Collector is a pivotal component of this architecture, acting as a centralized and configurable pipeline for all telemetry data. Its primary role is to receive data from the application and route it to the appropriate backend systems. This design decouples the application from the observability infrastructure; the application only needs to know about the Collector's endpoint, not the specifics of Jaeger or Prometheus. This provides immense flexibility, as backends can be changed, or new ones (like a logging backend) can be added, solely by modifying the Collector's configuration without touching the application code.

The following YAML configuration defines the Collector's behavior. It sets up an OTLP receiver, a batch processor for efficiency, and two distinct pipelines: one for routing traces to Jaeger and another for routing metrics to Prometheus.

**`otel-collector-config.yaml`:**

# 1. Receivers: Defines how data gets into the Collector.

receivers:

  otlp:

    protocols:

      # OTLP over gRPC, typically used by SDKs for performance.

      grpc:

        endpoint: 0.0.0.0:4317

      # OTLP over HTTP, useful for broader compatibility.

      http:

        endpoint: 0.0.0.0:4318

# 2. Processors: Defines how data is processed within the Collector.

processors:

  # Batches telemetry data to reduce the number of export requests.

  batch:

    timeout: 1s

    send_batch_size: 512

# 3. Exporters: Defines where data is sent from the Collector.

exporters:

  # Exports traces to Jaeger via gRPC.

  jaeger:

    endpoint: jaeger:14250

    tls:

      insecure: true


  # Exports metrics in a format that Prometheus can scrape.

  prometheus:

    endpoint: 0.0.0.0:8889

    namespace: crewai_assistant

# 4. Service: Connects receivers, processors, and exporters into pipelines.

service:

  pipelines:

    # Pipeline for trace data.

    traces:

      receivers: [otlp]

      processors: [batch]

      exporters: [jaeger]

    

    # Pipeline for metric data.

    metrics:

      receivers: [otlp]

      processors: [batch]

      exporters: [prometheus]

### **3.3. Data Backend and Visualization**

The final layer of the observability stack consists of the specialized backend systems for storing, querying, and visualizing the telemetry data.

The table below summarizes the components of the observability stack, clarifying the specific function of each tool in the architecture.

| Component | Role in Architecture | Key Functionality | Configuration Interface |
| :---- | :---- | :---- | :---- |
| OpenLLMetry SDK | Instrumentation Library | Auto-instruments `crewai`, LLMs, and tools to generate OTel traces and metrics. | Python (`Traceloop.init()`) |
| OpenTelemetry Collector | Telemetry Pipeline / Router | Receives data via OTLP, batches it, and exports it to multiple backend systems. | YAML (`config.yaml`) |
| Jaeger | Distributed Tracing Backend & UI | Stores and visualizes end-to-end traces, enabling deep debugging of agent flows. | Web UI, API |
| Prometheus | Metrics Time-Series Database | Scrapes and stores numerical metrics data for performance analysis and alerting. | YAML, PromQL, Web UI |
| Grafana | Visualization & Dashboarding | Queries Prometheus to create rich, interactive dashboards for monitoring system health. | Web UI |

#### **Distributed Tracing with Jaeger**

Jaeger is used to visualize the end-to-end lifecycle of each scheduling request. When a new request is processed, a developer can navigate to the Jaeger UI and see a detailed trace. This trace will appear as a waterfall diagram, showing:

* A single **root span** representing the entire `crew.kickoff()` call.  
* Nested **parent spans** for each task executed by the crew (e.g., `scan_inbox_task`, `find_slots_task`).  
* Further nested **child spans** for each LLM call and tool usage within a task.

Crucially, by selecting an LLM span, the developer can view the full, unredacted text of the `llm.prompt` and `llm.completion` in the span's attributes (tags). This provides an unparalleled level of insight for debugging agent behavior, analyzing prompt effectiveness, and understanding why the AI made a particular decision.

#### **Metrics Monitoring with Prometheus & Grafana**

Prometheus will be configured to periodically "scrape" the `/metrics` endpoint exposed by the OpenTelemetry Collector's Prometheus exporter. It will store this data in its time-series database. Key metrics automatically generated by OpenLLMetry and available for monitoring include:

* `llm_calls_total`: A counter for the total number of LLM API calls, which can be broken down by model, agent, or task.  
* `llm_tokens_total`: A counter for prompt and completion token usage, essential for cost monitoring.  
* `llm_request_duration_seconds`: a histogram measuring the latency of LLM API calls.  
* `crew_task_duration_seconds`: a histogram measuring the execution time of each `crewai` task.

This data can then be visualized in a Grafana dashboard. A sample dashboard could include panels for:

* **Estimated LLM Costs**: A time-series graph showing the cumulative cost based on token usage.  
* **Average Task Latency**: A bar chart showing the average execution time for each task in the crew.  
* **Token Usage by Agent**: A pie chart breaking down token consumption by each agent.  
* **API Error Rate**: A stat panel showing the percentage of failed LLM or tool calls.