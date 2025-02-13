# main.py (Modified for Direct Debugging)
from crewai import Crew, Task, Process
from agents.data_extractor import DataExtractorAgent
from core.glpi import GLPIClient
from core.config import settings
from typing import Dict
from fastapi import FastAPI, Request, HTTPException
from datetime import datetime
import json
from pydantic import ValidationError  # Import ValidationError

app = FastAPI()

def run_autopdf(incident_id: int, update_solution: bool = False) -> Dict:
    """Runs the AutoPDF workflow for a given incident ID."""

    glpi_client = GLPIClient()  # Initialize GLPIClient

    try:
        agent = DataExtractorAgent(glpi_client=glpi_client)  # Instantiate DataExtractorAgent
        print("DataExtractorAgent instantiated SUCCESSFULLY")  # Success message
        print(f"Agent glpi_client: {agent.glpi_client}") # Print agent.glpi_client
        print(f"Agent tools: {agent.tools}") # Print agent.tools
        return {"status": "success", "message": "DataExtractorAgent instantiated successfully and checked"}

    except ValidationError as e:
        print("ValidationError DETECTED in run_autopdf:")
        print(e)
        return {"status": "error", "message": "ValidationError during DataExtractorAgent instantiation", "error_details": str(e)}
    except Exception as e:
        print(f"Unexpected Error in run_autopdf: {e}")
        return {"status": "error", "message": f"Unexpected error: {e}"}
    finally:
        glpi_client.close_session()

@app.post("/webhook")
async def glpi_webhook(request: Request):
    # This whole function is now COMMENTED OUT for debugging
    pass
    # """Handles incoming webhooks from GLPI."""
    # try:
    #     body = await request.body()
    #     data = json.loads(body.decode())
    #     results = []

    #     if not isinstance(data, list):
    #         raise HTTPException(status_code=400, detail="Invalid webhook payload format")

    #     for event in data:
    #         if "event" not in event or "itemtype" not in event or "items_id" not in event:
    #             raise HTTPException(status_code=400, detail="Missing required fields in event")

    #         if event["itemtype"] == "Ticket":
    #             incident_id = int(event["items_id"])

    #             if event["event"] in ("add", "update"):
    #                 print("*" * 50)
    #                 print(f"Received event: {event['event']} for Ticket ID: {incident_id}")
    #                 print("*" * 50)
    #                 result = run_autopdf(incident_id, update_solution=True)
    #                 results.append(result)
    #             else:
    #                 print(f"Ignoring event type: {event['event']} for Ticket")
    #     return results
    # except json.JSONDecodeError:
    #     raise HTTPException(status_code=400, detail="Invalid JSON payload")
    # except Exception as e:
    #     print(f"Error in webhook: {e}")
    #     raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    # Call run_autopdf directly when accessing the root URL for testing
    test_result = run_autopdf(incident_id=123, update_solution=False) # Example incident ID
    return {"message": "AutoPDF is running!", "debug_result": test_result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port="8000")
