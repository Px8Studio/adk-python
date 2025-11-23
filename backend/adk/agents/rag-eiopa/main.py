# --- Define the specialized agents first (we'll detail them next) ---
# ingestion_agent = ...
# comparison_agent = ...
import pandas as pd
from pypdf import PdfReader
from google.adk.tools import ToolContext
from google.adk.agents import LlmAgent, FunctionTool
from google.adk.agents import BaseAgent, InvocationContext, Event
from typing import AsyncGenerator
import os
from google.adk.sessions import Part  # Add this import for ADK artifact part

# Tool for PDFs
def process_pdf(file_path: str, tool_context: ToolContext) -> dict:
    """Extracts text from a PDF file and saves it as an artifact."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        # Save the extracted text as a new artifact for the Indexing Agent
        artifact_name = f"processed_{os.path.basename(file_path)}.txt"
        text_part = Part(text=text)
        version = tool_context.save_artifact(artifact_name, text_part)

        return {"status": "success", "artifact_name": artifact_name, "version": version}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Tool for Excel files
def process_excel(file_path: str, tool_context: ToolContext) -> dict:
    """Extracts text from an Excel file (all sheets) and saves it as an artifact."""
    try:
        xls = pd.ExcelFile(file_path)
        full_text = ""
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            full_text += f"--- Sheet: {sheet_name} ---\n"
            full_text += df.to_string() + "\n\n"


        artifact_name = f"processed_{os.path.basename(file_path)}.txt"
        text_part = Part(text=full_text)
        version = tool_context.save_artifact(artifact_name, text_part)
        version = tool_context.save_artifact(artifact_name, text_part)

        return {"status": "success", "artifact_name": artifact_name, "version": version}
    except Exception as e:
        return {"status": "error", "message": str(e)}



class IngestionAgent(BaseAgent):
    """A custom agent that scans a folder and calls processing tools."""
    # Assume pdf_tool and excel_tool are FunctionTool-wrapped versions of the functions above
    pdf_tool: FunctionTool
    excel_tool: FunctionTool
    model_config = {"arbitrary_types_allowed": True}

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        folder_path = ctx.session.state.get("folder_to_process")
        if not folder_path:
            yield Event(author=self.name, content="Error: No folder path provided in state.")
            return

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            tool_to_run = None
            if filename.lower().endswith('.pdf'):
                tool_to_run = self.pdf_tool
            elif filename.lower().endswith(('.xlsx', '.xls')):
                tool_to_run = self.excel_tool

            if tool_to_run:
                # The tool's run_async will handle creating the artifact
                async for event in tool_to_run.run_async(args={"file_path": file_path}, tool_context=ctx):
                    yield event
        yield Event(author=self.name, content=f"Finished processing folder: {folder_path}")

# Instantiate the ingestion_agent with dummy FunctionTool instances (replace with actual tools as needed)
ingestion_agent = IngestionAgent(
    name="IngestionAgent",
    pdf_tool=FunctionTool(process_pdf, name="process_pdf"),
    excel_tool=FunctionTool(process_excel, name="process_excel")
)

from google.adk.tools import VertexAiSearchTool

# You must configure this with your Vertex AI Search datastore ID
# This datastore should be configured to index the GCS bucket where your
# processed text files are stored.
# e.g., "projects/your-proj/locations/global/collections/default_collection/dataStores/my-docs-store"
DATASTORE_ID = "YOUR_VERTEX_AI_SEARCH_DATASTORE_ID"

retrieval_tool = VertexAiSearchTool(data_store_id=DATASTORE_ID)

comparison_agent = LlmAgent(
    name="ComparisonAgent",
    model="gemini-2.5-pro", # A more powerful model for analysis
    tools=[retrieval_tool],
    instruction="""You are a documentation analyst. The user wants to compare two sets of documents (e.g., 'pension' vs 'insurance').
    1. Use the search tool to retrieve relevant information for the user's query from BOTH sources. You can filter your search by source metadata if available.
    2. Analyze the retrieved documents from both sources.
    3. Synthesize a clear, concise report summarizing the key similarities and differences. Use headings and bullet points for clarity.
    """
)

# --- The Coordinator Agent ---
coordinator_agent = LlmAgent(
    name="DocumentationComparatorCoordinator",
    model="gemini-2.5-flash", # A fast model is good for orchestration
    instruction="""You are the coordinator for a document comparison system.
    When a user asks to compare folders, first delegate to the 'IngestionAgent' to process the documents.
    Then, delegate to the 'ComparisonAgent' to analyze the differences and generate a report.
    """,
    description="Coordinates the process of ingesting and comparing documentation folders.",
    # The sub_agents are the specialists it can delegate to.
    sub_agents=[ingestion_agent, comparison_agent]
)

# This will be our final root_agent
root_agent = coordinator_agent
