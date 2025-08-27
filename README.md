# AI-Powered Scheduling Assistant

[![Main CI Pipeline](https://github.com/jules-example/crewai-scheduling-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/jules-example/crewai-scheduling-assistant/actions/workflows/ci.yml)
[![Security Pipeline](https://github.com/jules-example/crewai-scheduling-assistant/actions/workflows/security.yml/badge.svg)](https://github.com/jules-example/crewai-scheduling-assistant/actions/workflows/security.yml)

This project is an AI-powered scheduling assistant that automates the process of scheduling meetings from email requests. It uses a `crewai`-based multi-agent system to read emails, identify scheduling requests, find available time slots in a user's calendar, and create calendar events after receiving user approval.

The core of the project is a `crewai` application that leverages Google Mail and Google Calendar APIs. The system is designed with a strong focus on observability, using OpenTelemetry to provide deep insights into the agent's behavior and performance. The entire application and its observability stack (Jaeger, Prometheus, Grafana) are containerized with Docker for easy and reproducible deployment.

## How it Works

The AI is powered by a team of autonomous agents, each with a specific role, working together to handle scheduling requests. The workflow is sequential, with each agent handing off its work to the next in the process.

### The Agents

1.  **Inbox Analyst (`email_triage_agent`)**:
    -   **Goal**: Meticulously scans incoming emails to identify actionable meeting requests.
    -   **Tools**: `gmail_reader_tool`
    -   **Backstory**: An expert in natural language understanding, trained to distinguish between casual mentions of meetings and concrete scheduling requests.

2.  **Calendar Coordination Specialist (`scheduling_agent`)**:
    -   **Goal**: Analyzes meeting requirements and finds optimal, conflict-free time slots in the user's calendar.
    -   **Tools**: `google_calendar_search_tool`
    -   **Backstory**: A master of temporal logistics with deep knowledge of the Google Calendar API.

3.  **User Interaction Liaison (`confirmation_agent`)**:
    -   **Goal**: Clearly presents proposed meeting times to the user and accurately captures their final decision.
    -   **Tools**: `human_approval_tool`
    -   **Backstory**: A communications expert focused on making the human-in-the-loop step seamless and efficient.

4.  **Event Logistics Executor (`booking_agent`)**:
    -   **Goal**: Creates precise calendar events based on confirmed details.
    -   **Tools**: `google_calendar_writer_tool`
    -   **Backstory**: A detail-oriented professional who ensures all event details are perfect and all attendees are invited.

### The Tasks

1.  **Scan Inbox (`scan_inbox_task`)**:
    -   The `Inbox Analyst` scans the last 24 hours of emails to find potential meeting requests.

2.  **Find Available Slots (`find_slots_task`)**:
    -   The `Calendar Coordination Specialist` extracts meeting details from the email and queries Google Calendar to find three suitable time slots.

3.  **Confirm Time with User (`confirm_time_task`)**:
    -   The `User Interaction Liaison` presents the proposed slots to the user for their approval.

4.  **Create Calendar Event (`create_event_task`)**:
    -   The `Event Logistics Executor` takes the user-confirmed time and creates the event in Google Calendar, inviting all attendees.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install project dependencies:**
    This project uses Poetry to manage dependencies. Run the following command to create a virtual environment and install all necessary packages from `pyproject.toml`:
    ```bash
    poetry install
    ```

## Google API Credentials Setup

This application requires Google API credentials to access your Gmail and Google Calendar. Follow these steps to set up the necessary credentials:

1.  **Create a Google Cloud Project:**
    - Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.

2.  **Enable APIs:**
    - In your project's dashboard, navigate to the "APIs & Services" section.
    - Enable the **Gmail API** and the **Google Calendar API**.

3.  **Configure OAuth Consent Screen:**
    - Configure the OAuth consent screen. For personal use, you can select "External" for the user type.
    - Provide an application name and user support email.

4.  **Create OAuth 2.0 Client ID:**
    - Go to the "Credentials" section and create a new "OAuth 2.0 Client ID".
    - Select "Desktop app" as the application type.
    - Download the credentials as a `client_secret.json` file and place it in the root of the project directory.

5.  **Create a `.env` file:**
    - Create a `.env` file in the root of the project.
    - Add any necessary API keys to this file, for example:
      ```
      OPENAI_API_KEY="your-openai-api-key"
      ```

## Running the Application

1.  **Launch the observability stack:**
    This project uses Docker Compose to manage the observability stack. Run the following command to start all the necessary services (OpenTelemetry Collector, Jaeger, Prometheus, Grafana) in the background:
    ```bash
    docker compose up -d
    ```

2.  **Run the application:**
    Execute the main application script from the root of the project:
    ```bash
    python main.py
    ```
    On the first run, you will be prompted to authenticate with your Google account in your web browser. After granting permissions, a `token.json` file will be created, and subsequent runs will be non-interactive.

## Observability Stack

The observability stack allows you to monitor and trace the application's behavior. The following services are included:

-   **Jaeger:** For distributed tracing.
    -   **URL:** [http://localhost:16686](http://localhost:16686)
    -   **Usage:** Select the `crewai_scheduling_assistant` service to view detailed traces of the application's execution, including agent interactions and LLM calls.

-   **Prometheus:** For metrics collection.
    -   **URL:** [http://localhost:9090](http://localhost:9090)
    -   **Usage:** You can use the Prometheus UI to query metrics scraped from the OpenTelemetry Collector.

-   **Grafana:** For metrics visualization.
    -   **URL:** [http://localhost:3000](http://localhost:3000)
    -   **Usage:** Log in to Grafana (default credentials: `admin`/`admin`) and add a new Prometheus data source pointing to `http://prometheus:9090`. You can then build dashboards to visualize key application metrics.
