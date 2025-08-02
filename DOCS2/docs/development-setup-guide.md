# Development Setup Guide

This document provides step-by-step instructions for setting up the Network Automation Platform development environment.

## Prerequisites

### Required Software
- **Node.js**: Version 18 or higher
- **npm**: Version 8 or higher (comes with Node.js)
- **Git**: For version control

### Recommended Tools
- **VS Code**: IDE with excellent TypeScript support
- **Chrome DevTools**: For debugging
- **Postman**: For API testing
- **Supabase CLI**: For local development (optional)

## Project Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd network-automation-platform
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Environment Configuration
Create a `.env.local` file in the project root:

```env
# Supabase Configuration
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# AI API Keys (for edge functions)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
```

**Note**: The application currently works with placeholder values for quick development setup.

### 4. Start Development Server
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Development Workflow

### Project Structure
```
src/
├── components/          # Reusable UI components
│   ├── auth/           # Authentication components
│   ├── layout/         # Layout components
│   └── ui/             # shadcn/ui components
├── pages/              # Route components
├── hooks/              # Custom React hooks
├── lib/                # Utility functions
├── integrations/       # External service integrations
└── index.css          # Global styles and design tokens

supabase/
├── functions/          # Edge functions
│   ├── ai-automation/
│   ├── openrouter-ai/
│   └── device-operations/
└── config.toml        # Supabase configuration

docs/                   # Documentation files
```

### Key Technologies

#### Frontend Stack
- **React 18**: UI library with hooks and functional components
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Pre-built, customizable UI components

#### Backend & Data
- **Supabase**: Backend-as-a-Service platform
- **PostgreSQL**: Database (managed by Supabase)
- **Edge Functions**: Serverless functions (Deno runtime)

#### State Management
- **React Query**: Server state management
- **React Context**: Global state management
- **React Router**: Client-side routing

## Available Scripts

### Development Commands
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint
```

### Supabase Commands (if CLI installed)
```bash
# Start local Supabase
supabase start

# Deploy edge functions
supabase functions deploy ai-automation

# Generate types
supabase gen types typescript --local > src/integrations/supabase/types.ts
```

## Development Guidelines

### Code Style
- Use TypeScript for all new files
- Follow React functional component patterns
- Use Tailwind CSS for styling (avoid custom CSS)
- Implement proper error handling
- Write descriptive component and function names

### Component Structure
```typescript
// Example component structure
interface ComponentProps {
  // Define prop types
}

export function Component({ prop1, prop2 }: ComponentProps) {
  // Hooks at the top
  const [state, setState] = useState()
  
  // Event handlers
  const handleEvent = () => {
    // Handler logic
  }
  
  // Render
  return (
    <div className="tailwind-classes">
      {/* Component JSX */}
    </div>
  )
}
```

### File Naming Conventions
- Components: `PascalCase.tsx`
- Hooks: `use-kebab-case.ts`
- Utilities: `kebab-case.ts`
- Pages: `PascalCase.tsx`
- Types: `PascalCase.ts`

### Design System Usage
- Use semantic color tokens from `index.css`
- Leverage shadcn/ui components
- Create component variants instead of custom styles
- Maintain consistent spacing and typography

### State Management Patterns
```typescript
// Local state
const [data, setData] = useState()

// Context state
const { user, signOut } = useAuth()

// Server state
const { data, isLoading, error } = useQuery({
  queryKey: ['devices'],
  queryFn: fetchDevices
})
```

## Debugging

### Development Tools

#### React DevTools
- Install React DevTools browser extension
- Inspect component hierarchy and props
- Monitor state changes and re-renders

#### Console Logging
```typescript
// Structured logging
console.log('User action:', { action: 'click', element: 'button' })

// Error logging
console.error('API Error:', error)

// Development-only logging
if (process.env.NODE_ENV === 'development') {
  console.log('Debug info:', data)
}
```

#### Network Debugging
- Use browser DevTools Network tab
- Monitor API calls and responses
- Check for CORS issues
- Verify request/response formats

### Common Issues

#### TypeScript Errors
- Check for missing type definitions
- Verify import paths are correct
- Ensure proper interface implementations

#### Styling Issues
- Verify Tailwind classes are valid
- Check for CSS specificity conflicts
- Ensure design tokens are used correctly

#### State Management Issues
- Check React Query cache invalidation
- Verify context provider placement
- Monitor re-render cycles

## Testing

### Unit Testing (Future Implementation)
```bash
# Install testing dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest
```

### Manual Testing Checklist
- [ ] All routes load correctly
- [ ] Sidebar navigation works
- [ ] Mock authentication functions
- [ ] API calls complete successfully
- [ ] UI components render properly
- [ ] Responsive design works on mobile

## Deployment

### Build Process
```bash
# Create production build
npm run build

# Test production build locally
npm run preview
```

### Environment Variables for Production
Ensure all environment variables are configured in your hosting platform:
- Supabase URL and keys
- API keys for AI services
- Any additional configuration

### Hosting Platforms
- **Vercel**: Recommended for React applications
- **Netlify**: Good alternative with easy setup
- **Supabase Hosting**: Native integration
- **Custom VPS**: For full control

## Contributing

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature description"

# Push to remote
git push origin feature/new-feature

# Create pull request
```

### Code Review Checklist
- [ ] Code follows project conventions
- [ ] TypeScript types are properly defined
- [ ] Components are properly documented
- [ ] No console errors in development
- [ ] Responsive design is maintained
- [ ] Accessibility considerations are addressed

## Documentation

### Updating Documentation
- Keep README.md current with setup instructions
- Update component documentation for new features
- Maintain API documentation for edge functions
- Document any breaking changes

### Code Documentation
```typescript
/**
 * Generates network configuration using AI
 * @param deviceType - Type of network device
 * @param requirements - Configuration requirements
 * @returns Generated configuration string
 */
async function generateConfig(deviceType: string, requirements: string): Promise<string> {
  // Implementation
}
```

This setup guide should get you started with development. For specific feature implementation, refer to the component and route documentation files.