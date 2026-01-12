/**
 * Agent adapter for integrating async tasks with AI SDK agents.
 * Provides prepareCall hooks and utilities for injecting completed tasks.
 */

import type { AsyncTaskAdapterConfig, AsyncTask } from './types';
import { getCompletedTasks, markTaskProcessed } from './core';

/**
 * Default formatter for task results.
 */
function defaultFormatTaskResults(tasks: AsyncTask[]): string {
  const results: string[] = [];

  for (const task of tasks) {
    if (task.toolName === 'get_delayed_weather') {
      const city = task.parameters.city as string;
      results.push(`Weather result for ${city}: ${task.result}`);
    } else {
      results.push(`${task.toolName} result: ${task.result}`);
    }
  }

  return results.join('\n');
}

/**
 * Default instructions template for injecting task results.
 */
const DEFAULT_INSTRUCTIONS_TEMPLATE = `Note: You now have completed task results available:
{results}

Please answer the user's current question naturally, and if appropriate, also mention the completed task results at the end of your response in a natural way, like 'By the way, I found out about...' or 'Also, regarding your earlier question about...' Make sure to include the actual result data when mentioning it.`;

/**
 * Creates a prepareCall function for ToolLoopAgent that injects completed tasks.
 */
export function createAsyncTaskPrepareCall<T extends { instructions?: string }>(
  config: AsyncTaskAdapterConfig,
): (args: {
  messages?: unknown;
  options?: unknown;
  [key: string]: unknown;
}) => Promise<T> {
  const { getUserId, formatTaskResults = defaultFormatTaskResults, instructionsTemplate = DEFAULT_INSTRUCTIONS_TEMPLATE } = config;

  return async ({ options, ...settings }) => {
    const userId = getUserId(options);

    // Get completed tasks for this user
    const completedTasks = getCompletedTasks(userId);
    console.log(
      `[Async Task] Found ${completedTasks.length} completed tasks for user ${userId}`,
    );

    // If there are completed tasks, inject them into the conversation
    if (completedTasks.length > 0) {
      // Format task results
      const formattedResults = formatTaskResults(completedTasks);

      // Mark all tasks as processed
      for (const task of completedTasks) {
        markTaskProcessed(task.taskId);
      }

      // Inject task results into instructions
      const taskMentionContent = instructionsTemplate.replace(
        '{results}',
        formattedResults,
      );

      const currentInstructions =
        (settings as { instructions?: string }).instructions || '';

      return {
        ...settings,
        instructions: `${currentInstructions}\n\n${taskMentionContent}`,
      } as T;
    }

    return settings as T;
  };
}

/**
 * Creates a context provider for passing userId to async tools.
 * Uses a closure to store the userId during agent execution.
 */
export function createUserIdContext(getUserId: (options: unknown) => string) {
  // Use a WeakMap to store userId per execution context
  // This avoids global state pollution
  const userIdMap = new WeakMap<object, string>();

  return {
    /**
     * Set the userId for the current execution context.
     */
    setUserId(context: object, options: unknown): void {
      const userId = getUserId(options);
      userIdMap.set(context, userId);
    },

    /**
     * Get the userId for the current execution context.
     */
    getUserId(context: object, fallback: string = 'anonymous'): string {
      return userIdMap.get(context) || fallback;
    },
  };
}

