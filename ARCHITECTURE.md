# **I. System Architecture Overview**

This section establishes the high-level architectural design, defining the system's components, boundaries, and the technologies that underpin its functionality. The architecture is designed for modularity, scalability, and, most importantly, deep observability.

### **1.1. High-Level System Context**

The system operates as an intermediary between a user's Google Workspace account and an AI-driven decision-making engine. It is composed of five primary interacting components: the User, Google Workspace, the `crewai` Scheduling Assistant application, a Human-in-the-Loop (HITL) Interface, and the Observability Stack.

The diagram below illustrates the relationships and primary data flows between these components. The `crewai` assistant is the central hub, pulling data from Google Mail, pushing data to Google Calendar, interacting with the user for confirmation, and continuously emitting telemetry data to the dedicated observability stack.

C4Context

  title System Context Diagram for AI Scheduling Assistant

  Person(user, "User", "Provides email/calendar access and event confirmation.")

  System_Ext(google, "Google Workspace", "Provides Gmail and Google Calendar APIs.")

  System_Boundary(c1, "AI Scheduling System") {

    System(app, "crewai Scheduling Assistant", "Core Python application with agentic logic.")

    System(hitl, "Human-in-the-Loop Interface", "CLI or simple UI for user approvals.")

  }

  System_Boundary(c2, "Observability Stack") {

    System(collector, "OpenTelemetry Collector", "Receives, processes, and routes telemetry.")

    SystemDb(jaeger, "Jaeger", "Stores and visualizes distributed traces.")

    SystemDb(prometheus, "Prometheus", "Stores and queries time-series metrics.")

  }

  Rel(user, google, "Authenticates with")

  Rel(user, hitl, "Approves/Rejects proposals via")

  Rel(app, google, "Reads emails and manages calendar via APIs")

  Rel(app, hitl, "Presents proposals to")

  Rel(app, collector, "Emits traces and metrics to", "OTLP")

  Rel(collector, jaeger, "Exports traces to")

  Rel(collector, prometheus, "Exports metrics to")

  UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="2")

### **1.2. Core Technology Stack**

The selection of technologies is driven by the project's dual requirements: building a functional AI agent system and establishing a comprehensive, open-source observability framework. Each component is chosen for its maturity, community support, and alignment with modern cloud-native and AI development practices.

* **Application Framework**: `crewai`. This modern, Python-native framework is selected for its standalone nature (independent of other agent frameworks like LangChain), its focus on role-based autonomous agents, and its support for both autonomous `Crews` and structured `Flows`. Its lean design and growing ecosystem make it an ideal choice for this project.  
* **External Service APIs**: Google Mail API & Google Calendar API. These are the necessary interfaces to fulfill the application's core functional requirements of reading emails and managing calendar events.  
* **Observability Instrumentation**: OpenLLMetry. This library is a critical choice as it is an extension of OpenTelemetry specifically designed for LLM applications. It provides out-of-the-box instrumentation for `crewai`, LLM providers, and vector databases, capturing rich, application-specific context such as prompts, completions, and token counts automatically. This directly addresses the core requirement for deep LLM traceability.  
* **Telemetry Pipeline**: OpenTelemetry Collector. The Collector is a vendor-neutral proxy that receives, processes, and exports telemetry data. Its use is a strategic architectural decision that decouples the application from the specific observability backends, allowing for flexible routing and processing of traces, metrics, and logs.  
* **Distributed Tracing Backend**: Jaeger. A popular and powerful open-source distributed tracing system. Its user interface is highly effective for visualizing the complex, nested interactions of a multi-agent system, making it possible to trace a single request from email ingestion through agent collaboration to final event creation.  
* **Metrics & Monitoring Backend**: Prometheus & Grafana. Prometheus is the de-facto industry standard for open-source metrics storage and querying, while Grafana is the leading tool for building rich, interactive dashboards from that data. This combination will provide at-a-glance insights into system performance, LLM costs, and operational health.  
* **Containerization**: Docker & Docker Compose. The entire system, including the application and the multi-component observability stack, will be defined and managed via Docker Compose. This ensures a consistent, reproducible, and portable development environment that can be spun up with a single command.

For more details, please refer to the documents in the `docs/` directory.