"""
Asynchronous Gemini Chatbot - Main Application Module

This module initializes the FastAPI application, sets up middleware,
includes routers, and manages application lifecycle events.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import chat
from app.services import task_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Task monitoring global flag
TASK_MONITOR_RUNNING = False


# Lifespan context manager (FastAPI recommended approach for startup/shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.

    This manages the startup and shutdown events for the application.
    """
    # Startup: Start the task monitoring background task
    logger.info("Starting up the application")
    task_monitor = asyncio.create_task(monitor_tasks())

    yield  # Application runs here

    # Shutdown: Clean up resources
    logger.info("Shutting down the application")
    task_monitor.cancel()
    try:
        await task_monitor
    except asyncio.CancelledError:
        logger.info("Task monitor cancelled")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix=settings.API_V1_STR)


async def monitor_tasks():
    """
    Periodically check for completed tasks.

    This function runs in the background and monitors the task queue
    for completed tasks. It logs information about the tasks and ensures
    the task worker is running.
    """
    global TASK_MONITOR_RUNNING

    logger.info("Task monitor started")
    TASK_MONITOR_RUNNING = True

    try:
        while True:
            # Get task statistics
            total_tasks = len(task_manager.tasks)
            active_tasks = sum(
                1
                for task in task_manager.tasks.values()
                if task.status == task_manager.TaskStatus.RUNNING
            )
            completed_tasks = sum(
                1
                for task in task_manager.tasks.values()
                if task.status == task_manager.TaskStatus.COMPLETED
            )

            # Log statistics periodically
            logger.info(
                "Task monitor: %d total, %d active, %d completed",
                total_tasks,
                active_tasks,
                completed_tasks,
            )

            # Ensure worker is running
            task_manager.ensure_worker_running()

            # Sleep before next check
            await asyncio.sleep(settings.TASK_CHECK_INTERVAL)

    except asyncio.CancelledError:
        logger.info("Task monitor cancelled")
    except Exception as e:
        logger.error("Error in task monitor: %s", str(e))
    finally:
        TASK_MONITOR_RUNNING = False


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "task_worker_running": task_manager.IS_WORKER_RUNNING,
        "task_monitor_running": TASK_MONITOR_RUNNING,
        "active_tasks": sum(
            1
            for task in task_manager.tasks.values()
            if task.status == task_manager.TaskStatus.RUNNING
        ),
        "queued_tasks": len(task_manager.task_queue),
    }
