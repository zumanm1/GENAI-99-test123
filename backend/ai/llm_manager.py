from .llm_providers import LLMProvider, LLMFactory

class LLMSettings:
    """Data class for holding LLM provider settings."""
    def __init__(self, provider: str, api_key: str, model: str, 
                 temperature: float = 0.7, max_tokens: int = 2000):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def to_dict(self):
        """Convert settings to a dictionary for provider instantiation."""
        return {
            "api_key": self.api_key,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

class LLMManager:
    """Manages the lifecycle and switching of LLM providers."""
    def __init__(self):
        self._providers = {}
        self._current_provider = None

    def add_provider(self, name: str, settings: LLMSettings):
        """Adds and instantiates a new provider based on settings."""
        if name not in self._providers:
            provider_instance = LLMFactory.create_llm(provider=settings.provider, **settings.to_dict())
            self._providers[name] = provider_instance
            if self._current_provider is None:
                self.switch_provider(name)

    def switch_provider(self, name: str):
        """Switches the currently active provider."""
        if name in self._providers:
            self._current_provider = self._providers[name]
        else:
            raise ValueError(f"Provider '{name}' not found. Please add it first.")

    @property
    def current_provider(self) -> LLMProvider:
        """Returns the currently active LLM provider."""
        if self._current_provider is None:
            raise ValueError("No active LLM provider. Please add and switch to a provider.")
        return self._current_provider

# Global instance to be used across the application
llm_manager = LLMManager()
