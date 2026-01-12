/**
 * Async Task System for AI SDK
 *
 * A containerized, standalone system for handling asynchronous tool execution
 * with AI SDK agents. This module provides:
 *
 * - ToolLoopAgentAsync: A drop-in replacement for ToolLoopAgent with async support
 * - Core task storage and retrieval
 * - Tool wrappers for converting sync tools to async
 * - Agent adapters for seamless integration
 * - Extensible storage backends
 *
 * @example
 * ```ts
 * import { ToolLoopAgentAsync } from '@/lib/async-tasks';
 *
 * // Create an agent with async tools built-in
 * const agent = new ToolLoopAgentAsync({
 *   model: anthropic('claude-sonnet-4-5'),
 *   instructions: 'You are a helpful assistant...',
 *   asyncTools: {
 *     get_weather: {
 *       tool: weatherTool,
 *       immediateResponse: ({ city }) => `Fetching weather for ${city}...`,
 *     },
 *   },
 * });
 * ```
 */

// Core functionality
export {
  storeCompletedTask,
  getCompletedTasks,
  markTaskProcessed,
  clearTasks,
  setStorage,
  getStorage,
  type AsyncTask,
  type AsyncTaskStorage,
} from './core';

// Tool wrapper
export { createAsyncTool } from './wrapper';

// Agent adapter
export {
  createAsyncTaskPrepareCall,
  createUserIdContext,
} from './adapter';

// Types
export type {
  AsyncTaskWrapperOptions,
  AsyncTaskAdapterConfig,
} from './types';

// ToolLoopAgentAsync class and related types
export {
  ToolLoopAgentAsync,
  asyncAgentCallOptionsSchema,
  type AsyncToolConfig,
  type AsyncAgentCallOptions,
  type ToolLoopAgentAsyncSettings,
  type InferAsyncAgentUIMessage,
} from './agent';

