# File Structure Overview

This document explains the purpose and function of each file in the Network Automation Platform.

## Core Application Files

### src/App.tsx
**Purpose**: Main application component that sets up routing and providers
**Function**: 
- Configures React Query for state management
- Sets up authentication provider
- Defines all application routes
- Provides toast notifications and tooltips

### src/main.tsx
**Purpose**: Application entry point
**Function**: 
- Renders the root App component
- Mounts the application to the DOM

## Layout Components

### src/components/layout/MainLayout.tsx
**Purpose**: Main application layout wrapper
**Function**:
- Provides sidebar navigation
- Contains top header with search and user actions
- Handles sidebar toggle functionality
- Manages user logout functionality

### src/components/layout/AppSidebar.tsx
**Purpose**: Application sidebar navigation
**Function**:
- Displays navigation menu items
- Shows current active route
- Provides collapsible sidebar functionality
- Contains application logo and branding

## Authentication

### src/components/auth/AuthProvider.tsx
**Purpose**: Authentication context provider
**Function**:
- Manages user authentication state
- Provides mock authentication (bypasses actual login)
- Exposes signIn, signUp, signOut functions
- Creates mock admin user for development

## Page Components

### src/pages/Dashboard.tsx
**Purpose**: Main dashboard view
**Function**:
- Displays overview of network operations
- Shows system metrics and statistics
- Provides quick access to main features

### src/pages/Automation.tsx
**Purpose**: AI-powered automation interface
**Function**:
- Handles AI configuration generation
- Manages device selection and operations
- Provides configuration validation
- Integrates with Supabase edge functions

### src/pages/Operations.tsx
**Purpose**: Network operations management
**Function**:
- Displays network operation history
- Manages device operations (connect, backup, restore)
- Shows operation status and results

### src/pages/Devices.tsx
**Purpose**: Network device management
**Function**:
- Lists all network devices
- Manages device configurations
- Handles device status monitoring

### src/pages/Settings.tsx
**Purpose**: Application settings
**Function**:
- User preferences management
- System configuration options
- Account settings

### src/pages/Chat.tsx
**Purpose**: AI chat interface
**Function**:
- Provides conversational AI interface
- Handles network automation queries
- Manages chat history and sessions

### src/pages/NotFound.tsx
**Purpose**: 404 error page
**Function**:
- Displays when user navigates to non-existent route
- Logs navigation errors
- Provides link back to home

## UI Components (shadcn/ui)

### src/components/ui/
**Purpose**: Reusable UI component library
**Function**:
- Provides consistent design system
- Implements shadcn/ui components
- Includes buttons, forms, dialogs, etc.
- Customizable with variants and themes

## Configuration Files

### src/index.css
**Purpose**: Global styles and design tokens
**Function**:
- Defines CSS custom properties for theming
- Sets up Tailwind CSS base styles
- Includes component-specific styles

### tailwind.config.ts
**Purpose**: Tailwind CSS configuration
**Function**:
- Extends default Tailwind theme
- Defines custom colors and utilities
- Configures design system tokens

### vite.config.ts
**Purpose**: Vite build tool configuration
**Function**:
- Configures development server
- Sets up path aliases (@/ for src/)
- Optimizes build process

## Supabase Integration

### src/integrations/supabase/client.ts
**Purpose**: Supabase client configuration
**Function**:
- Initializes Supabase connection
- Provides database and auth access
- Configured for development environment

### supabase/functions/
**Purpose**: Edge functions for backend logic
**Function**:
- ai-automation: Handles AI model interactions
- openrouter-ai: Alternative AI provider integration
- device-operations: Network device management APIs

## Utility Files

### src/lib/utils.ts
**Purpose**: Common utility functions
**Function**:
- Provides helper functions
- Includes className merging utilities
- Common data manipulation functions

### src/hooks/
**Purpose**: Custom React hooks
**Function**:
- use-mobile.tsx: Mobile device detection
- use-toast.ts: Toast notification management