# agents/data_extractor.py (CORRECTED - FOR REAL THIS TIME)
from core.glpi import GLPIClient
from langchain.tools import tool, Tool  # Import Tool
from typing import Optional, List
from pydantic import ConfigDict
from crewai import Agent

class DataExtractorAgent(Agent):
    glpi_client: GLPIClient  #  Declare glpi_client as a field!
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, glpi_client: GLPIClient):
        super().__init__(
            role='Data Extractor',
            goal='Retrieve and validate raw data from GLPI',
            backstory="""Expert in extracting data from various sources,
            especially GLPI. Resilient to API issues and data inconsistencies.""",
            tools=self.create_tools(),  # Use create_tools() method
            verbose=True,
            allow_delegation=False
        )
        self.glpi_client = glpi_client #Assignment remains the same

    def create_tools(self) -> List[Tool]:
        return [
            Tool(name="Get GLPI Incident Details", func=self.get_glpi_incident_details, description="Fetches details for a specific incident from GLPI."),
            Tool(name="Get GLPI Document Content", func=self.get_glpi_document_content, description="Fetches the content of a document from GLPI."),
            Tool(name="Get GLPI Ticket Solution", func=self.get_glpi_ticket_solution, description="Retrieves the solution field from a GLPI ticket."),
            Tool(name="Get GLPI Ticket Tasks", func=self.get_glpi_ticket_tasks, description="Retrieves the tasks from a GLPI ticket.")
        ]
    @tool
    def get_glpi_incident_details(self, incident_id: int) -> str:
        """Fetches details for a specific incident from GLPI."""
        try:
            incident = self.glpi_client.get_incident(incident_id)
            return str(incident)
        except Exception as e:
            print(f"Error in get_glpi_incident_details: {e}")
            return ""

    @tool
    def get_glpi_document_content(self, document_id: int) -> str:
        """Fetches the content of a document from GLPI."""
        try:
            document_content = self.glpi_client.get_document(document_id)
            return str(document_content)
        except Exception as e:
            print(f"Error in get_glpi_document_content: {e}")
            return ""

    @tool
    def get_glpi_ticket_solution(self, ticket_id: int) -> str:
        """Retrieves the solution field from a GLPI ticket."""
        try:
            return self.glpi_client.get_ticket_solution(ticket_id)
        except Exception as e:
            print(f"Error in get_glpi_ticket_solution: {e}")
            return ""

    @tool
    def get_glpi_ticket_tasks(self, ticket_id: int) -> str:
        """Retrieves the tasks from a GLPI ticket."""
        try:
            tasks = self.glpi_client.get_ticket_tasks(ticket_id)
            return str(tasks)
        except Exception as e:
            print(f"Error in get_glpi_ticket_tasks: {e}")
            return ""
