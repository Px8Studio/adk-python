"""
Simple agent that uses DNB tools via GenAI Toolbox MCP server
"""
import asyncio
from toolbox_langchain import ToolboxClient
from langchain_google_vertexai import ChatVertexAI
from langgraph.prebuilt import create_react_agent

async def main():
    # Connect to MCP server
    client = ToolboxClient("http://localhost:5000")
    
    # Load the toolset
    tools = await client.aload_toolset("dnb-echo-tools")
    
    print(f"Loaded {len(tools)} tools from GenAI Toolbox")
    
    # Create LLM
    llm = ChatVertexAI(model="gemini-2.5-flash")
    
    # Create agent with LLM + tools
    agent = create_react_agent(llm, tools)
    
    # Run agent
    response = await agent.ainvoke({
        "messages": [("user", "Test the DNB API connection using the echo tool")]
    })
    
    print("\nAgent Response:")
    print(response["messages"][-1].content)

    # Agent can now invoke DNB API endpoints

if __name__ == "__main__":
    asyncio.run(main())
