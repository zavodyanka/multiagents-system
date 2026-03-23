import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("doctorserver")
doctors: list = json.loads(Path("../data/doctors.json").read_text())

@mpc.tool()
def list_doctors(city: str | None = None) -> list[dict]:
    """This tool returns a list of doctors practicing in a specific location. The search is case-insensitive.

    Args:
        city: The name of the city or town (e.g., "Wroclaw").

    Returns:
        A JSON string representing a list of doctors matching the criteria.
        If no criteria are provided, an error message is returned.
        Example: '[{"name": "Dr John James", "specialty": "Cardiology", ...}]'
    """
    if not city:
        return [{"error": "Please provide a city."}]

    target_city = city.strip().lower() if city else None

    return [
        doc
        for doc in doctors
        if not target_city or doc["address"]["city"].lower() == target_city
    ]

if __name__ == "__main__":
    mcp.run(transport="stdio")