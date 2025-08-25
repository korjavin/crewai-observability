import os
from dotenv import load_dotenv
from traceloop.sdk import Traceloop
from crewai_observability.crew import SchedulingCrew

def main():
    """
    Main function to run the crew.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Initialize OpenLLMetry
    Traceloop.init(app_name="crewai_scheduling_assistant")

    # Set the OTLP endpoint
    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"

    print("Kicking off the crew...")
    crew = SchedulingCrew()
    crew.crew().kickoff()
    print("Crew execution finished.")

if __name__ == "__main__":
    main()
