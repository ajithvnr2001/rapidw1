from crewai import Agent
from core.pdf_utils import create_pdf_from_text, create_pdf_from_html
from langchain.tools import tool
from typing import ClassVar, Any

class PDFGeneratorAgent(Agent):
    create_pdf_from_text_tool_method: ClassVar[Any]
    create_pdf_from_html_tool_method: ClassVar[Any]

    def __init__(self):
        super().__init__(
            role='PDF Generator',
            goal='Create well-formatted PDF reports',
            backstory="""Skilled in document formatting and PDF generation.
            Uses ReportLab to create professional-looking reports.""",
            tools=[self.create_pdf_from_text_tool_method, self.create_pdf_from_html_tool_method],
            verbose=True,
            allow_delegation=False
        )

    @tool
    def create_pdf_from_text_tool_method(self, content: str, title: str = "Incident Report") -> bytes:
        """Creates a PDF from plain text content."""
        if not content:
            raise ValueError("Content is required for PDF Generation.")
        return create_pdf_from_text(content, title)

    @tool
    def create_pdf_from_html_tool_method(self, content: str, title: str = "Incident Report") -> bytes:
        """Creates a PDF from HTML content."""
        if not content:
            raise ValueError("Content is required for PDF Generation.")
        return create_pdf_from_html(content, title)