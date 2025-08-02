from abc import ABC, abstractmethod

# Placeholder imports - we will manage dependencies later
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from groq import Groq
except ImportError:
    Groq = None

# We'll use requests directly to call the OpenRouter API
try:
    import requests
    OpenRouter = object  # Use a placeholder to indicate the dependency is available
except ImportError:
    requests = None
    OpenRouter = None

class LLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate a text response from a prompt."""
        pass

    def generate_config(self, requirements: str, device_type: str) -> str:
        """Generate a network configuration."""
        prompt = f"Generate a Cisco {device_type} configuration for the following requirements: {requirements}"
        return self.generate_text(prompt)

    def validate_config(self, config: str, requirements: str) -> dict:
        """Validate a network configuration."""
        prompt = f"Validate the following configuration against these requirements. Requirements: {requirements}\n\nConfiguration:\n{config}"
        # This would likely return a structured JSON in a real scenario
        return {"validation_report": self.generate_text(prompt)}

    def troubleshoot_issue(self, issue_description: str, device_info: dict) -> str:
        """Provide troubleshooting steps for a network issue."""
        prompt = f"Troubleshoot the following network issue. Issue: {issue_description}\n\nDevice Info: {device_info}"
        return self.generate_text(prompt)

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4", **kwargs):
        if OpenAI is None:
            raise ImportError("OpenAI library is not installed. Please install it with 'pip install openai'.")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        # Store common LLM parameters, filtering out None values
        self.default_params = {
            key: kwargs.get(key) for key in ["temperature", "max_tokens"] if kwargs.get(key) is not None
        }

    def generate_text(self, prompt: str, **kwargs) -> str:
        request_params = self.default_params.copy()
        request_params.update(kwargs)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **request_params
        )
        return response.choices[0].message.content

class GroqProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "llama3-70b-8192", **kwargs):
        if Groq is None:
            raise ImportError("Groq library is not installed. Please install it with 'pip install groq'.")
        self.client = Groq(api_key=api_key)
        self.model = model
        # Filter kwargs to only include parameters that the Groq client accepts
        valid_params = ["temperature", "max_tokens"]
        self.default_params = {
            key: kwargs.get(key) for key in valid_params if kwargs.get(key) is not None
        }

    def generate_text(self, prompt: str, **kwargs) -> str:
        request_params = self.default_params.copy()
        request_params.update(kwargs)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **request_params
        )
        return response.choices[0].message.content

class OpenRouterProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "openai/gpt-4", **kwargs):
        if requests is None:
            raise ImportError("requests library is not installed. Please install it with 'pip install requests'.")
        if OpenRouter is None:
            raise ImportError("OpenRouter library is not installed. Please install it with 'pip install openrouter'.")
        # Use a simple object to hold model information
        self.client = type('obj', (object,), {'model': model})
        self.api_key = api_key
        self.default_params = {
            key: kwargs.get(key) for key in ["temperature", "max_tokens"] if kwargs.get(key) is not None
        }

    def generate_text(self, prompt: str, **kwargs) -> str:
        request_params = self.default_params.copy()
        request_params.update(kwargs)
        
        # Set the API key in headers for each request
        import requests
        api = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare messages in the required format
        messages = [{"role": "user", "content": prompt}]
        
        # Prepare the data payload
        data = {
            "model": self.client.model,
            "messages": messages,
            **request_params
        }
        
        # Make the request
        response = requests.post(api, json=data, headers=headers)
        response.raise_for_status()
        
        # Extract and return the generated text
        return response.json()["choices"][0]["message"]["content"]

class LLMFactory:
    @staticmethod
    def create_llm(provider: str, **kwargs) -> LLMProvider:
        # Filter out None values from kwargs to avoid passing them to the constructor
        filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        if provider == "openai":
            return OpenAIProvider(**filtered_kwargs)
        elif provider == "groq":
            return GroqProvider(**filtered_kwargs)
        elif provider == "openrouter":
            return OpenRouterProvider(**filtered_kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
