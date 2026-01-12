/**
 * ToolLoopAgentAsync
 *
 * A composition-based wrapper around ToolLoopAgent that provides built-in
 * async task support. This class automatically wraps specified tools to
 * execute in the background and injects completed task results into the
 * conversation context.
 */

import {
  ToolLoopAgent,
  type Agent,
  type ToolSet,
  type Output,
  type CoreTool,
  type GenerateTextResult,
  type StreamTextResult,
} from 'ai';
import { z } from 'zod';
import { createAsyncTool } from './wrapper';
import { createAsyncTaskPrepareCall } from './adapter';
import type { AsyncTask } from './types';

/**
 * Configuration for an async tool.
 */
export interface AsyncToolConfig {
  /**
   * The original tool to wrap for async execution.
   */
  tool: CoreTool;
  /**
   * Optional custom message to return immediately when the tool is triggered.
   * Receives the tool parameters as input.
   */
  immediateResponse?: (params: Record<string, unknown>) => string;
}

/**
 * Type-safe global storage for current user ID during agent execution.
 */
declare global {
  // eslint-disable-next-line no-var
  var __currentUserId: string | undefined;
}

/**
 * Base call options schema that includes userId for async task support.
 */
export const asyncAgentCallOptionsSchema = z.object({
  userId: z.string().optional().default('anonymous'),
});

export type AsyncAgentCallOptions = z.infer<typeof asyncAgentCallOptionsSchema>;

/**
 * Settings for ToolLoopAgentAsync.
 * Extends standard ToolLoopAgent settings with async-specific options.
 */
export interface ToolLoopAgentAsyncSettings<
  CALL_OPTIONS extends AsyncAgentCallOptions = AsyncAgentCallOptions,
  TOOLS extends ToolSet = ToolSet,
  ASYNC_TOOLS extends Record<string, AsyncToolConfig> = Record<string, AsyncToolConfig>,
  OUTPUT extends Output = never,
> {
  /**
   * The id of the agent.
   */
  id?: string;

  /**
   * The instructions for the agent.
   */
  instructions?: string;

  /**
   * The language model to use.
   */
  model: Parameters<typeof ToolLoopAgent>[0]['model'];

  /**
   * Regular (synchronous) tools that the agent can use.
   */
  tools?: TOOLS;

  /**
   * Async tools that execute in the background.
   * These tools return immediately and store results for later retrieval.
   */
  asyncTools?: ASYNC_TOOLS;

  /**
   * The schema for call options. Must extend AsyncAgentCallOptions.
   */
  callOptionsSchema?: z.ZodType<CALL_OPTIONS>;

  /**
   * Optional custom function to format task results for injection.
   */
  formatTaskResults?: (tasks: AsyncTask[]) => string;

  /**
   * Optional custom instructions template for task injection.
   * Use {results} as a placeholder for the formatted results.
   */
  instructionsTemplate?: string;

  /**
   * Additional prepareCall hook to run after async task injection.
   * This allows chaining custom prepareCall logic.
   */
  prepareCall?: Parameters<typeof ToolLoopAgent>[0]['prepareCall'];

  /**
   * All other ToolLoopAgent settings.
   */
  maxOutputTokens?: number;
  temperature?: number;
  topP?: number;
  topK?: number;
  presencePenalty?: number;
  frequencyPenalty?: number;
  stopSequences?: string[];
  seed?: number;
  headers?: Record<string, string>;
  stopWhen?: Parameters<typeof ToolLoopAgent>[0]['stopWhen'];
  onStepFinish?: Parameters<typeof ToolLoopAgent>[0]['onStepFinish'];
  onFinish?: Parameters<typeof ToolLoopAgent>[0]['onFinish'];
  experimental_telemetry?: Parameters<typeof ToolLoopAgent>[0]['experimental_telemetry'];
  experimental_context?: unknown;
}

/**
 * ToolLoopAgentAsync - A ToolLoopAgent with built-in async task support.
 *
 * This class wraps ToolLoopAgent using composition and provides:
 * - Automatic async tool wrapping for background execution
 * - Automatic task result injection into conversation context
 * - Full compatibility with the Agent interface
 *
 * @example
 * ```typescript
 * const agent = new ToolLoopAgentAsync({
 *   model: anthropic('claude-sonnet-4-5'),
 *   instructions: 'You are a helpful assistant...',
 *   tools: {
 *     get_weather: weatherTool,  // Regular tool
 *   },
 *   asyncTools: {
 *     get_delayed_weather: {
 *       tool: delayedWeatherTool,
 *       immediateResponse: ({ city }) => `Fetching weather for ${city}...`,
 *     },
 *   },
 * });
 * ```
 */
export class ToolLoopAgentAsync<
  CALL_OPTIONS extends AsyncAgentCallOptions = AsyncAgentCallOptions,
  TOOLS extends ToolSet = ToolSet,
  ASYNC_TOOLS extends Record<string, AsyncToolConfig> = Record<string, AsyncToolConfig>,
  OUTPUT extends Output = never,
> implements Agent<CALL_OPTIONS, TOOLS & { [K in keyof ASYNC_TOOLS]: CoreTool }, OUTPUT>
{
  readonly version = 'agent-v1' as const;

  private readonly innerAgent: ToolLoopAgent<
    CALL_OPTIONS,
    TOOLS & { [K in keyof ASYNC_TOOLS]: CoreTool },
    OUTPUT
  >;

  private readonly settings: ToolLoopAgentAsyncSettings<
    CALL_OPTIONS,
    TOOLS,
    ASYNC_TOOLS,
    OUTPUT
  >;

  constructor(
    settings: ToolLoopAgentAsyncSettings<CALL_OPTIONS, TOOLS, ASYNC_TOOLS, OUTPUT>,
  ) {
    this.settings = settings;

    // Convert async tools to wrapped async tools
    const wrappedAsyncTools: Record<string, CoreTool> = {};
    if (settings.asyncTools) {
      for (const [name, config] of Object.entries(settings.asyncTools)) {
        wrappedAsyncTools[name] = createAsyncTool(config.tool, {
          toolName: name,
          getUserId: () => globalThis.__currentUserId || 'anonymous',
          immediateResponse: config.immediateResponse,
        });
      }
    }

    // Merge regular tools with wrapped async tools
    const allTools = {
      ...settings.tools,
      ...wrappedAsyncTools,
    } as TOOLS & { [K in keyof ASYNC_TOOLS]: CoreTool };

    // Create the async task prepareCall hook
    const asyncPrepareCall = createAsyncTaskPrepareCall({
      getUserId: (options) => {
        const callOptions = options as CALL_OPTIONS | undefined;
        return callOptions?.userId || 'anonymous';
      },
      formatTaskResults: settings.formatTaskResults,
      instructionsTemplate: settings.instructionsTemplate,
    });

    // Create the inner ToolLoopAgent with combined prepareCall
    this.innerAgent = new ToolLoopAgent({
      id: settings.id,
      model: settings.model,
      instructions: settings.instructions,
      tools: allTools,
      callOptionsSchema: settings.callOptionsSchema || asyncAgentCallOptionsSchema,
      maxOutputTokens: settings.maxOutputTokens,
      temperature: settings.temperature,
      topP: settings.topP,
      topK: settings.topK,
      presencePenalty: settings.presencePenalty,
      frequencyPenalty: settings.frequencyPenalty,
      stopSequences: settings.stopSequences,
      seed: settings.seed,
      headers: settings.headers,
      stopWhen: settings.stopWhen,
      onStepFinish: settings.onStepFinish,
      onFinish: settings.onFinish,
      experimental_telemetry: settings.experimental_telemetry,
      experimental_context: settings.experimental_context,

      // Combined prepareCall that handles async tasks and user's custom prepareCall
      prepareCall: async ({ messages, options, ...restSettings }) => {
        const callOptions = options as CALL_OPTIONS | undefined;
        const userId = callOptions?.userId || 'anonymous';

        // Store userId in global storage for async tools to access
        globalThis.__currentUserId = userId;

        // First, apply async task injection
        let modifiedSettings = await asyncPrepareCall({
          messages,
          options,
          ...restSettings,
        });

        // Then, apply user's custom prepareCall if provided
        if (settings.prepareCall) {
          modifiedSettings = await settings.prepareCall({
            messages,
            options,
            ...modifiedSettings,
          } as Parameters<NonNullable<typeof settings.prepareCall>>[0]);
        }

        return modifiedSettings;
      },
    } as Parameters<typeof ToolLoopAgent>[0]);
  }

  /**
   * The id of the agent.
   */
  get id(): string | undefined {
    return this.innerAgent.id;
  }

  /**
   * The tools that the agent can use (both regular and async).
   */
  get tools(): TOOLS & { [K in keyof ASYNC_TOOLS]: CoreTool } {
    return this.innerAgent.tools;
  }

  /**
   * The async tools configuration.
   */
  get asyncTools(): ASYNC_TOOLS | undefined {
    return this.settings.asyncTools;
  }

  /**
   * Generates an output from the agent (non-streaming).
   */
  generate(
    options: Parameters<typeof this.innerAgent.generate>[0],
  ): Promise<GenerateTextResult<TOOLS & { [K in keyof ASYNC_TOOLS]: CoreTool }, OUTPUT>> {
    return this.innerAgent.generate(options);
  }

  /**
   * Streams an output from the agent (streaming).
   */
  stream(
    options: Parameters<typeof this.innerAgent.stream>[0],
  ): Promise<StreamTextResult<TOOLS & { [K in keyof ASYNC_TOOLS]: CoreTool }, OUTPUT>> {
    return this.innerAgent.stream(options);
  }
}

/**
 * Infer the UI message type of a ToolLoopAgentAsync.
 */
export type InferAsyncAgentUIMessage<
  AGENT extends ToolLoopAgentAsync<any, any, any, any>,
> = AGENT extends ToolLoopAgentAsync<infer _CO, infer TOOLS, infer ASYNC_TOOLS, any>
  ? import('ai').UIMessage<unknown, never, import('ai').InferUITools<TOOLS & { [K in keyof ASYNC_TOOLS]: CoreTool }>>
  : never;

