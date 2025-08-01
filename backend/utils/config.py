import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Configuration class to hold all application settings
    """
    
    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/network_automation")
    
    # Security settings
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # API settings
    API_V1_STR = "/api/v1"
    PROJECT_NAME = "Network Automation Application"
    PROJECT_VERSION = "1.0.0"
    
    # LLM settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    
    # Network settings
    DEFAULT_SSH_PORT = int(os.getenv("DEFAULT_SSH_PORT", "22"))
    DEFAULT_TELNET_PORT = int(os.getenv("DEFAULT_TELNET_PORT", "23"))
    CONNECTION_TIMEOUT = int(os.getenv("CONNECTION_TIMEOUT", "30"))
    
    # AI settings
    DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gpt-3.5-turbo")
    DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "2000"))
    
    # Chat settings
    MAX_CHAT_HISTORY = int(os.getenv("MAX_CHAT_HISTORY", "50"))
    CHAT_CONTEXT_WINDOW = int(os.getenv("CHAT_CONTEXT_WINDOW", "10"))
    
    # Device settings
    DEFAULT_POLLING_INTERVAL = int(os.getenv("DEFAULT_POLLING_INTERVAL", "300"))  # 5 minutes
    MAX_CONCURRENT_CONNECTIONS = int(os.getenv("MAX_CONCURRENT_CONNECTIONS", "10"))
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Testing settings
    TESTING = os.getenv("TESTING", "False").lower() == "true"
    
    @classmethod
    def get_llm_config(cls, provider=None):
        """
        Get LLM configuration for a specific provider or default
        """
        if provider is None:
            provider = cls.DEFAULT_LLM_PROVIDER
            
        configs = {
            "openai": {
                "api_key": cls.OPENAI_API_KEY,
                "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
                "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
            },
            "groq": {
                "api_key": cls.GROQ_API_KEY,
                "model": os.getenv("GROQ_MODEL", "llama3-70b-8192"),
                "temperature": float(os.getenv("GROQ_TEMPERATURE", "0.7")),
                "max_tokens": int(os.getenv("GROQ_MAX_TOKENS", "2000"))
            },
            "openrouter": {
                "api_key": cls.OPENROUTER_API_KEY,
                "model": os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo"),
                "temperature": float(os.getenv("OPENROUTER_TEMPERATURE", "0.7")),
                "max_tokens": int(os.getenv("OPENROUTER_MAX_TOKENS", "2000"))
            }
        }
        
        return configs.get(provider, configs[cls.DEFAULT_LLM_PROVIDER])

# Create a global config instance
config = Config()