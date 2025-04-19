# LLM Integration

The Vortex framework provides robust integration with various Large Language Models (LLMs) through a flexible and extensible architecture. This allows the framework to leverage the capabilities of different models while providing a consistent interface for the rest of the system.

## Supported Models

Vortex can connect to any LLM supported by LiteLLM. However, it requires a powerful model to work effectively. Based on evaluations and community feedback, the following models have been verified to work well with Vortex:

- **anthropic/claude-3-7-sonnet-20250219** (recommended)
- **gemini/gemini-2.5-pro**
- **deepseek/deepseek-chat**
- **openai/o3-mini**
- **all-hands/openhands-lm-32b-v0.1**

## LLM Configuration

The LLM integration can be configured through several mechanisms:

### Basic Configuration

- **LLM Provider**: The provider of the LLM (e.g., OpenAI, Anthropic, Google).
- **LLM Model**: The specific model to use (e.g., gpt-4, claude-3).
- **API Key**: The API key for accessing the LLM provider's services.
- **Base URL**: The base URL for the LLM provider's API (useful for custom deployments).

### Advanced Configuration

Additional settings can be configured through environment variables:

- **LLM_API_VERSION**: The API version to use.
- **LLM_EMBEDDING_MODEL**: The model to use for embeddings.
- **LLM_EMBEDDING_DEPLOYMENT_NAME**: The deployment name for the embedding model.
- **LLM_DROP_PARAMS**: Parameters to drop from the LLM request.
- **LLM_DISABLE_VISION**: Whether to disable vision capabilities.
- **LLM_CACHING_PROMPT**: Whether to cache prompts to avoid redundant API calls.

### API Retries and Rate Limits

LLM providers typically have rate limits, and Vortex includes automatic retry mechanisms:

- **LLM_NUM_RETRIES**: Number of retries (default: 4).
- **LLM_RETRY_MIN_WAIT**: Minimum wait time between retries (default: 5 seconds).
- **LLM_RETRY_MAX_WAIT**: Maximum wait time between retries (default: 30 seconds).
- **LLM_RETRY_MULTIPLIER**: Multiplier for exponential backoff (default: 2).

## LLM Class Implementation

The `LLM` class is the core component for interacting with language models:

1. **Model Management**: Handles different model types and their specific requirements.
2. **Function Calling**: Supports function calling for models that have this capability.
3. **Retry Mechanism**: Implements retry logic for handling API errors.
4. **Vision Support**: Provides vision capabilities for compatible models.

```python
# Key aspects of the LLM class
class LLM:
    def __init__(self, model_name, api_key, ...):
        # Initialize the LLM with the specified model and credentials
        
    async def generate(self, prompt, functions=None, ...):
        # Generate a response from the LLM
        
    async def generate_with_functions(self, prompt, functions, ...):
        # Generate a response with function calling
        
    def _handle_retry(self, exception):
        # Handle retries for API errors
```

## Function Calling

Vortex supports function calling for models that have this capability:

1. **Function Definition**: Define functions that the LLM can call.
2. **Function Execution**: Execute functions called by the LLM.
3. **Result Processing**: Process the results of function calls.

```python
# Example of function calling
functions = [
    {
        "name": "get_weather",
        "description": "Get the current weather in a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                }
            },
            "required": ["location"]
        }
    }
]

response = await llm.generate_with_functions(prompt, functions)
```

## Provider-Specific Guides

Vortex includes guides for using specific LLM providers:

1. **Azure**: Configuration for Azure OpenAI services.
2. **Google**: Configuration for Google's AI models.
3. **Groq**: Configuration for Groq's high-performance inference API.
4. **Local LLMs**: Configuration for running local models with SGLang or vLLM.
5. **LiteLLM Proxy**: Configuration for using LiteLLM's proxy service.
6. **OpenAI**: Configuration for OpenAI's models.
7. **OpenRouter**: Configuration for accessing various models through OpenRouter.

## Integration with Other Components

The LLM integration connects with other Vortex components:

1. **Agent**: Provides the core reasoning capabilities for the agent.
2. **Memory**: Enhances prompts with relevant context from memory.
3. **Reinforcement Learning**: Generates actions for reinforcement learning.

## Best Practices

When using the LLM integration, follow these best practices:

1. **Model Selection**: Choose a model that balances performance and cost for your use case.
2. **Rate Limit Management**: Configure retry settings based on your provider's rate limits.
3. **Error Handling**: Implement robust error handling for API failures.
4. **Cost Monitoring**: Set spending limits and monitor usage to control costs.
5. **Prompt Optimization**: Optimize prompts to get the best performance from the model.
6. **Function Design**: Design functions that are clear and specific for effective function calling.

## Customization

The LLM integration can be customized in several ways:

1. **Custom Models**: Add support for new models as they become available.
2. **Custom Providers**: Integrate with new LLM providers.
3. **Custom Retry Logic**: Implement specialized retry logic for specific use cases.
4. **Extended Function Calling**: Enhance function calling with additional capabilities.