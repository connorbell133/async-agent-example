/**
 * Async Task Manager
 *
 * @deprecated This module is deprecated. Please use the new containerized async task system:
 * @see {@link @/lib/async-tasks} for the new implementation.
 *
 * This file is kept for backward compatibility but will be removed in a future version.
 * Migrate to: import { ... } from '@/lib/async-tasks'
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

// In-memory storage for completed tasks
const completedTasks = new Map<string, AsyncTask>();

/**
 * Store a completed task result.
 */
export function storeCompletedTask(
  userId: string,
  toolName: string,
  parameters: Record<string, unknown>,
  result: string,
): string {
  const taskId = crypto.randomUUID();
  const task: AsyncTask = {
    taskId,
    userId,
    toolName,
    parameters,
    result,
    processed: false,
    createdAt: Date.now(),
    completedAt: Date.now(),
  };

  completedTasks.set(taskId, task);
  return taskId;
}

/**
 * Get all completed tasks for a user that haven't been processed.
 */
export function getCompletedTasks(userId: string): AsyncTask[] {
  return Array.from(completedTasks.values()).filter(
    task => task.userId === userId && !task.processed,
  );
}

/**
 * Mark a task as processed.
 */
export function markTaskProcessed(taskId: string): void {
  const task = completedTasks.get(taskId);
  if (task) {
    task.processed = true;
  }
}

