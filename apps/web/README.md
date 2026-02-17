# ZETA Platform - Admin Panel

Modern, dark-themed admin panel for managing cities, bot configurations, products, and analytics in the ZETA Platform.

## 🚀 Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (Super Admin, City Admin, Manager)
- Protected routes with automatic redirects
- Persistent login state

### City Management
- Create and manage multiple cities
- City-specific settings and configurations
- Active/inactive status toggle
- Super Admin exclusive access

### Bot Configuration
- Large syntax-highlighted system prompt editor
- Manager Telegram handle configuration
- Escalation action selection (Link, Notify Manager, Bitrix)
- Optimistic UI updates
- Real-time configuration management

### Product Management
- Full CRUD operations for products
- Product activation/deactivation
- Price and description management
- City-scoped product lists
- Inline editing and deletion

### Analytics Dashboard
- Real-time conversation metrics (today, week, month)
- Average messages per conversation
- Top products inquired visualization
- Interactive charts using Recharts
- Time-series conversation data

### Audit Logs
- Complete audit trail of all actions
- User activity tracking
- Change history with detailed diffs
- Paginated log viewing
- Timestamp and entity tracking

### User Profile
- Profile information management
- Role and permissions display
- City access overview
- Account information

## 🛠️ Tech Stack

- **Framework:** Next.js 15 (App Router)
- **React:** 19
- **Language:** TypeScript
- **Styling:** TailwindCSS
- **State Management:** Zustand
- **Data Fetching:** React Query (@tanstack/react-query)
- **Charts:** Recharts
- **Icons:** Lucide React
- **HTTP Client:** Axios

## 📦 Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local and set NEXT_PUBLIC_API_URL

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🌐 Environment Variables

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:3001/api
```

For production (Vercel), set this in the Vercel dashboard.

## 📁 Project Structure

```
app/
├── (dashboard)/           # Protected dashboard routes
│   ├── dashboard/        # Main dashboard
│   ├── cities/           # City management
│   │   ├── [id]/        # City-specific routes
│   │   │   ├── settings/
│   │   │   ├── bot-config/
│   │   │   ├── products/
│   │   │   ├── analytics/
│   │   │   └── audit-logs/
│   │   └── new/         # Create new city
│   └── profile/         # User profile
├── login/               # Login page
├── register/            # Registration page
└── layout.tsx           # Root layout

components/
├── auth/                # Authentication components
├── layout/              # Layout components (Sidebar, Navbar)
└── ui/                  # Reusable UI components

lib/
├── api.ts              # Axios instance with interceptors
├── store.ts            # Zustand state management
├── queries.ts          # React Query hooks
└── types.ts            # TypeScript type definitions
```

## 🎨 Design System

### Color Scheme (Dark Theme)
- **Background:** Black (#000000)
- **Cards/Surfaces:** Gray-900 (#111827)
- **Borders:** Gray-800 (#1F2937)
- **Text Primary:** White (#FFFFFF)
- **Text Secondary:** Gray-400 (#9CA3AF)
- **Primary (Blue):** #3B82F6
- **Success (Green):** #10B981
- **Warning (Yellow):** #F59E0B
- **Danger (Red):** #EF4444
- **Purple:** #8B5CF6

### Typography
- **Font Family:** Inter (sans-serif)
- **Headings:** Bold weight
- **Body:** Regular weight

## 🔐 Authentication Flow

1. User logs in via `/login`
2. JWT token received and stored in localStorage
3. Token automatically attached to all API requests
4. User redirected to `/dashboard`
5. Protected routes check authentication status
6. 401 responses trigger automatic logout

## 🧭 Routes & Access Control

### Public Routes
- `/` - Landing (redirects based on auth)
- `/login` - Login form
- `/register` - Registration (invite-only)

### Protected Routes (All Roles)
- `/dashboard` - Overview
- `/profile` - User profile

### City Admin & Super Admin
- `/cities/[id]/settings` - City settings
- `/cities/[id]/bot-config` - Bot configuration
- `/cities/[id]/analytics` - Analytics dashboard
- `/cities/[id]/audit-logs` - Audit trail

### All Roles (with City Access)
- `/cities/[id]/products` - Product management

### Super Admin Only
- `/cities` - City list
- `/cities/new` - Create new city

## 📊 State Management

### Zustand Store
```typescript
{
  user: User | null,
  token: string | null,
  selectedCityId: string | null,
  setUser: (user) => void,
  setToken: (token) => void,
  setSelectedCityId: (cityId) => void,
  logout: () => void,
  isAuthenticated: () => boolean,
  hasRole: (roles) => boolean,
  canAccessCity: (cityId) => boolean
}
```

### React Query
- Automatic caching and revalidation
- Optimistic updates
- Error handling
- Loading states

## 🚢 Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import project in Vercel dashboard
3. Set environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy

Vercel will automatically detect Next.js and configure build settings.

### Manual Deployment

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 🔧 Development

```bash
# Run development server with Turbopack
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Build
npm run build
```

## 📱 Responsive Design

The admin panel is fully responsive and works on:
- Desktop (1920px+)
- Laptop (1280px - 1919px)
- Tablet (768px - 1279px)
- Mobile (320px - 767px)

Sidebar collapses to hamburger menu on mobile (future enhancement).

## 🎯 Key Features Implementation

### City Selector
- Dropdown in navbar
- Filters cities based on user access
- Persists selection in Zustand store
- Updates available routes dynamically

### Bot Config
- Large textarea with monospace font
- Syntax highlighting ready (can add code editor)
- Manager Telegram handle validation
- Escalation action dropdown

### Analytics
- Interactive line and bar charts
- Real-time data updates
- Top products ranking
- Time-series visualization

### Audit Logs
- Paginated for performance
- Detailed change tracking
- Expandable change diffs
- User and timestamp info

## 🤝 Contributing

This is part of the ZETA Platform monorepo. Follow the monorepo guidelines for contributions.

## 📄 License

Proprietary - ZETA Platform

## 🆘 Support

For issues or questions, contact the development team.

---

Built with ❤️ by the ZETA team
