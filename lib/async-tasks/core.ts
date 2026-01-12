/**
 * Core async task management system.
 * Provides storage and retrieval of async task results.
 */

import type { AsyncTask, AsyncTaskStorage } from './types';

/**
 * In-memory storage implementation for async tasks.
 * In production, this could be replaced with a database-backed implementation.
 */
class InMemoryAsyncTaskStorage implements AsyncTaskStorage {
  private tasks = new Map<string, AsyncTask>();

  store(task: Omit<AsyncTask, 'taskId' | 'createdAt' | 'completedAt'>): string {
    const taskId = crypto.randomUUID();
    const fullTask: AsyncTask = {
      ...task,
      taskId,
      processed: false,
      createdAt: Date.now(),
      completedAt: Date.now(),
    };
    this.tasks.set(taskId, fullTask);
    return taskId;
  }

  getUnprocessed(userId: string): AsyncTask[] {
    return Array.from(this.tasks.values()).filter(
      task => task.userId === userId && !task.processed,
    );
  }

  markProcessed(taskId: string): void {
    const task = this.tasks.get(taskId);
    if (task) {
      task.processed = true;
    }
  }

  clear(userId?: string): void {
    if (userId) {
      // Clear only tasks for a specific user
      for (const [taskId, task] of this.tasks.entries()) {
        if (task.userId === userId) {
          this.tasks.delete(taskId);
        }
      }
    } else {
      // Clear all tasks
      this.tasks.clear();
    }
  }
}

/**
 * Default in-memory storage instance.
 * Can be replaced with a custom storage implementation.
 */
let defaultStorage: AsyncTaskStorage = new InMemoryAsyncTaskStorage();

/**
 * Set a custom storage implementation.
 */
export function setStorage(storage: AsyncTaskStorage): void {
  defaultStorage = storage;
}

/**
 * Get the current storage implementation.
 */
export function getStorage(): AsyncTaskStorage {
  return defaultStorage;
}

/**
 * Store a completed async task result.
 */
export function storeCompletedTask(
  userId: string,
  toolName: string,
  parameters: Record<string, unknown>,
  result: string,
): string {
  return defaultStorage.store({
    userId,
    toolName,
    parameters,
    result,
  });
}

/**
 * Get all unprocessed completed tasks for a user.
 */
export function getCompletedTasks(userId: string): AsyncTask[] {
  return defaultStorage.getUnprocessed(userId);
}

/**
 * Mark a task as processed.
 */
export function markTaskProcessed(taskId: string): void {
  defaultStorage.markProcessed(taskId);
}

/**
 * Clear tasks (optionally for a specific user).
 */
export function clearTasks(userId?: string): void {
  defaultStorage.clear(userId);
}

// Re-export types
export type { AsyncTask, AsyncTaskStorage };

