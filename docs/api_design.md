# API Design and Communication

## Overview
This document outlines the API endpoints for each service and how components communicate with each other in the network automation application. All APIs follow RESTful principles and use JSON for data exchange.

## API Gateway Routes

### Authentication
```
POST   /api/auth/login          # User login
POST   /api/auth/logout         # User logout
GET    /api/auth/validate       # Validate authentication token
```

### Dashboard
```
GET    /api/dashboard/overview  # Get dashboard overview data
GET    /api/dashboard/metrics   # Get system metrics
GET    /api/dashboard/alerts    # Get recent alerts
```

### Network Automation
```
POST   /api/network-automation/config/generate   # Generate configuration
POST   /api/network-automation/config/validate   # Validate configuration
POST   /api/network-automation/config/deploy     # Deploy configuration
GET    /api/network-automation/config/status     # Get deployment status
```

### Network Operations
```
POST   /api/network-operations/audit             # Perform network audit
POST   /api/network-operations/troubleshoot      # Start troubleshooting session
POST   /api/network-operations/baseline/create   # Create network baseline
POST   /api/network-operations/baseline/compare  # Compare with baseline
```

### Devices
```
GET    /api/devices              # Get all devices
POST   /api/devices              # Add new device
GET    /api/devices/{id}         # Get specific device
PUT    /api/devices/{id}         # Update device
DELETE /api/devices/{id}         # Delete device
POST   /api/devices/{id}/poll    # Poll device status
POST   /api/devices/{id}/ping    # Ping test device
```

### Settings
```
GET    /api/settings/llm         # Get LLM settings
PUT    /api/settings/llm         # Update LLM settings
GET    /api/settings/api-keys    # Get API key settings
POST   /api/settings/api-keys    # Add new API key
PUT    /api/settings/api-keys/{id} # Update API key
DELETE /api/settings/api-keys/{id} # Delete API key
GET    /api/settings/chat        # Get chat settings
PUT    /api/settings/chat        # Update chat settings
```

### Chat
```
GET    /api/chat/history         # Get chat history
POST   /api/chat/message         # Send chat message
DELETE /api/chat/history         # Clear chat history
POST   /api/chat/agent           # Interact with agentic AI
```

## Internal Service Communication

### Service-to-Service Communication Patterns

#### 1. Request-Response Pattern
Services communicate via direct API calls for immediate responses:
```
Network Automation Service -> AI Service: Request config generation
AI Service -> Network Automation Service: Return generated config
```

#### 2. Asynchronous Processing Pattern
Long-running operations use task queues:
```
Network Automation Service -> Task Queue: Submit deployment task
Task Worker -> Network Execution Engine: Execute deployment
Task Worker -> Database: Store result
Frontend -> API Gateway: Poll for status
API Gateway -> Database: Retrieve result
```

#### 3. Event-Driven Pattern
Services publish events for loosely coupled communication:
```
Device Service -> Event Bus: DeviceAdded event
Network Operations Service -> Event Bus: Subscribe to DeviceAdded
Network Operations Service -> Event Bus: Receive DeviceAdded event
Network Operations Service -> Device Service: Initialize baseline
```

## API Data Models

### Device Model
```json
{
  "id": "string",
  "name": "string",
  "ip_address": "string",
  "device_type": "string", // ios, iosxr, iosxe
  "username": "string",
  "password": "string", // encrypted
  "port": "integer",
  "protocol": "string", // ssh, telnet
  "status": "string", // online, offline, error
  "last_polled": "datetime"
}
```

### Configuration Model
```json
{
  "id": "string",
  "device_id": "string",
  "content": "string",
  "status": "string", // draft, validated, deployed
  "created_at": "datetime",
  "validated_at": "datetime",
  "deployed_at": "datetime"
}
```

### Chat Message Model
```json
{
  "id": "string",
  "user_id": "string",
  "message": "string",
  "response": "string",
  "timestamp": "datetime",
  "context": "object" // Additional context for RAG
}
```

### LLM Settings Model
```json
{
  "provider": "string", // openai, groq, openrouter
  "api_key": "string", // encrypted
  "model": "string",
  "temperature": "number",
  "max_tokens": "integer"
}
```

## Error Handling

### Standard Error Response Format
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object"
  }
}
```

### Common HTTP Status Codes
- 200: Success
- 201: Created
- 204: No Content
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict
- 500: Internal Server Error
- 503: Service Unavailable

## Authentication and Authorization

### JWT Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "string",
    "username": "string",
    "role": "string", // admin, user
    "exp": "timestamp",
    "iat": "timestamp"
  },
  "signature": "string"
}
```

### API Key Authentication
For service-to-service communication:
```
Authorization: Bearer <api_key>
```

## Rate Limiting

### Limits by Endpoint Category
- Authentication: 10 requests/minute
- Dashboard: 60 requests/minute
- Network Automation: 30 requests/minute
- Network Operations: 30 requests/minute
- Devices: 60 requests/minute
- Settings: 60 requests/minute
- Chat: 120 requests/minute

### Rate Limit Response Headers
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1627845600
```

## WebSocket Communication (for real-time updates)

### Dashboard Updates
```
WebSocket Endpoint: /ws/dashboard
Events:
- metrics_update
- alert_notification
- system_status
```

### Chat Updates
```
WebSocket Endpoint: /ws/chat
Events:
- message_received
- agent_typing
- agent_response
```

## API Versioning
All APIs are versioned using URL path:
```
/v1/api/dashboard/overview
```

## Security Considerations

1. All API communications use HTTPS
2. Sensitive data (passwords, API keys) encrypted at rest
3. Input validation on all endpoints
4. CORS policies properly configured
5. API keys rotated regularly
6. Audit logging for all operations