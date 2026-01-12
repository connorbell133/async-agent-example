/**
 * Core types for the async task system.
 */

/**
 * Represents an async task that has been completed and stored.
 */
export interface AsyncTask {
  taskId: string;
  userId: string;
  toolName: string;
  parameters: Record<string, unknown>;
  result: string;
  processed: boolean;
  createdAt: number;
  completedAt: number;
}

/**
 * Options for creating an async task wrapper.
 */
export interface AsyncTaskWrapperOptions {
  /**
   * The name of the tool (used for identification).
   */
  toolName: string;
  /**
   * A function to get the current user ID during tool execution.
   */
  getUserId: () => string;
  /**
   * Optional message to return immediately when the async task is triggered.
   * If not provided, a default message will be used.
   */
  immediateResponse?: (params: Record<string, unknown>) => string;
}

/**
 * Configuration for the async task adapter.
 */
export interface AsyncTaskAdapterConfig {
  /**
   * Function to get the user ID from agent call options.
   */
  getUserId: (options: unknown) => string;
  /**
   * Optional function to format task results for injection into the conversation.
   * If not provided, a default formatter will be used.
   */
  formatTaskResults?: (tasks: AsyncTask[]) => string;
  /**
   * Optional instructions template for injecting task results.
   * Use {results} as a placeholder for the formatted results.
   */
  instructionsTemplate?: string;
}

/**
 * Storage interface for async tasks.
 * Allows for different storage backends (in-memory, database, etc.).
 */
export interface AsyncTaskStorage {
  store(task: Omit<AsyncTask, 'taskId' | 'createdAt' | 'completedAt'>): string;
  getUnprocessed(userId: string): AsyncTask[];
  markProcessed(taskId: string): void;
  clear(userId?: string): void;
}

