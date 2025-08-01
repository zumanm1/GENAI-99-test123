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

try:
    from openrouter import OpenRouter # Assuming 'openrouter' is the package name
except ImportError:
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

class OpenRouterProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "openai/gpt-4", **kwargs):
        if OpenRouter is None:
            raise ImportError("OpenRouter library is not installed. Please install it with 'pip install openrouter-py'.")
        self.client = OpenRouter(api_key=api_key)
        self.model = model
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
