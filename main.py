# main.py (CORRECTED - FINALLY)
from crewai import Crew, Task, Process
from agents.data_extractor import DataExtractorAgent
from agents.data_processor import DataProcessorAgent
from agents.query_handler import QueryHandlerAgent
from agents.pdf_generator import PDFGeneratorAgent
from agents.search_indexer import SearchIndexerAgent
from core.glpi import GLPIClient
from core.config import settings
from typing import Dict
from fastapi import FastAPI, Request, HTTPException
from datetime import datetime
import json

app = FastAPI()

def run_autopdf(incident_id: int, update_solution: bool = False) -> Dict:
    """Runs the AutoPDF workflow for a given incident ID."""

    glpi_client = GLPIClient()  # Initialize inside the function

    try:
        data_extractor_agent = DataExtractorAgent(glpi_client=glpi_client)
        data_processor_agent = DataProcessorAgent()
        query_handler_agent = QueryHandlerAgent()
        pdf_generator_agent = PDFGeneratorAgent()
        search_indexer_agent = SearchIndexerAgent()

        extract_incident_task = Task(
            description=f"Extract details for GLPI incident ID {incident_id}",
            agent=data_extractor_agent,
            expected_output="Raw data of the incident",
        )
        extract_solution_task = Task(
            description=f"Extract solution for GLPI incident ID {incident_id}",
            agent=data_extractor_agent,
            expected_output="Raw solution data",
        )
        extract_tasks_task = Task(
            description=f"Extract tasks for GLPI incident ID {incident_id}",
            agent=data_extractor_agent,
            expected_output="Raw tasks data",
        )
        document_id = 12345  # TODO: Get this dynamically from GLPI.  Placeholder.
        extract_document_task = Task(
            description=f"Extract content of document ID {document_id}",
            agent=data_extractor_agent,
            expected_output="Raw document content",
        )

        # IMPORTANT:  Tasks now receive the *results* of previous tasks as inputs.
        process_data_task = Task(
            description="Process the extracted data from GLPI",
            agent=data_processor_agent,
            expected_output="Cleaned and structured data",
            context=[data_extractor_agent, data_processor_agent,query_handler_agent,pdf_generator_agent,search_indexer_agent],  # Provide the AGENTS for context
            # We'll pass the actual data as arguments (see below).
        )
        generate_content_task = Task(
            description="Generate report content using RAG",
            agent=query_handler_agent,
            expected_output="Generated content for the report",
            context=[data_processor_agent], # Pass the agent!
        )

        create_pdf_task = Task(
            description="Create a PDF report",
            agent=pdf_generator_agent,
            expected_output="PDF file as bytes.",
            context=[query_handler_agent],  # Pass the agent!
        )
        index_pdf_task = Task(
            description="Store PDF and index",
            agent=search_indexer_agent,
            expected_output="Confirmation message",
            context=[create_pdf_task, process_data_task, data_processor_agent, pdf_generator_agent, query_handler_agent], # Pass the agents!
        )

        crew = Crew(
            agents=[
                data_extractor_agent,
                data_processor_agent,
                query_handler_agent,
                pdf_generator_agent,
                search_indexer_agent,
            ],
            tasks=[
                extract_incident_task,
                extract_solution_task,
                extract_tasks_task,
                extract_document_task,
                process_data_task,
                generate_content_task,
                create_pdf_task,
                index_pdf_task,
            ],
            process=Process.sequential,
            verbose=2,
        )

        result = crew.kickoff()  # Result is a single value, the output of the LAST task.
        return result

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
                    if event["event"] == "update":
                         run_autopdf(incident_id, update_solution=True)
                    else:
                        run_autopdf(incident_id)  # Don't update solution on add
                else:
                    print(f"Ignoring event type: {event['event']} for Ticket")

        return {"message": "Webhook received and processed"}  # Consistent return
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        print(f"Error in webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/")
async def root():
    return {"message": "AutoPDF is running!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port="8000")
