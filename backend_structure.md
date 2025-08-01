# Backend Folder Structure

## Overview
Each page/route in the application will have its own dedicated backend folder to ensure modularity and separation of concerns. This structure will make the application easier to maintain and scale.

## Folder Structure

```
backend/
├── api/
│   ├── __init__.py
│   ├── main.py              # API gateway and routing
│   └── middleware/          # Authentication, logging, etc.
│
├── dashboard/
│   ├── __init__.py
│   ├── routes.py            # Dashboard-specific routes
│   ├── service.py           # Business logic for dashboard
│   └── schemas.py           # Data schemas for dashboard
│
├── network_automation/
│   ├── __init__.py
│   ├── routes.py            # Network automation routes
│   ├── service.py           # Business logic for config generation/validation/deployment
│   ├── config_generator.py  # GENAI config generation
│   ├── validator.py         # Configuration validation
│   └── deployer.py          # Configuration deployment
│
├── network_operations/
│   ├── __init__.py
│   ├── routes.py            # Network operations routes
│   ├── service.py           # Business logic for audit/troubleshoot/baseline
│   ├── auditor.py           # Network audit functionality
│   ├── troubleshooter.py    # Troubleshooting assistance
│   └── baseliner.py         # Network baseline operations
│
├── devices/
│   ├── __init__.py
│   ├── routes.py            # Device management routes
│   ├── service.py           # Business logic for device management
│   ├── manager.py           # Device CRUD operations
│   └── poller.py            # Device polling functionality
│
├── settings/
│   ├── __init__.py
│   ├── routes.py            # Settings routes
│   ├── service.py           # Business logic for settings
│   ├── llm_manager.py       # LLM provider management
│   └── api_manager.py       # API key management
│
├── chat/
│   ├── __init__.py
│   ├── routes.py            # Chat routes
│   ├── service.py           # Business logic for chat
│   ├── agent.py             # Agentic AI implementation
│   ├── rag.py               # Retrieval-Augmented Generation
│   └── memory.py            # Conversation memory management
│
├── ai/
│   ├── __init__.py
│   ├── llm_factory.py       # Factory for different LLM providers
│   ├── openai_client.py     # OpenAI API client
│   ├── groq_client.py       # Groq API client
│   ├── openrouter_client.py # OpenRouter API client
│   ├── crewai_integration.py# CrewAI integration
│   ├── langchain_integration.py # LangChain integration
│   └── langgraph_integration.py # LangGraph integration
│
├── network/
│   ├── __init__.py
│   ├── connection_manager.py # SSH/Telnet connection management
│   ├── netmiko_adapter.py   # Netmiko integration
│   ├── telnet_adapter.py    # Telnet integration
│   ├── genie_adapter.py     # Cisco Genie/PyATS integration
│   └── nonir_adapter.py     # Nonir modules integration
│
├── database/
│   ├── __init__.py
│   ├── models.py            # Database models
│   ├── connection.py        # Database connection
│   └── migrations/          # Database migrations
│
├── utils/
│   ├── __init__.py
│   ├── logger.py            # Logging utility
│   ├── config.py            # Configuration management
│   └── exceptions.py        # Custom exceptions
│
├── tests/
│   ├── __init__.py
│   ├── test_dashboard/
│   ├── test_network_automation/
│   ├── test_network_operations/
│   ├── test_devices/
│   ├── test_settings/
│   ├── test_chat/
│   ├── test_ai/
│   └── test_network/
│
├── config/
│   ├── __init__.py
│   ├── settings.py          # Application settings
│   └── environment.py       # Environment configuration
│
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
└── docker-compose.yml       # Docker Compose configuration
```

## Folder Descriptions

### 1. api/
Central API gateway that routes requests to appropriate services. Contains middleware for authentication, logging, and other cross-cutting concerns.

### 2. dashboard/
Handles all dashboard-related functionality including metrics aggregation, notifications, and system overview.

### 3. network_automation/
Manages configuration generation, validation, and deployment workflows. Contains specialized modules for each phase of the automation process.

### 4. network_operations/
Implements audit, troubleshooting, and baseline functionalities. Each operation type has its own module for clear separation.

### 5. devices/
Manages all device-related operations including CRUD operations, polling, and connectivity testing.

### 6. settings/
Handles application settings including LLM provider selection, API key management, and user preferences.

### 7. chat/
Implements the chat interface with agentic AI, RAG capabilities, and conversation memory management.

### 8. ai/
Centralizes all AI/LLM integrations. Contains adapters for different providers and agentic frameworks.

### 9. network/
Encapsulates all network communication logic including SSH/Telnet connections and device interactions.

### 10. database/
Contains database models, connection logic, and migration scripts.

### 11. utils/
Utility functions and common components used across the application.

### 12. tests/
Organized test suite that mirrors the application structure for easy maintenance.

### 13. config/
Application configuration and environment management.

## Communication Between Folders
- All inter-folder communication happens through the API layer
- Each folder exposes well-defined interfaces through its routes.py file
- Shared utilities and common components are in the utils/ folder
- Database interactions are centralized in the database/ folder
- AI integrations are abstracted in the ai/ folder
- Network operations are encapsulated in the network/ folder