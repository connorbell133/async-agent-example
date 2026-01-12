'use client';

import { useChat } from '@ai-sdk/react';
import { DefaultChatTransport } from 'ai';
import { AsyncTaskAgentMessage } from '@/agent/async-task-agent';
import ChatInput from '@/components/chat-input';
import { useState, useEffect } from 'react';

export default function Home() {
  const [userId, setUserId] = useState('anonymous');

  // Initialize userId on client side only
  useEffect(() => {
    const stored = localStorage.getItem('async-chat-user-id');
    if (stored) {
      setUserId(stored);
    } else {
      const newId = crypto.randomUUID();
      localStorage.setItem('async-chat-user-id', newId);
      setUserId(newId);
    }
  }, []);

  const { error, status, sendMessage, messages, regenerate, stop } = useChat<
    AsyncTaskAgentMessage
  >({
    transport: new DefaultChatTransport({
      api: '/api/chat',
      body: {
        userId,
      },
    }),
  });

  return (
    <div className="flex flex-col py-24 mx-auto w-full max-w-2xl stretch">
      <div className="mb-4 p-4 bg-blue-50 rounded-lg">
        <h1 className="text-2xl font-bold mb-2">Async Task Chat</h1>
        <p className="text-sm text-gray-600">
          This chat demonstrates async task execution. Try asking for weather in a city
          (e.g., "Get me the weather for London") - it will queue the task and you can
          continue chatting. The result will be mentioned naturally when it's ready!
        </p>
        <p className="text-xs text-gray-500 mt-2">User ID: {userId}</p>
      </div>

      <div className="space-y-4 mb-8">
        {messages.map(m => (
          <div
            key={m.id}
            className={`p-4 rounded-lg ${m.role === 'user'
              ? 'bg-blue-100 ml-auto max-w-[80%]'
              : 'bg-gray-100 mr-auto max-w-[80%]'
              }`}
          >
            <div className="font-semibold mb-1">
              {m.role === 'user' ? 'You' : 'Assistant'}
            </div>
            <div className="whitespace-pre-wrap">
              {m.parts.map((part, idx) => {
                if (part.type === 'text') {
                  return <div key={idx}>{part.text}</div>;
                }
                if (part.type === 'tool-call' && 'toolName' in part) {
                  return (
                    <div key={idx} className="mt-2 p-2 bg-yellow-100 rounded text-sm">
                      🔧 Calling tool: {String(part.toolName)}
                    </div>
                  );
                }
                if (part.type === 'tool-result' && 'output' in part) {
                  return (
                    <div key={idx} className="mt-2 p-2 bg-green-100 rounded text-sm">
                      ✅ Tool result: {String(part.output)}
                    </div>
                  );
                }
                return null;
              })}
            </div>
          </div>
        ))}
      </div>

      {(status === 'submitted' || status === 'streaming') && (
        <div className="mt-4 text-gray-500 mb-4">
          {status === 'submitted' && <div>Loading...</div>}
          {status === 'streaming' && <div>Streaming response...</div>}
          <button
            type="button"
            className="px-4 py-2 mt-4 text-blue-500 rounded-md border border-blue-500 hover:bg-blue-50"
            onClick={stop}
          >
            Stop
          </button>
        </div>
      )}

      {error && (
        <div className="mt-4 p-4 bg-red-50 rounded-lg">
          <div className="text-red-500 font-semibold">An error occurred</div>
          <div className="text-red-600 text-sm mt-2">{error.message}</div>
          <button
            type="button"
            className="px-4 py-2 mt-4 text-blue-500 rounded-md border border-blue-500 hover:bg-blue-50"
            onClick={() => regenerate()}
          >
            Retry
          </button>
        </div>
      )}

      <ChatInput status={status} onSubmit={text => sendMessage({ text })} />
    </div>
  );
}
