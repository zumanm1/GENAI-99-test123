# Component Functions Guide

This document explains the function and purpose of each major component in the application.

## Layout Components

### MainLayout Component
**File**: `src/components/layout/MainLayout.tsx`
**Purpose**: Primary application layout structure

**Key Functions**:
- `MainLayout({ children })`: Main layout wrapper
  - Provides sidebar navigation
  - Contains top header with search functionality
  - Manages user actions (notifications, profile, logout)
  - Renders child components in main content area

**Props**:
- `children`: React nodes to render in main content area

**State Management**:
- Uses `useAuth()` hook for authentication
- Manages sidebar visibility via SidebarProvider

**Styling**:
- Responsive design with sidebar collapse
- Backdrop blur effects for modern UI
- Consistent spacing and layout structure

---

### AppSidebar Component
**File**: `src/components/layout/AppSidebar.tsx`
**Purpose**: Navigation sidebar with menu items

**Key Functions**:
- Renders navigation menu items
- Highlights active route
- Provides collapsible functionality
- Shows application branding

**Navigation Items**:
- Dashboard: System overview
- Automation: AI-powered configuration
- Operations: Network operations management
- Devices: Device inventory
- Settings: Application preferences
- Chat: AI assistance interface

**State Management**:
- Uses `useLocation()` to determine active route
- Integrates with SidebarProvider for collapse state

## Authentication Components

### AuthProvider Component
**File**: `src/components/auth/AuthProvider.tsx`
**Purpose**: Authentication context and state management

**Key Functions**:
- `AuthProvider({ children })`: Context provider wrapper
- `signIn(email, password)`: User login (currently mock)
- `signUp(email, password)`: User registration (currently mock)
- `signOut()`: User logout (currently mock)

**Context Values**:
- `user`: Current user object or null
- `loading`: Authentication loading state
- `signIn`, `signUp`, `signOut`: Authentication functions

**Current Implementation**:
- Mock authentication system
- Auto-creates admin user
- Bypasses actual Supabase authentication

## Page Components

### Dashboard Component
**File**: `src/pages/Dashboard.tsx`
**Purpose**: Main dashboard with system overview

**Key Features**:
- System metrics display
- Quick action buttons
- Recent activity summary
- Network health indicators

**Data Sources**:
- Network device status
- Recent operations
- System performance metrics

---

### Automation Component
**File**: `src/pages/Automation.tsx`
**Purpose**: AI-powered network configuration automation

**Key Functions**:
- Device type selection
- Configuration requirement input
- AI configuration generation
- Configuration validation and deployment

**API Integration**:
- Calls Supabase edge functions
- Integrates with AI providers (OpenAI/Anthropic)
- Manages configuration templates

**User Workflow**:
1. Select device vendor/type
2. Describe configuration needs
3. Generate configuration with AI
4. Validate and deploy

---

### Operations Component
**File**: `src/pages/Operations.tsx`
**Purpose**: Network operations monitoring and management

**Key Functions**:
- Operation history display
- Status filtering and sorting
- Operation retry functionality
- Log viewing and download

**Data Management**:
- Fetches from `network_operations` table
- Real-time status updates
- Operation result tracking

---

### Devices Component
**File**: `src/pages/Devices.tsx`
**Purpose**: Network device inventory management

**Key Functions**:
- Device listing with details
- Add/edit/delete devices
- Status monitoring
- Configuration management

**Device Properties**:
- Name, type, vendor
- IP address and credentials
- Status and health metrics
- Configuration version

---

### Settings Component
**File**: `src/pages/Settings.tsx`
**Purpose**: Application and user settings management

**Key Functions**:
- User profile editing
- System preferences
- API configuration
- Notification settings

**Settings Categories**:
- Profile: User information
- Preferences: UI and behavior
- API: Integration settings
- Security: Authentication options

---

### Chat Component
**File**: `src/pages/Chat.tsx`
**Purpose**: Conversational AI interface

**Key Functions**:
- Real-time chat interface
- Message history management
- Context-aware responses
- Command suggestions

**AI Integration**:
- Connects to AI automation functions
- Maintains conversation context
- Provides network expertise

## UI Components (shadcn/ui)

### Button Component
**File**: `src/components/ui/button.tsx`
**Purpose**: Reusable button component with variants

**Variants**:
- `default`: Primary button style
- `destructive`: Warning/danger actions
- `outline`: Secondary button style
- `secondary`: Alternative secondary style
- `ghost`: Minimal button style
- `link`: Link-styled button

**Sizes**:
- `default`: Standard size
- `sm`: Small button
- `lg`: Large button
- `icon`: Icon-only button

### Input Component
**File**: `src/components/ui/input.tsx`
**Purpose**: Styled input field component

**Features**:
- Consistent styling across app
- Focus states and validation
- Disabled and error states
- Accessible form integration

### Card Component
**File**: `src/components/ui/card.tsx`
**Purpose**: Container component for content sections

**Sub-components**:
- `Card`: Main container
- `CardHeader`: Header section
- `CardTitle`: Title element
- `CardDescription`: Description text
- `CardContent`: Main content area
- `CardFooter`: Footer section

## Utility Components

### Toast Component
**File**: `src/components/ui/toast.tsx`
**Purpose**: Notification system

**Types**:
- Success notifications
- Error messages
- Warning alerts
- Info messages

**Features**:
- Auto-dismiss timing
- Manual dismiss option
- Queue management
- Accessible announcements

### Dialog Component
**File**: `src/components/ui/dialog.tsx`
**Purpose**: Modal dialog system

**Sub-components**:
- `Dialog`: Main dialog wrapper
- `DialogTrigger`: Opens dialog
- `DialogContent`: Modal content
- `DialogHeader`: Header section
- `DialogTitle`: Dialog title
- `DialogDescription`: Description text

## Custom Hooks

### useAuth Hook
**Purpose**: Access authentication context

**Returns**:
- `user`: Current user object
- `loading`: Authentication loading state
- `signIn`, `signUp`, `signOut`: Auth functions

### useMobile Hook
**File**: `src/hooks/use-mobile.tsx`
**Purpose**: Detect mobile device viewport

**Returns**:
- `isMobile`: Boolean indicating mobile viewport

### useToast Hook
**File**: `src/hooks/use-toast.ts`
**Purpose**: Manage toast notifications

**Functions**:
- `toast()`: Show notification
- `dismiss()`: Hide notification
- Configuration options for styling and timing