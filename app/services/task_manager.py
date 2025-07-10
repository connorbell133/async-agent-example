"""
Task Manager Module

This module provides functionality for managing asynchronous tasks,
including queuing, execution, and monitoring.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Callable
from uuid import uuid4
from collections import deque

from app.models.chat import AsyncTask, TaskStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for tasks
# Structure: {task_id: AsyncTask}
tasks: Dict[str, AsyncTask] = {}

# Task queue using deque for simplicity
task_queue = deque()

# Flag to check if worker is running
IS_WORKER_RUNNING = False


async def queue_task(task: AsyncTask) -> str:
    """
    Queue a task for execution.

    Args:
        task: The task to queue

    Returns:
        The task ID
    """
    # Ensure task has a task_id
    if not task.task_id:
        task.task_id = str(uuid4())

    # Store the task
    tasks[task.task_id] = task

    # Add to queue
    task_queue.append(task.task_id)

    logger.info("Queued task: %s", task.task_id)

    # Ensure worker is running
    ensure_worker_running()

    return task.task_id


def get_task(task_id: str) -> Optional[AsyncTask]:
    """
    Get a task by ID.

    Args:
        task_id: The task ID

    Returns:
        The task or None if not found
    """
    return tasks.get(task_id)


def get_tasks_by_user(user_id: str) -> List[AsyncTask]:
    """
    Get all tasks for a user.

    Args:
        user_id: The user ID

    Returns:
        A list of tasks for the user
    """
    return [task for task in tasks.values() if task.user_id == user_id]


def get_completed_tasks(user_id: str) -> List[AsyncTask]:
    """
    Get all completed tasks for a user that haven't been processed.

    Args:
        user_id: The user ID

    Returns:
        A list of completed tasks for the user
    """
    return [
        task
        for task in tasks.values()
        if task.user_id == user_id
        and task.status == TaskStatus.COMPLETED
        and not task.processed
    ]


def ensure_worker_running():
    """Ensure the worker task is running."""
    global IS_WORKER_RUNNING

    if not IS_WORKER_RUNNING:
        # Start the worker
        asyncio.create_task(worker())
        IS_WORKER_RUNNING = True
        logger.info("Started task worker")


async def worker():
    """Worker to process tasks from the queue."""
    global IS_WORKER_RUNNING

    logger.info("Task worker started")

    try:
        IS_WORKER_RUNNING = True

        while True:
            if not task_queue:
                # No tasks, sleep for a bit
                await asyncio.sleep(1)
                continue

            # Get the next task
            task_id = task_queue.popleft()
            task = tasks.get(task_id)

            if not task:
                logger.warning("Task %s not found", task_id)
                continue

            # Process the task
            try:
                await process_task(task)
            except Exception as ex:
                logger.error("Error processing task %s: %s", task_id, str(ex))

                # Update task status
                task.status = TaskStatus.FAILED
                task.error = str(ex)
                task.completed_at = time.time()

    except asyncio.CancelledError:
        logger.info("Task worker cancelled")
    except Exception as ex:
        logger.error("Error in task worker: %s", str(ex))
    finally:
        IS_WORKER_RUNNING = False


async def process_task(task: AsyncTask):
    """
    Process a task.

    Args:
        task: The task to process
    """
    logger.info("Processing task: %s", task.task_id)

    # Update task status
    task.status = TaskStatus.RUNNING

    # Get the tool function based on the tool name
    tool_function = get_tool_function(task.tool_call.name)

    if not tool_function:
        task.status = TaskStatus.FAILED
        task.error = f"Unknown tool: {task.tool_call.name}"
        task.completed_at = time.time()
        return

    try:
        # Execute the tool function
        result = await tool_function(**task.tool_call.parameters)

        # Update task with result
        task.result = result
        task.status = TaskStatus.COMPLETED
        task.completed_at = time.time()

        logger.info("Task completed: %s", task.task_id)

    except Exception as ex:
        # Update task with error
        task.status = TaskStatus.FAILED
        task.error = str(ex)
        task.completed_at = time.time()

        logger.error("Error executing task %s: %s", task.task_id, str(ex))


def get_tool_function(tool_name: str) -> Optional[Callable]:
    """
    Get the tool function by name.

    Args:
        tool_name: The name of the tool

    Returns:
        The tool function or None if not found
    """
    # Import here to avoid circular imports
    from app.tools.weather import get_delayed_weather

    tool_functions = {
        "get_delayed_weather": get_delayed_weather,
    }

    return tool_functions.get(tool_name)
