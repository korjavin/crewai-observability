## **V. Deployment and Operationalization Blueprint**

This section provides a practical guide for setting up, containerizing, and running the entire system. The use of Docker Compose ensures a one-command setup for the entire multi-service architecture.

### **5.1. Containerization with Docker Compose**

Docker Compose is used to define and run the multi-container application. This approach encapsulates each component of the architecture into its own isolated service, simplifying deployment and ensuring consistency across different developer machines.

A key benefit of this approach is the creation of an isolated virtual network for all services defined in the `docker-compose.yml` file. Within this network, Docker provides an internal DNS service, allowing containers to communicate with each other using their service names as hostnames (e.g., the application can send data to `http://otel-collector:4318`). This networking abstraction is a crucial architectural pattern that makes the entire stack portable and removes the need for environment-specific network configurations, greatly simplifying operations.

**`docker-compose.yml`:**

version: '3.8'

services:

  # The core crewai application

  crew-app:

    build: .

    container_name: crew-app

    env_file: .env

    volumes:

      - .:/app

    depends_on:

      - otel-collector

    environment:

      # This overrides any local setting to ensure it points to the container

      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318

  # The OpenTelemetry Collector

  otel-collector:

    image: otel/opentelemetry-collector-contrib:latest

    container_name: otel-collector

    command: ["--config=/etc/otelcol-contrib/config.yaml"]

    volumes:

      - ./otel-collector-config.yaml:/etc/otelcol-contrib/config.yaml

    ports:

      - "4317:4317" # OTLP gRPC

      - "4318:4318" # OTLP HTTP

      - "8889:8889" # Prometheus exporter

  # Jaeger for distributed tracing

  jaeger:

    image: jaegertracing/all-in-one:latest

    container_name: jaeger

    ports:

      - "16686:16686" # Jaeger UI

      - "14250:14250" # gRPC collector endpoint for OTel

  # Prometheus for metrics

  prometheus:

    image: prom/prometheus:latest

    container_name: prometheus

    volumes:

      - ./prometheus.yml:/etc/prometheus/prometheus.yml

    ports:

      - "9090:9090"

    depends_on:

      - otel-collector

  # Grafana for dashboards

  grafana:

    image: grafana/grafana:latest

    container_name: grafana

    ports:

      - "3000:3000"

    depends_on:

      - prometheus

**`prometheus.yml`:**

global:

  scrape_interval: 15s

scrape_configs:

  - job_name: 'otel-collector'

    static_configs:

      - targets: ['otel-collector:8889']

### **5.2. Project Setup and Execution Guide**

The following steps provide a complete walkthrough for a developer to get the system running locally.

1. **Clone Repository**: Obtain the project source code from the version control system.  
2. **Install `crewai` Project**: Run the `crewai install` command. This will use `uv` to create a virtual environment and install all dependencies listed in `pyproject.toml`, setting up the Python environment correctly.  
3. **Obtain Google Credentials**: Follow the steps detailed in Section 4.1 to create a Google Cloud project, enable APIs, and download the `client_secret.json` file, placing it in the project's root directory.  
4. **Configure Environment**: Create a `.env` file in the project root. Populate it with the necessary API keys (e.g., `OPENAI_API_KEY`).  
5. **Launch Infrastructure**: From the project root, run the command `docker compose up -d`. This will build the application image and start all the infrastructure containers (Collector, Jaeger, Prometheus, Grafana) in the background.  
6. **Run the Application**: Execute the main application script from the terminal: `python src/project_name/main.py`.  
7. **First-Time Authentication**: On the first run, the application will open a web browser. The user must log in to their Google account and grant the requested permissions. After consent, the `token.json` file will be created, and subsequent runs will be non-interactive.  
8. **Observe Application**: The application's progress, including agent thoughts and actions, will be printed to the console (due to `verbose=2`). The user will be prompted for approval when the `HumanApprovalTool` is invoked.  
9. **Explore Telemetry Data**:  
   * **Traces**: Open a web browser and navigate to the Jaeger UI at `http://localhost:16686`. Select the `crewai_scheduling_assistant` service to find and explore the detailed, end-to-end traces of the application's execution.  
   * **Metrics**: Navigate to the Grafana UI at `http://localhost:3000`. Configure a new Prometheus data source pointing to `http://prometheus:9090`. Build dashboards to visualize the metrics being scraped from the OTel Collector.

This completes the setup and execution, successfully demonstrating a fully functional and deeply observable `crewai` application.