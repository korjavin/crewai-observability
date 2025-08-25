from traceloop.sdk import Traceloop
import os

# Configure the exporter endpoint to point to the OTel Collector
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"

Traceloop.init(app_name="crewai_scheduling_assistant")

def main():
    """
    Main function to run the crew.
    """
    print("Running the crew...")
    # In a real implementation, this is where you would kick off the crew.
    # from .crew import SchedulingCrew
    # crew = SchedulingCrew()
    # crew.crew().kickoff()

if __name__ == "__main__":
    main()
