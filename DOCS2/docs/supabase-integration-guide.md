# Supabase Integration Guide

This document explains how Supabase is integrated into the Network Automation Platform.

## Overview

The application uses Supabase for:
- Authentication (currently bypassed with mock auth)
- Database operations
- Edge functions for backend logic
- Real-time data synchronization

## Client Configuration

### Supabase Client Setup
**File**: `src/integrations/supabase/client.ts`

```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://placeholder.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'placeholder-key'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

**Purpose**: 
- Initializes Supabase client for frontend use
- Handles authentication and database queries
- Manages real-time subscriptions

## Edge Functions

### 1. AI Automation Function
**File**: `supabase/functions/ai-automation/index.ts`
**Purpose**: Handles AI-powered network configuration generation

**Endpoints**: `POST /ai-automation`

**Request Format**:
```typescript
{
  action: string,        // 'generate', 'validate', 'chat', 'analyze'
  prompt: string,        // User's configuration request
  context?: any,         // Additional context data
  deviceType?: string,   // Device type (router, switch, etc.)
  vendor?: string        // Vendor (cisco, juniper, etc.)
}
```

**Response Format**:
```typescript
{
  response: string,      // AI-generated response
  sessionId: string,     // Conversation session ID
  model: string,         // AI model used
  tokensUsed: number,    // Token consumption
  responseTime: number   // Processing time in ms
}
```

**Key Features**:
- Integrates with OpenAI and Anthropic APIs
- Stores conversation history in database
- Handles different automation actions
- Provides network-specific prompt engineering

---

### 2. OpenRouter AI Function
**File**: `supabase/functions/openrouter-ai/index.ts`
**Purpose**: Alternative AI provider using OpenRouter

**Endpoints**: `POST /openrouter-ai`

**Request Format**:
```typescript
{
  action: string,
  prompt: string,
  context?: any,
  model?: string,        // Specific model selection
  sessionId?: string     // Conversation continuation
}
```

**Features**:
- Multiple AI model support
- Cost-effective AI access
- Same interface as main AI function
- Conversation history tracking

---

### 3. Device Operations Function
**File**: `supabase/functions/device-operations/index.ts`
**Purpose**: Manages network device operations

**Endpoints**: `POST /device-operations`

**Request Format**:
```typescript
{
  action: string,              // 'connect', 'backup', 'restore', 'deploy', 'validate'
  deviceId: string,           // Target device ID
  config?: string,            // Configuration data (for restore/deploy)
  connectionParams?: any      // SSH/API connection parameters
}
```

**Response Format**:
```typescript
{
  success: boolean,
  result: string,             // Operation result/output
  duration: number,           // Operation time in ms
  checksum?: string           // Configuration checksum
}
```

**Supported Operations**:
- **Connect**: Test device connectivity
- **Backup**: Save current configuration
- **Restore**: Apply saved configuration
- **Deploy**: Push new configuration
- **Validate**: Check configuration syntax

## Database Schema

### Tables Used

#### 1. network_devices
**Purpose**: Stores network device inventory
**Columns**:
- `id`: Unique device identifier
- `name`: Device name
- `type`: Device type (router, switch, firewall)
- `vendor`: Manufacturer (cisco, juniper, arista)
- `ip_address`: Device IP address
- `status`: Current status (online, offline, error)
- `config_version`: Configuration version
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

#### 2. network_operations
**Purpose**: Tracks network operations history
**Columns**:
- `id`: Operation ID
- `device_id`: Target device reference
- `operation_type`: Type of operation performed
- `status`: Operation status (pending, success, failed)
- `result`: Operation output/result
- `duration`: Operation duration in ms
- `created_at`: Operation timestamp
- `user_id`: User who initiated operation

#### 3. ai_conversations
**Purpose**: Stores AI chat history
**Columns**:
- `id`: Conversation entry ID
- `session_id`: Conversation session
- `user_message`: User's input prompt
- `ai_response`: AI's response
- `model_used`: AI model identifier
- `tokens_used`: Token consumption
- `response_time`: Processing time
- `created_at`: Message timestamp
- `user_id`: User reference

#### 4. device_configurations
**Purpose**: Stores device configuration versions
**Columns**:
- `id`: Configuration ID
- `device_id`: Device reference
- `config_data`: Configuration content
- `checksum`: Configuration hash
- `version`: Version number
- `is_active`: Current active config
- `created_at`: Creation timestamp

## Authentication Integration

### Current Implementation
The application currently uses **mock authentication** that bypasses Supabase Auth:

```typescript
// Mock user created in AuthProvider
const mockUser = {
  id: 'mock-admin-user',
  email: 'admin@admin.com',
  // ... other user properties
} as User
```

### Full Authentication Setup (Not Currently Active)
For production use, implement proper Supabase authentication:

```typescript
// Sign up
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'password'
})

// Sign in
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password'
})

// Sign out
const { error } = await supabase.auth.signOut()
```

## Real-time Features

### Subscription Setup
```typescript
// Listen to device status changes
const subscription = supabase
  .channel('network_devices')
  .on('postgres_changes', 
    { event: 'UPDATE', schema: 'public', table: 'network_devices' },
    (payload) => {
      // Handle device status updates
    }
  )
  .subscribe()
```

### Use Cases
- Real-time device status updates
- Live operation progress tracking
- Instant configuration change notifications
- Multi-user collaboration features

## Error Handling

### API Errors
```typescript
try {
  const { data, error } = await supabase
    .from('network_devices')
    .select('*')
  
  if (error) throw error
  return data
} catch (error) {
  console.error('Database error:', error)
  // Handle error appropriately
}
```

### Edge Function Errors
```typescript
try {
  const response = await supabase.functions.invoke('ai-automation', {
    body: { action: 'generate', prompt: 'Configure OSPF' }
  })
  
  if (response.error) throw response.error
  return response.data
} catch (error) {
  console.error('Function error:', error)
  // Handle error with user feedback
}
```

## Environment Variables

### Required Variables
- `VITE_SUPABASE_URL`: Supabase project URL
- `VITE_SUPABASE_ANON_KEY`: Public anonymous key
- `OPENAI_API_KEY`: OpenAI API key (for edge functions)
- `ANTHROPIC_API_KEY`: Anthropic API key (for edge functions)
- `OPENROUTER_API_KEY`: OpenRouter API key (optional)

### Development vs Production
- Development: Uses placeholder values for quick setup
- Production: Requires actual Supabase project and API keys

## Security Considerations

### Row Level Security (RLS)
Currently not implemented but recommended for production:

```sql
-- Enable RLS on tables
ALTER TABLE network_devices ENABLE ROW LEVEL SECURITY;

-- Create policies for user access
CREATE POLICY "Users can view their own devices" 
ON network_devices FOR SELECT 
USING (auth.uid() = user_id);
```

### API Key Management
- Store API keys in Supabase environment variables
- Never expose keys in frontend code
- Use edge functions for secure API calls

### Authentication Security
- Implement proper password policies
- Use email verification for signups
- Consider multi-factor authentication
- Implement session management
