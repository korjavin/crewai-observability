import os
from dotenv import load_dotenv
from traceloop.sdk import Traceloop
from src.crewai_observability.auth import get_google_credentials
from src.crewai_observability.crew import SchedulingCrew

# Load environment variables from .env file
load_dotenv()

# Initialize OpenLLMetry
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"
Traceloop.init(app_name="crewai_scheduling_assistant")

def main():
    """
    Main function to run the scheduling crew.
    """
    # Get Google credentials
    creds = get_google_credentials()

    # Initialize the crew
    scheduling_crew = SchedulingCrew(creds=creds)

    # Kick off the crew
    scheduling_crew.crew().kickoff()

if __name__ == "__main__":
    main()
