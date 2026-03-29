import asyncio

from rich.console import Console
from rich.markdown import Markdown

# from a2a.client import (
#     Client,
#     ClientConfig,
#     ClientFactory,
#     create_text_message_object,
# )
# from a2a.types import AgentCard, Artifact, Message, Task
# from a2a.utils.message import get_message_text
import os
from google.adk.agents import SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from dotenv import load_dotenv
import logging
import warnings

from google.adk.runners import InMemoryRunner

logging.disable(level=logging.WARNING)
warnings.filterwarnings("ignore")


load_dotenv()

host = os.environ.get("AGENT_HOST", "localhost")
pzu_port = os.environ.get("POLICY_AGENT_PORT")
research_port = os.environ.get("RESEARCH_AGENT_PORT")

print(f"{host}, {pzu_port}, {research_port}")

pzu_agent = RemoteA2aAgent(name="pzu_agent", agent_card=f"http://{host}:{pzu_port}")
print("\tℹ️", f"{pzu_agent.name} initialized")

health_research_agent = RemoteA2aAgent(
    name="health_research_agent", agent_card=f"http://{host}:{research_port}"
)
print("\tℹ️", f"{health_research_agent.name} initialized")

root_agent = SequentialAgent(
    name="root_agent",
    description="Healthcare Routing Agent",
    sub_agents=[
        pzu_agent,
        health_research_agent,
    ],
)


async def main():
    # prompt = "How much would I pay for mental health therapy?"
    prompt = "How do I get mental health therapy?"

    print("Running Healthcare Workflow Agent")

    runner = InMemoryRunner(root_agent)

    for event in await runner.run_debug(prompt, quiet=True):
        if event.is_final_response() and event.content:
            console = Console()
            console.print(Markdown(event.content.parts[0].text))


if __name__ == "__main__":
    asyncio.run(main())
# def display_agent_card(agent_card: AgentCard) -> None:
#     def esc(text: str) -> str:
#         """Escapes pipe characters for Markdown table compatibility."""
#         return str(text).replace("|", r"\|")
#
#     # --- Part 1: Main Metadata Table ---
#     md_parts = [
#         "### Agent Card Details",
#         "| Property | Value |",
#         "| :--- | :--- |",
#         f"| **Name** | {esc(agent_card.name)} |",
#         f"| **Description** | {esc(agent_card.description)} |",
#         f"| **Version** | `{esc(agent_card.version)}` |",
#         f"| **URL** | [{esc(agent_card.url)}]({agent_card.url}) |",
#         f"| **Protocol Version** | `{esc(agent_card.protocol_version)}` |",
#     ]
#
#     # --- Part 2: Skills Table ---
#     if agent_card.skills:
#         md_parts.extend(
#             [
#                 "\n#### Skills",
#                 "| Name | Description | Examples |",
#                 "| :--- | :--- | :--- |",
#             ]
#         )
#         for skill in agent_card.skills:
#             examples_str = (
#                 "<br>".join(f"• {esc(ex)}" for ex in skill.examples)
#                 if skill.examples
#                 else "N/A"
#             )
#             md_parts.append(
#                 f"| **{esc(skill.name)}** | {esc(skill.description)} | {examples_str} |"
#             )
#
#     # Join all parts and display
#     display(Markdown("\n".join(md_parts)))
#
# async with httpx.AsyncClient(timeout=100.0) as httpx_client:
#     # Step 1: Create a client
#     client: Client = await ClientFactory.connect(
#         f"http://{host}:{port}",
#         client_config=ClientConfig(
#             httpx_client=httpx_client,
#         ),
#     )
#
#     # Step 2: Discover the agent by fetching its card
#     agent_card = await client.get_card()
#     display_agent_card(agent_card)
#
#     # Step 3: Create the message using a convenient helper function
#     message = create_text_message_object(content=prompt)
#
#     display(Markdown(f"**Sending prompt:** `{prompt}` to the agent..."))
#
#     # Step 4: Send the message and await the final response.
#     responses = client.send_message(message)
#
#     text_content = ""
#
#     # Step 5: Process the responses from the agent
#     async for response in responses:
#         if isinstance(response, Message):
#             # The agent replied directly with a final message
#             print(f"Message ID: {response.message_id}")
#             text_content = get_message_text(response)
#         # response is a ClientEvent
#         elif isinstance(response, tuple):
#             task: Task = response[0]
#             print(f"Task ID: {task.id}")
#             if task.artifacts:
#                 artifact: Artifact = task.artifacts[0]
#                 print(f"Artifact ID: {artifact.artifact_id}")
#                 text_content = get_message_text(artifact)
#
#     display(Markdown("### Final Agent Response\n-----"))
#     if text_content:
#         display(Markdown(text_content))
#     else:
#         display(
#             Markdown(
#                 """**No final text content received or task did not
#                 complete successfully.**"""
#             )
#         )
