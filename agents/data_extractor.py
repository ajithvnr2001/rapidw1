# agents/data_extractor.py (Minimal agent)
from crewai import Agent
from pydantic import ConfigDict

class DataExtractorAgent(Agent):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # Keep this for now

    def __init__(self): # Removed glpi_client argument
        super().__init__(
            role='Test Agent',
            goal='Test agent instantiation',
            backstory="""Test agent""",
            verbose=True,
            allow_delegation=False,
            tools=[] # No tools
        )
