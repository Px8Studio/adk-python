"""
Simple agent that uses DNB tools via GenAI Toolbox MCP server
"""
import asyncio
from toolbox_langchain import ToolboxClient
from langchain_google_vertexai import ChatVertexAI
import os

try:
    # Local central model cascade if available
    from .agents._common.config import get_llm_model, get_model  # type: ignore
except Exception:  # pragma: no cover
    def get_llm_model() -> str:
        return (
            os.getenv("ORKHON_LLM_MODEL")
            or os.getenv("ROOT_AGENT_MODEL")
            or os.getenv("GOOGLE_GEMINI_MODEL")
            or "gemini-2.5-flash"
        )
    def get_model(profile: str) -> str:
        return get_llm_model()
from langgraph.prebuilt import create_react_agent

async def main():
    # Connect to MCP server
    client = ToolboxClient("http://localhost:5000")
    
    # Load ALL available tools from the toolbox
    tools = await client.aload_toolset()
    
    print(f"Loaded {len(tools)} tools from GenAI Toolbox")
    print(f"Available tools: {[t.name for t in tools[:5]]}...")
    
    # Create LLM
    llm = ChatVertexAI(model=get_model("fast"))
    
    # Create agent with LLM + tools
    agent = create_react_agent(llm, tools)
    
    # Try a real statistics query
    response = await agent.ainvoke({
        "messages": [("user", "Get the latest exchange rates of the euro and gold price")]
    })
    
    print("\nAgent Response:")
    print(response["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
