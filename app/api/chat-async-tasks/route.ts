import { asyncTaskAgent, AsyncTaskAgentCallOptions } from '@/agent/async-task-agent';
import { createAgentUIStreamResponse, validateUIMessages, UIMessage } from 'ai';

export async function POST(req: Request) {
  const body = await req.json();
  const { messages, userId } = body;

  const uiMessages = await validateUIMessages<UIMessage>({ messages });

  // Prepare call options with userId
  const options: AsyncTaskAgentCallOptions = {
    userId: userId || 'anonymous',
  };

  return createAgentUIStreamResponse({
    agent: asyncTaskAgent,
    uiMessages,
    options,
  });
}

