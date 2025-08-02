# GENAI-Powered Network Automation Application

This is a comprehensive network automation application powered by a FastAPI backend and a static frontend. It is designed to be run natively using a Python virtual environment.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.12 or higher
- PostgreSQL

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/zumanm1/GENAI-99-test123.git
    cd GENAI-99-test123
    ```

2.  **Configure your environment**:
    -   Copy the `.env.example` file to a new file named `.env`.
    -   Update the `.env` file with your PostgreSQL database credentials.

3.  **Run the setup script**:
    This script will create a virtual environment, install all dependencies, and initialize the database.
    ```bash
    ./init_setup.sh
    ```

## How to Run the Application

After the initial setup, you can run the frontend and backend servers.

1.  **Activate the virtual environment**:
    ```bash
    source venv/bin/activate
    ```

2.  **Start the Frontend Server**:
    ```bash
    python frontend/server.py
    ```
    The frontend will be available at [http://localhost:8001](http://localhost:8001).

3.  **Start the Backend Server** (in a new terminal):
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8002
    ```
    The backend API will be available at [http://localhost:8002/docs](http://localhost:8002/docs).


## Overview
This is a network automation application that leverages GENAI, LLMs, and agentic AI to automate Cisco network operations. The application supports Cisco IOS, IOSXR, and IOSXE devices with dummy devices (R15-R25) for testing purposes.

## Features
- Dashboard with system overview and metrics
- GENAI Network Automation (configuration generation, validation, deployment)
- GENAI Network Operations (audit, troubleshooting, baseline)
- Device Management (add, delete, edit, poll, test ping)
- Settings (LLM selection, API key management)
- Chat Interface (agentic, RAG, memory)

## Technology Stack
- Backend: Python with FastAPI
- Frontend: HTML/CSS/JavaScript
- Database: PostgreSQL
- AI/ML: OpenAI, Groq, OpenRouter APIs with CrewAI, LangChain, LangGraph
- Network Libraries: Netmiko, Cisco Genie, PyATS

## Installation

### Option 1: Using Docker (Recommended)
**Note:** The Docker configuration is being updated to support the new dependency structure. For now, please use the Manual Installation.

1. Install Docker and Docker Compose (see [DOCKER_INSTRUCTIONS.md](DOCKER_INSTRUCTIONS.md) for detailed instructions)
2. Clone the repository
3. Run the application: `docker-compose up -d`
4. Access the application at http://localhost:5888

### Option 2: Manual Installation
This project uses separate dependency files to manage package conflicts and isolate modules.

1. **Clone the repository**

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Core Dependencies:**
   These are required to run the main application.
   ```bash
   pip install -r requirements-core.txt
   ```

4. **Install AI Dependencies (Optional):**
   These are only needed for GENAI features.
   ```bash
   pip install -r requirements-ai.txt
   ```

5. **Set up the database:**
   ```bash
   python init_db.py
   ```

6. **Run the application:**
   ```bash
   uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Usage
1. Access the web interface at http://localhost:5888 (Docker) or http://localhost:8000 (manual)
2. Login with username: `admin` and password: `admin123`
3. Configure LLM settings in the Settings page
4. Add network devices in the Devices page
5. Use the GENAI Network Automation page to generate and deploy configurations
6. Use the GENAI Network Operations page for audit, troubleshooting, and baseline operations
7. Interact with the AI through the Chat interface

## API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Documentation
- [Product Requirements Document](prd.md)
- [Architecture](architecture.md)
- [Backend Structure](backend_structure.md)
- [API Design](api_design.md)
- [AI Integration](ai_integration.md)
- [SSH/Telnet Integration](ssh_telnet_integration.md)
- [UI Design](ui_design.md)
- [Implementation Roadmap](implementation_roadmap.md)
- [Docker Installation and Startup Guide](DOCKER_INSTRUCTIONS.md)