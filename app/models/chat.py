"""
Chat Models Module

This module defines the data models used for chat interactions, tool definitions,
and asynchronous task tracking.
"""

import time
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class Role(str, Enum):
    """Chat message roles."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ChatMessage(BaseModel):
    """Chat message model."""

    role: Role
    content: str


class ChatHistory(BaseModel):
    """Chat history model."""

    messages: List[ChatMessage] = []


class ChatRequest(BaseModel):
    """Chat request model."""

    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message: str


class ChatResponse(BaseModel):
    """Chat response model."""

    response: str


class ToolParameter(BaseModel):
    """Tool parameter model."""

    name: str
    description: Optional[str] = None
    type: str = "string"
    required: bool = False


class ToolDefinition(BaseModel):
    """Tool definition model."""

    name: str
    description: str
    parameters: List[ToolParameter] = []


class ToolCall(BaseModel):
    """Tool call model."""

    name: str
    parameters: Dict[str, Any]


class TaskStatus(str, Enum):
    """Task status."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


def get_current_time() -> float:
    """Get the current time as a float."""
    return time.time()


class AsyncTask(BaseModel):
    """Asynchronous task model."""

    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    tool_call: ToolCall
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    processed: bool = False
    created_at: float = Field(default_factory=get_current_time)
    completed_at: Optional[float] = None
