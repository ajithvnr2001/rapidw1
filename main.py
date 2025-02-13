# main.py (Simplified for Debugging)
from crewai import Crew, Task, Process
from agents.data_extractor import DataExtractorAgent
from agents.data_processor import DataProcessorAgent  # Import, but not used in simplified version
from agents.query_handler import QueryHandlerAgent # Import, but not used
from agents.pdf_generator import PDFGeneratorAgent # Import, but not used
from agents.search_indexer import SearchIndexerAgent # Import, but not used
from core.glpi import GLPIClient
from core.config import settings
from typing import Dict
from fastapi import FastAPI, Request, HTTPException
from datetime import datetime
import json

app = FastAPI()

def run_autopdf(incident_id: int, update_solution: bool = False) -> Dict:
    """Runs the AutoPDF workflow for a given incident ID."""

    glpi_client = GLPIClient()  # Keep GLPIClient instantiation for now

    try:
        # Use the simplified DataExtractorAgent, no glpi_client argument
        data_extractor_agent = DataExtractorAgent() # No glpi_client argument
        data_processor_agent = DataProcessorAgent() # Not used in simplified version
        query_handler_agent = QueryHandlerAgent() # Not used
        pdf_generator_agent = PDFGeneratorAgent() # Not used
        search_indexer_agent = SearchIndexerAgent() # Not used

        # process_data_task = Task(  # Keep ONLY this Task definition
        #     description="Process the extracted data from GLPI",
        #     agent=data_processor_agent,
        #     expected_output="Cleaned and structured data",
        #     context=[data_extractor_agent],
        # )

        # crew = Crew(  # Comment out Crew definition
        #     agents=[
        #         data_extractor_agent,
        #         data_processor_agent,
        #         query_handler_agent,
        #         pdf_generator_agent,
        #         search_indexer_agent,
        #     ],
        #     tasks=[
        #         process_data_task, # Keep ONLY process_data_task in tasks
        #     ],
        #     process=Process.sequential,
        #     verbose=2,
        # )

        # result = crew.kickoff()  # Comment out kickoff

        return {"status": "success", "message": "Simplified agent instantiated and tasks commented out"} # Modified return

    except Exception as e:
        print(f"Error in run_autopdf: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        glpi_client.close_session()


@app.post("/webhook")
async def glpi_webhook(request: Request):
    """Handles incoming webhooks from GLPI."""
    try:
        body = await request.body()
        data = json.loads(body.decode())
        results = []

        if not isinstance(data, list):
            raise HTTPException(status_code=400, detail="Invalid webhook payload format")

        for event in data:
            if "event" not in event or "itemtype" not in event or "items_id" not in event:
                raise HTTPException(status_code=400, detail="Missing required fields in event")

            if event["itemtype"] == "Ticket":
                incident_id = int(event["items_id"])

                if event["event"] in ("add", "update"):
                    print("*" * 50)
                    print(f"Received event: {event['event']} for Ticket ID: {incident_id}")
                    print("*" * 50)
                    result = run_autopdf(incident_id) # Call run_autopdf
                    results.append(result)
                else:
                    print(f"Ignoring event type: {event['event']} for Ticket")
        return results
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        print(f"Error in webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "AutoPDF is running!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port="8000")
