from google.adk.agents import LlmAgent
from .domain_coordinators.dnb_coordinator import dnb_coordinator
from .domain_coordinators.data_science_coordinator import data_science_coordinator

root_agent = LlmAgent(
    name="root_agent",
    model="gemini-2.0-flash",
    description="System root coordinating all domain operations",
    instruction="""
    You are the Orkhon system root. Route requests to:
    - dnb_coordinator: For DNB API operations
    - data_science_coordinator: For analytics/BigQuery
    """,
    sub_agents=[dnb_coordinator, data_science_coordinator],
    output_key="system_response"
)
