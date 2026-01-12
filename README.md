# Async Agent Example with AI SDK

This project demonstrates how to build AI agents with **asynchronous background task execution** using the [AI SDK](https://ai-sdk.dev/docs), [Next.js](https://nextjs.org/), and [Anthropic's Claude](https://anthropic.com).

## Features

- **Async Tool Execution**: Tools can run in the background while the agent remains responsive
- **Task Result Injection**: Completed task results are automatically injected into conversation context
- **Multi-User Support**: Built-in userId context management for handling multiple concurrent users
- **Streaming UI**: Real-time streaming responses using AI SDK's RSC capabilities
- **Type-Safe**: Full TypeScript support with Zod schemas

## How It Works

The core innovation is the `ToolLoopAgentAsync` class, which wraps standard AI SDK tools to enable:

1. **Background execution**: Long-running tools execute asynchronously without blocking the agent
2. **Immediate responses**: Agent provides immediate feedback while tasks run in the background
3. **Automatic result delivery**: Completed task results are injected into subsequent conversations
4. **Clean separation**: Simple API that abstracts away the complexity of async task management

## Getting Started

### Prerequisites

1. Sign up at [Anthropic's Console](https://console.anthropic.com/)
2. Create an API key from the [API Keys page](https://console.anthropic.com/settings/keys)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd async-agent-example

# Install dependencies
pnpm install
```

### Configuration

1. Copy the example environment file:
   ```bash
   cp .env.local.example .env.local
   ```

2. Add your Anthropic API key to `.env.local`:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

3. Start the development server:
   ```bash
   pnpm dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
agent/
  async-task-agent.ts          # Agent configuration with async tools
lib/
  async-tasks/
    agent.ts                    # ToolLoopAgentAsync implementation
    adapter.ts                  # AI SDK adapter integration
    wrapper.ts                  # Async tool wrapper logic
    core.ts                     # Core async task management
tools/
  delayed-weather-tool.ts       # Example async tool (simulates 15s delay)
app/
  chat-async-tasks/             # Demo chat interface
```

## Learn More

- [AI SDK Documentation](https://ai-sdk.dev/docs) - Learn about the AI SDK
- [Anthropic Claude](https://anthropic.com/claude) - Learn about Claude models
- [Next.js Documentation](https://nextjs.org/docs) - Learn about Next.js
- [Vercel AI Playground](https://ai-sdk.dev/playground) - Experiment with AI models
