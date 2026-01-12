import { tool } from 'ai';
import { z } from 'zod';

const weatherConditions: Record<
  string,
  { temp: string; condition: string; humidity: string }
> = {
  London: { temp: '15°C', condition: 'partly cloudy', humidity: '72%' },
  'New York': { temp: '22°C', condition: 'sunny', humidity: '60%' },
  Tokyo: { temp: '19°C', condition: 'rainy', humidity: '85%' },
  Sydney: { temp: '27°C', condition: 'clear', humidity: '55%' },
  Paris: { temp: '14°C', condition: 'overcast', humidity: '70%' },
};

/**
 * Delayed weather tool that simulates a long-running operation (15 seconds).
 * This tool is designed to be executed asynchronously in the background.
 */
export const delayedWeatherTool = tool({
  description:
    'Get the weather forecast for a city. This is a long-running operation that may take 15 seconds.',
  inputSchema: z.object({
    city: z.string().describe('The name of the city to get weather for'),
  }),
  async execute({ city }) {
    // Simulate a long-running API call (15 seconds)
    await new Promise(resolve => setTimeout(resolve, 15000));

    // Get weather for the specific city or use a default response
    const cityWeather = weatherConditions[city] || {
      temp: '18°C',
      condition: 'partly cloudy',
      humidity: '65%',
    };

    return `The weather in ${city} is currently ${cityWeather.temp} and ${cityWeather.condition} with ${cityWeather.humidity} humidity.`;
  },
});

