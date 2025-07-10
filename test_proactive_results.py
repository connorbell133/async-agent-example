#!/usr/bin/env python3
"""
Proactive Results Test for Asynchronous Gemini Chatbot
This script demonstrates how the agent proactively mentions completed tasks
in natural conversation without being directly asked.
"""

import asyncio
import uuid
from typing import Dict, Any

import httpx


class ProactiveResultsTester:
    """Tester class for proactive results behavior."""

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
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"❌ Error sending message: {e}")
                return {"response": f"Error: {e}"}

    def extract_text_response(self, response: Dict[str, Any]) -> str:
        """Extract the actual text response from the API response."""
        response_text = response.get("response", "")

        # Handle different response formats
        if response_text.startswith('text: "') and response_text.endswith('"'):
            # Remove the text: prefix and quotes, handle escaped quotes and newlines
            clean_text = (
                response_text[7:-1]
                .replace('\\"', '"')
                .replace("\\n", "\n")
                .replace("\\t", "\t")
            )
            return clean_text
        if response_text.startswith('text: "text: "') and response_text.endswith('""'):
            # Handle double-nested text format
            clean_text = (
                response_text[14:-2]
                .replace('\\"', '"')
                .replace("\\n", "\n")
                .replace("\\t", "\t")
            )
            return clean_text

        # Handle simple responses and clean up any remaining escapes
        return (
            response_text.replace("\\n", "\n").replace('\\"', '"').replace("\\t", "\t")
        )

    async def run_test(self):
        """Run the proactive results test."""
        print("🧪 Testing Proactive Results Behavior")
        print(f"User ID: {self.user_id}")
        print("=" * 60)

        # Step 1: Initial greeting
        print("\nStep 1: Initial greeting")
        response = await self.send_message("Hello! I'm visiting London soon.")
        print("👤 User: Hello! I'm visiting London soon.")
        print(f"🤖 Bot: {self.extract_text_response(response)}")

        # Step 2: Request weather (triggers 15-second task)
        print("\nStep 2: Request weather (triggers 15-second task)")
        response = await self.send_message("Can you get me the weather for London?")
        print("👤 User: Can you get me the weather for London?")
        print(f"🤖 Bot: {self.extract_text_response(response)}")

        # Step 3: Ask about something completely different while waiting
        print("\nStep 3: Ask about something different while waiting")
        response = await self.send_message(
            "What's the best way to get from Heathrow to central London?"
        )
        print("👤 User: What's the best way to get from Heathrow to central London?")
        print(f"🤖 Bot: {self.extract_text_response(response)}")

        # Step 4: Ask another unrelated question
        print("\nStep 4: Another unrelated question")
        response = await self.send_message("What are some good museums to visit?")
        print("👤 User: What are some good museums to visit?")
        print(f"🤖 Bot: {self.extract_text_response(response)}")

        # Step 5: Wait for weather task to complete, then ask another question
        print("\nStep 5: Wait for weather task to complete (15+ seconds total)")
        print("⏳ Waiting for weather task to finish...")
        await asyncio.sleep(
            18
        )  # Wait long enough for 15-second weather task to complete
        response = await self.send_message("Are there any good parks for jogging?")
        print("👤 User: Are there any good parks for jogging?")
        print(f"🤖 Bot: {self.extract_text_response(response)}")

        # Check if the weather result was mentioned proactively
        response_text = self.extract_text_response(response)
        if "weather" in response_text.lower() and (
            "by the way" in response_text.lower()
            or "regarding" in response_text.lower()
        ):
            print("✅ SUCCESS: Agent proactively mentioned completed weather task!")
        else:
            print("❌ ISSUE: Agent didn't proactively mention the weather result")

        # Step 6: One more question to see if it mentions it again (it shouldn't)
        print("\nStep 6: Another question to ensure task isn't mentioned again")
        response = await self.send_message("What about shopping areas?")
        print("👤 User: What about shopping areas?")
        print(f"🤖 Bot: {self.extract_text_response(response)}")

        # Check that weather isn't mentioned again
        response_text = self.extract_text_response(response)
        if "weather" not in response_text.lower():
            print("✅ SUCCESS: Agent didn't repeat the weather result (good!)")
        else:
            print(
                "⚠️  NOTE: Agent mentioned weather again (may be contextually appropriate)"
            )

        print("=" * 60)
        print("🎯 Test Complete!")
        print("\nExpected behavior:")
        print("- Agent should answer questions normally while weather task runs")
        print("- Agent should proactively mention weather result when it's ready")
        print(
            "- Agent should use natural language like 'By the way...' or 'Regarding...'"
        )
        print("- Agent should not repeat the same result multiple times")


async def main():
    """Main function to run the test."""
    tester = ProactiveResultsTester()

    try:
        await tester.run_test()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Test failed with error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
