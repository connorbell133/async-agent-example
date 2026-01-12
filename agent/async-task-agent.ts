import { anthropic } from '@ai-sdk/anthropic';
import { InferAgentUIMessage } from 'ai';
import { delayedWeatherTool } from '@/tools/delayed-weather-tool';
import {
  ToolLoopAgentAsync,
  asyncAgentCallOptionsSchema,
  type AsyncAgentCallOptions,
} from '@/lib/async-tasks';

/**
 * Call options schema for the async task agent.
 * Uses the built-in schema from ToolLoopAgentAsync.
 */
export const asyncTaskAgentCallOptionsSchema = asyncAgentCallOptionsSchema;

export type AsyncTaskAgentCallOptions = AsyncAgentCallOptions;

/**
 * Agent that uses ToolLoopAgentAsync with built-in async task support.
 *
 * This is a much simpler implementation compared to manually wiring up
 * ToolLoopAgent with async tools. The ToolLoopAgentAsync class handles:
 * - Wrapping tools for async background execution
 * - Storing completed task results
 * - Injecting completed task results into the conversation context
 * - Managing userId context for multi-user support
 */
export const asyncTaskAgent = new ToolLoopAgentAsync({
  model: anthropic('claude-sonnet-4-5'),
  callOptionsSchema: asyncTaskAgentCallOptionsSchema,
  instructions: `You are a helpful AI assistant. You can use tools when needed, but you should also be able to answer general questions and have conversations. When tools are available, use them when appropriate, but don't limit yourself to only tool-related responses. Be conversational and helpful.

When you have completed task results available, mention them naturally in your response using phrases like "By the way, regarding..." or "Also, I found out about..." without being asked directly.`,

  // Async tools execute in the background and store results for later
  asyncTools: {
    get_delayed_weather: {
      tool: delayedWeatherTool,
      immediateResponse: ({ city }) =>
        `I'm fetching the weather for ${city}. This might take about 15 seconds. Feel free to ask me anything else in the meantime!`,
    },
  },
});

export type AsyncTaskAgentMessage = InferAgentUIMessage<typeof asyncTaskAgent>;
