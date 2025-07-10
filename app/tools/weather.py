"""
Weather Tool Module

This module provides a simulated weather tool that returns hardcoded weather data
after a delay to demonstrate long-running asynchronous tasks.
"""

import asyncio
import logging
from typing import Dict

from app.models.chat import ToolDefinition, ToolParameter

# Configure logging
logger = logging.getLogger(__name__)

# Define the weather tool
WEATHER_TOOL = ToolDefinition(
    name="get_delayed_weather",
    description=(
        "Get the weather forecast for a city. This is a long-running operation "
        "that may take 15 seconds."
    ),
    parameters=[
        ToolParameter(
            name="city",
            description="The name of the city to get weather for",
            type="string",
            required=True,
        )
    ],
)


async def get_delayed_weather(city: str) -> str:
    """
    Get the weather for a city with a simulated delay.

    This is a mock implementation that returns hardcoded weather data
    after a 15-second delay to simulate a long-running API call.

    Args:
        city: The name of the city to get weather for

    Returns:
        A string containing the weather forecast
    """
    logger.info("Getting weather for %s (with 15s delay)", city)

    # Simulate a long-running API call
    await asyncio.sleep(15)

    # Return a hardcoded weather result
    # In a real implementation, this would call a weather API
    weather_conditions: Dict[str, Dict[str, str]] = {
        "London": {"temp": "15°C", "condition": "partly cloudy", "humidity": "72%"},
        "New York": {"temp": "22°C", "condition": "sunny", "humidity": "60%"},
        "Tokyo": {"temp": "19°C", "condition": "rainy", "humidity": "85%"},
        "Sydney": {"temp": "27°C", "condition": "clear", "humidity": "55%"},
        "Paris": {"temp": "14°C", "condition": "overcast", "humidity": "70%"},
    }

    # Get weather for the specific city or use a default response
    city_weather = weather_conditions.get(
        city, {"temp": "18°C", "condition": "partly cloudy", "humidity": "65%"}
    )

    return (
        f"The weather in {city} is currently {city_weather['temp']} and "
        f"{city_weather['condition']} with {city_weather['humidity']} humidity."
    )
