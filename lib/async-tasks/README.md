# Async Task System for AI SDK

A containerized, standalone system for handling asynchronous tool execution with AI SDK agents. This module provides a clean abstraction for executing long-running tools in the background while allowing the agent to continue processing other requests.

## Features

- **ToolLoopAgentAsync**: Drop-in replacement for ToolLoopAgent with built-in async support
- **Standalone & Reusable**: Works independently of any specific agent implementation
- **Type-Safe**: Full TypeScript support with proper types
- **Extensible**: Pluggable storage backends (in-memory, database, etc.)
- **Easy Integration**: Simple API for wrapping tools and integrating with agents
- **User-Scoped**: Tasks are scoped per user, allowing multi-user support

## Quick Start: ToolLoopAgentAsync

The easiest way to use async tasks is with `ToolLoopAgentAsync`:

```typescript
import { ToolLoopAgentAsync } from '@/lib/async-tasks';
import { anthropic } from '@ai-sdk/anthropic';
import { delayedWeatherTool } from './tools';

const agent = new ToolLoopAgentAsync({
  model: anthropic('claude-sonnet-4-5'),
  instructions: 'You are a helpful assistant...',
  
  // Regular tools (optional)
  tools: {
    quick_tool: myQuickTool,
  },
  
  // Async tools - execute in background and return immediately
  asyncTools: {
    get_weather: {
      tool: delayedWeatherTool,
      immediateResponse: ({ city }) => 
        `Fetching weather for ${city}. This may take a moment...`,
    },
  },
});

// Use with createAgentUIStreamResponse just like ToolLoopAgent
return createAgentUIStreamResponse({
  agent,
  uiMessages,
  options: { userId: 'user-123' },
});
```

## Core Concepts

1. **Async Tools**: Tools that execute in the background and return immediately
2. **Task Storage**: Completed task results are stored and retrieved later
3. **Task Injection**: Completed tasks are automatically injected into the conversation context

## API Reference

### ToolLoopAgentAsync

A composition-based wrapper around `ToolLoopAgent` with built-in async task support.

```typescript
new ToolLoopAgentAsync({
  // Required
  model: LanguageModel,
  
  // Optional
  instructions?: string,
  tools?: ToolSet,                    // Regular synchronous tools
  asyncTools?: {                       // Async tools
    [name: string]: {
      tool: CoreTool,
      immediateResponse?: (params) => string,
    },
  },
  callOptionsSchema?: z.ZodType,      // Must extend AsyncAgentCallOptions
  formatTaskResults?: (tasks) => string,
  instructionsTemplate?: string,       // Use {results} placeholder
  prepareCall?: Function,              // Chain additional prepareCall logic
  
  // All standard ToolLoopAgent settings...
});
```

**Methods:**
- `generate(options)`: Non-streaming generation
- `stream(options)`: Streaming generation

**Properties:**
- `id`: Agent ID
- `tools`: All tools (regular + async)
- `asyncTools`: Async tools configuration

### Low-Level API

For more control, use the individual utilities:

#### `createAsyncTool(originalTool, options)`

Wraps an existing tool to execute asynchronously in the background.

```typescript
import { createAsyncTool } from '@/lib/async-tasks';

const asyncTool = createAsyncTool(myLongRunningTool, {
  toolName: 'my_tool',
  getUserId: () => globalThis.__currentUserId || 'anonymous',
  immediateResponse: (params) => 'Processing your request...',
});
```

#### `createAsyncTaskPrepareCall(config)`

Creates a `prepareCall` function that injects completed tasks into the conversation.

```typescript
import { createAsyncTaskPrepareCall } from '@/lib/async-tasks';

const prepareCall = createAsyncTaskPrepareCall({
  getUserId: (options) => options?.userId || 'anonymous',
  formatTaskResults: (tasks) => tasks.map(t => t.result).join('\n'),
  instructionsTemplate: 'Results:\n{results}',
});
```

#### Task Storage Functions

```typescript
import { 
  storeCompletedTask,
  getCompletedTasks,
  markTaskProcessed,
  clearTasks,
  setStorage,
  getStorage,
} from '@/lib/async-tasks';

// Manually store a task result
const taskId = storeCompletedTask(userId, toolName, params, result);

// Get unprocessed tasks for a user
const tasks = getCompletedTasks(userId);

// Mark task as processed
markTaskProcessed(taskId);

// Clear tasks
clearTasks(userId);  // For a specific user
clearTasks();        // All tasks
```

## Custom Storage Backend

```typescript
import { setStorage, type AsyncTaskStorage } from '@/lib/async-tasks';

class DatabaseStorage implements AsyncTaskStorage {
  store(task) {
    const taskId = db.tasks.insert(task);
    return taskId;
  }

  getUnprocessed(userId) {
    return db.tasks.find({ userId, processed: false });
  }

  markProcessed(taskId) {
    db.tasks.update({ taskId }, { processed: true });
  }

  clear(userId?) {
    db.tasks.delete(userId ? { userId } : {});
  }
}

setStorage(new DatabaseStorage());
```

## Architecture

```
lib/async-tasks/
├── types.ts       # Type definitions and interfaces
├── core.ts        # Core storage and task management
├── wrapper.ts     # Tool wrapper for async execution
├── adapter.ts     # Agent integration adapter
├── agent.ts       # ToolLoopAgentAsync class
└── index.ts       # Public API exports
```

## TypeScript Types

```typescript
// Infer UI message type from agent
type MyAgentMessage = InferAsyncAgentUIMessage<typeof myAgent>;

// Or use standard InferAgentUIMessage
type MyAgentMessage = InferAgentUIMessage<typeof myAgent>;

// Call options (extends AsyncAgentCallOptions)
interface MyCallOptions extends AsyncAgentCallOptions {
  customOption?: string;
}
```

## Examples

See `agent/async-task-agent.ts` for a complete working example using `ToolLoopAgentAsync`.
