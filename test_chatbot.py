#!/usr/bin/env python3
"""
Test Script for Asynchronous Gemini Chatbot

This script tests the end-to-end flow of the chatbot, focusing on
the asynchronous task handling and result re-integration.
"""

import asyncio
import sys
import uuid
import json
import httpx

# Configuration
API_BASE_URL = "http://localhost:8000/api"
USER_ID = str(uuid.uuid4())  # Generate a unique user ID for this test session


async def send_message(message: str) -> str:
    """
    Send a message to the chatbot API.

    Args:
        message: The message to send

    Returns:
        The chatbot's response
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/chat",
                json={"user_id": USER_ID, "message": message},
                timeout=30.0,
            )

            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
                return f"Error: {response.status_code}"

            data = response.json()
            return data["response"]

        except httpx.RequestError as e:
            print(f"Request error: {e}")
            return f"Request error: {e}"


async def check_health() -> bool:
    """
    Check the health of the API.

    Returns:
        True if the API is healthy, False otherwise
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL.replace('/api', '')}/health")

            if response.status_code != 200:
                print(f"Health check failed: {response.status_code} - {response.text}")
                return False

            data = response.json()
            print(f"Health status: {json.dumps(data, indent=2)}")
            return data["status"] == "ok"

        except httpx.RequestError as e:
            print(f"Health check error: {e}")
            return False


async def test_conversation():
    """
    Test a conversation with the chatbot, focusing on the asynchronous
    weather lookup and result re-integration.
    """
    print("\n=== Starting Conversation Test ===\n")

    # Check health first
    print("Checking API health...")
    if not await check_health():
        print("API is not healthy. Exiting.")
        return

    print("\n=== Conversation Flow ===\n")

    # Initial greeting
    print("User: Hello, can you help me today?")
    response = await send_message("Hello, can you help me today?")
    print(f"Bot: {response}\n")

    # Ask for weather (triggers async task)
    print("User: What's the weather like in London?")
    response = await send_message("What's the weather like in London?")
    print(f"Bot: {response}\n")

    # Continue conversation while the weather task is running
    print("User: While we wait, can you tell me a bit about London?")
    response = await send_message("While we wait, can you tell me a bit about London?")
    print(f"Bot: {response}\n")

    # Wait for a moment to allow the weather task to complete
    print("Waiting for 16 seconds to allow the weather task to complete...")
    await asyncio.sleep(16)

    # Ask about the weather result (should see re-integration)
    print("User: Did you find out about the weather in London?")
    response = await send_message("Did you find out about the weather in London?")
    print(f"Bot: {response}\n")

    # Ask a follow-up weather question
    print("User: What other cities can you tell me the weather for?")
    response = await send_message("What other cities can you tell me the weather for?")
    print(f"Bot: {response}\n")

    # Check health to see task statistics
    print("Checking final API health status...")
    await check_health()

    print("\n=== Conversation Test Complete ===\n")


if __name__ == "__main__":
    print(f"Starting test with user ID: {USER_ID}")

    try:
        asyncio.run(test_conversation())
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)
