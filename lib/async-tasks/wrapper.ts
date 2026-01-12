/**
 * Async tool wrapper.
 * Converts any AI SDK tool into an async tool that executes in the background.
 */

import { tool, type CoreTool } from 'ai';
import type { AsyncTaskWrapperOptions } from './types';
import { storeCompletedTask } from './core';

/**
 * Creates an async wrapper around an existing tool.
 * The wrapper returns immediately while executing the original tool in the background.
 *
 * @param originalTool - The original tool to wrap
 * @param options - Configuration options for the async wrapper
 * @returns A new tool that executes the original tool asynchronously
 */
export function createAsyncTool<T extends CoreTool>(
  originalTool: T,
  options: AsyncTaskWrapperOptions,
): T {
  const { toolName, getUserId, immediateResponse } = options;

  // Create a wrapper tool with the same schema as the original
  const asyncTool = tool({
    description: originalTool.description,
    inputSchema: originalTool.inputSchema,
    async execute(params, context) {
      const userId = getUserId();

      // Execute the original tool in the background
      if (originalTool.execute) {
        // Fire and forget - execute in background
        (async () => {
          try {
            // Execute the original tool (potentially long-running)
            const result = await originalTool.execute(params, context);
            // Store the completed task result for later retrieval
            const taskId = storeCompletedTask(
              userId,
              toolName,
              params as Record<string, unknown>,
              String(result),
            );
            console.log(
              `[Async Task] Stored completed task ${taskId} for user ${userId}:`,
              result,
            );
          } catch (error) {
            console.error(`[Async Task] Error executing ${toolName}:`, error);
          }
        })();
      }

      // Return immediately with a user-friendly message
      if (immediateResponse) {
        return immediateResponse(params as Record<string, unknown>);
      }

      // Default immediate response
      return `I'm processing your request for ${toolName}. This might take a moment. Feel free to ask me anything else in the meantime!`;
    },
  }) as T;

  return asyncTool;
}

