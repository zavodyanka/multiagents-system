import asyncio
import os
from typing import TYPE_CHECKING

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from langchain.agents import create_agent
from langchain_litellm import ChatLiteLLM
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StdioConnection
from langgraph_a2a_server import A2AServer

from helpers import setup_env

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph

def main():
    print("Running Healthcare Clinic Agent")
    setup_env()

    HOST = os.getenv("AGENT_HOST", "localhost")
    PORT = int(os.getenv("CLINIC_AGENT_PORT"))

    mcp_client = MultiServerMCPClient(
        {
            "find_healthcare_clinics": StdioConnection(
                transport="stdio",
                command="uv",
                args=["run", "mcp_server.py"],
            )
        }
    )

    agent: CompiledStateGraph = create_agent(
        model=ChatLiteLLM(
            model="openai/gpt-4o",
            max_tokens=1000,
        ),
        tools=asyncio.run(mcp_client.get_tools()),
        name="HealthcareProviderAgent",
        system_prompt="Find and list healthcare providers using the find_healthcare_providers MCP Tool. Only provide information that is given to you from the find_healthcare_providers tool results.",
    )

    agent_card = AgentCard(
        name="HealthcareClinicAgent",
        description="Find healthcare clinics by location and specialty.",
        url=f"http://{HOST}:{PORT}/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[
            AgentSkill(
                id="find_healthcare_clinics",
                name="Find Healthcare Clinics",
                description="Finds clinics based on location/specialty.",
                tags=["healthcare", "clinics", "doctor", "psychiatrist"],
                examples=[
                    "Are there any Psychiatrists near me in Wroclaw?",
                    "Find a pediatrician in Poznan",
                ],
            )
        ],
    )

    server = A2AServer(
        graph=agent,
        agent_card=agent_card,
        host=HOST,
        port=PORT,
    )

    server.serve(app_type="starlette")

if __name__ == "__main__":
    main()