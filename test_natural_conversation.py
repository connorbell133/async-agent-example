#!/usr/bin/env python3
"""
Natural Conversation Test for Asynchronous Gemini Chatbot
This script tests the natural conversation flow where the user continues
talking and the agent proactively mentions completed tasks.
"""

import asyncio
import json
import uuid
from typing import Dict, Any

import httpx


class NaturalConversationTester:
    """Tester class for natural conversation behavior."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.user_id = str(uuid.uuid4())

    async def send_message(self, message: str) -> Dict[str, Any]:
        """Send a message to the chatbot and return the response."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={"user_id": self.user_id, "message": message},
                    timeout=30.0,
                )

                if response.status_code == 200:
                    return response.json()

                return {"error": f"{response.status_code} - {response.text}"}

            except Exception as e:
                return {"error": str(e)}

    async def check_health(self) -> Dict[str, Any]:
        """Check the API health status."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/health", timeout=10.0)
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    def print_conversation(self, user_msg: str, bot_response: Dict[str, Any]):
        """Print the conversation in a nice format."""
        print(f"User: {user_msg}")
        if "error" in bot_response:
            print(f"Bot: Error: {bot_response['error']}")
        else:
            response_text = bot_response.get("response", "No response")
            print(f"Bot: {response_text}")
        print()

    async def run_natural_conversation_test(self):
        """Run the natural conversation test."""
        print(f"Starting natural conversation test with user ID: {self.user_id}")
        print()

        print("=== Starting Natural Conversation Test ===")
        print()

        # Check API health
        print("Checking API health...")
        health = await self.check_health()
        print(f"Health status: {json.dumps(health, indent=2)}")
        print()

        print("=== Natural Conversation Flow ===")
        print()

        # 1. Initial greeting
        user_msg = "Hello! I'm planning a trip to London next month."
        bot_response = await self.send_message(user_msg)
        self.print_conversation(user_msg, bot_response)

        # 2. Ask about weather (this will trigger the long-running task)
        user_msg = "What's the weather like in London right now?"
        bot_response = await self.send_message(user_msg)
        self.print_conversation(user_msg, bot_response)

        # 3. Continue talking about London attractions
        user_msg = "What are the must-see attractions in London?"
        bot_response = await self.send_message(user_msg)
        self.print_conversation(user_msg, bot_response)

        # 4. Ask about transportation
        user_msg = "How does the London Underground work? Is it easy to navigate?"
        bot_response = await self.send_message(user_msg)
        self.print_conversation(user_msg, bot_response)

        # 5. Ask about food
        user_msg = "What about food? What should I try while I'm there?"
        bot_response = await self.send_message(user_msg)
        self.print_conversation(user_msg, bot_response)

        # 6. Ask about neighborhoods (by now the weather task should be complete)
        print("Weather task should be completed by now...")
        user_msg = "Which neighborhoods would you recommend for a first-time visitor?"
        bot_response = await self.send_message(user_msg)
        self.print_conversation(user_msg, bot_response)

        # 7. Ask about budget
        user_msg = "London seems expensive. Any tips for traveling on a budget?"
        bot_response = await self.send_message(user_msg)
        self.print_conversation(user_msg, bot_response)

        # 8. Ask about timing
        user_msg = "How many days would you recommend for a first visit?"
        bot_response = await self.send_message(user_msg)
        self.print_conversation(user_msg, bot_response)

        # Check final health
        print("Checking final API health status...")
        health = await self.check_health()
        print(f"Health status: {json.dumps(health, indent=2)}")
        print()

        print("=== Natural Conversation Test Complete ===")


async def main():
    """Main function to run the test."""
    tester = NaturalConversationTester()

    try:
        await tester.run_natural_conversation_test()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Test failed with error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
