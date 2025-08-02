# Product Requirements Document (PRD)
## Network Automation Application with GENAI

### 1. Overview
This document outlines the requirements for a network automation application that leverages GENAI, LLMs, and agentic AI to automate Cisco network operations. The application will support Cisco IOS, IOSXR, and IOSXE devices with dummy devices (R15-R25) for testing purposes.

### 2. Product Purpose
To provide network engineers with an intelligent automation platform that can generate, validate, and deploy network configurations while also performing audits, troubleshooting, and baseline analysis using GENAI capabilities.

### 3. Key Features

#### 3.1 Dashboard
- System overview and status monitoring
- Quick access to recent activities
- Performance metrics visualization
- Alert notifications

#### 3.2 GENAI Network Automation
- Configuration generation using natural language prompts
- Configuration validation and cleaning
- Secure deployment of validated configurations
- Confirmation of successful pushes

#### 3.3 GENAI Network Operations
- Network audit capabilities
- Intelligent troubleshooting assistance
- Network baseline creation and comparison
- Performance analysis

#### 3.4 Devices Management
- Add, delete, and edit network devices
- Device polling for status updates
- Ping testing functionality
- Device inventory management

#### 3.5 Settings
- LLM selection (OpenAI, Groq, OpenRouter)
- API key management (add, delete, edit, save)
- Remote API configuration
- Chat settings (agentic, RAG, memory)

#### 3.6 Chat Interface
- Agentic AI interactions
- Retrieval-Augmented Generation (RAG) support
- Conversation memory retention
- Context-aware responses

### 4. Technical Requirements

#### 4.1 AI/LLM Integration
- Primary: OpenAI API
- Compatible alternatives: Groq API, OpenRouter API
- Agentic frameworks: CrewAI, LangGraph, LangChain
- RAG implementations: Agentic RAG and Basic RAG

#### 4.2 Network Protocols
- SSH support via Python Netmiko
- Telnet support via Python libraries
- Cisco Genie with PyATS for configuration parsing
- Nonir modules for additional network operations

#### 4.3 Backend Architecture
- Each page/route will have its own backend folder
- API-based communication between components
- RESTful API design principles
- Modular and scalable structure

### 5. User Interface Requirements
- Web-based interface with 6 distinct pages
- Responsive design for various screen sizes
- Intuitive navigation between pages
- Real-time feedback for long-running operations

### 6. Security Requirements
- Secure storage of API keys and credentials
- Encrypted communication channels
- Role-based access control
- Audit logging for all operations

### 7. Performance Requirements
- Configuration generation within 30 seconds
- Device polling intervals configurable by user
- Support for concurrent operations
- Efficient memory management for large networks

### 8. Compatibility Requirements
- Cross-platform web application
- Support for modern browsers
- Integration with Cisco IOS, IOSXR, and IOSXE
- API compatibility with multiple LLM providers