# Dashboard v2 - Technical Implementation Roadmap

Step-by-step plan to build your personal command center.

---

## 🎯 PROJECT OVERVIEW

**Goal:** Build a fast, real-time personal dashboard with 8 key widgets  
**Timeline:** 3-4 weeks (part-time) or 1-2 weeks (full-time)  
**Tech Stack:** Next.js 14, React, Tailwind CSS, Supabase, Stripe API

---

## 📋 PHASE 1: FOUNDATION (Days 1-3)

### Day 1: Project Setup
- [ ] Create Next.js 14 app with App Router
  ```bash
  npx create-next-app@latest dashboard-v2
  # Choose: TypeScript, Tailwind, App Router
  ```
- [ ] Set up Tailwind CSS with custom theme
- [ ] Configure environment variables
- [ ] Initialize Git repository
- [ ] Set up project structure:
  ```
  /app
    /dashboard
      page.tsx
    /api
      /revenue
      /health
      /wins
  /components
    /widgets
      RevenueTracker.tsx
      FloridaFund.tsx
      ...
  /lib
    /api
    /utils
  /types
  ```
- [ ] Install dependencies:
  ```bash
  npm install @supabase/supabase-js stripe recharts date-fns lucide-react
  npm install -D @types/node
  ```

### Day 2: Design System Setup
- [ ] Create color palette in `tailwind.config.js`
- [ ] Set up typography scale
- [ ] Build reusable UI components:
  - `Card` component (base for all widgets)
  - `LoadingSpinner` component
  - `ErrorBoundary` component
  - `Button` variants
  - `Badge` component
- [ ] Create layout template with header
- [ ] Implement dark mode toggle
- [ ] Set up responsive grid system

### Day 3: Authentication & Database
- [ ] Set up Supabase project
- [ ] Configure Supabase auth (email + OAuth)
- [ ] Create database tables:
  ```sql
  -- users table (handled by Supabase Auth)
  
  -- revenue_logs
  CREATE TABLE revenue_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    source TEXT NOT NULL, -- 'stripe' or 'gumroad'
    amount DECIMAL(10,2) NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
  );
  
  -- florida_fund
  CREATE TABLE florida_fund (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    goal_amount DECIMAL(10,2) NOT NULL,
    current_amount DECIMAL(10,2) DEFAULT 0,
    contributions JSONB,
    updated_at TIMESTAMP DEFAULT NOW()
  );
  
  -- fitness_logs
  CREATE TABLE fitness_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    date DATE NOT NULL,
    workout_completed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
  );
  
  -- wins
  CREATE TABLE wins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    title TEXT NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    category TEXT,
    created_at TIMESTAMP DEFAULT NOW()
  );
  
  -- system_health
  CREATE TABLE system_health (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name TEXT NOT NULL,
    status TEXT NOT NULL, -- 'online', 'degraded', 'offline'
    response_time INT,
    last_checked TIMESTAMP DEFAULT NOW()
  );
  
  -- quick_actions
  CREATE TABLE quick_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    label TEXT NOT NULL,
    icon TEXT NOT NULL,
    action TEXT NOT NULL,
    order_index INT,
    created_at TIMESTAMP DEFAULT NOW()
  );
  ```
- [ ] Set up Row Level Security (RLS) policies
- [ ] Create Supabase client helper (`/lib/supabase.ts`)
- [ ] Test database connections

---

## 📋 PHASE 2: CORE WIDGETS (Days 4-10)

### Day 4: Revenue Tracker Widget
- [ ] Create `/api/revenue/route.ts` endpoint
- [ ] Integrate Stripe API:
  ```ts
  import Stripe from 'stripe';
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);
  // Fetch balance transactions, charges, etc.
  ```
- [ ] Integrate Gumroad API (if applicable)
- [ ] Build `RevenueTracker.tsx` component
- [ ] Add chart (Recharts line chart)
- [ ] Implement timeframe selector (7d, 30d, 90d, 1y)
- [ ] Add loading and error states
- [ ] Calculate growth percentage
- [ ] Store aggregated data in Supabase (daily sync)

### Day 5: Florida Fund Widget
- [ ] Create `/api/florida-fund/route.ts`
- [ ] Build `FloridaFund.tsx` component
- [ ] Create progress bar component
- [ ] Calculate estimated completion date
- [ ] Add contribution history list
- [ ] Build "Add Contribution" modal
- [ ] Integrate with Plaid (optional, or manual entries)
- [ ] Add animation to progress bar

### Day 6: Fitness Streak Widget
- [ ] Create `/api/fitness/route.ts`
- [ ] Build `FitnessStreak.tsx` component
- [ ] Implement calendar grid (current month + previous)
- [ ] Calculate current streak logic:
  ```ts
  function calculateStreak(logs: FitnessLog[]): number {
    // Sort by date descending
    // Count consecutive days from today
    // Return streak count
  }
  ```
- [ ] Show longest streak
- [ ] Build "Log Workout" quick action
- [ ] Add hover tooltips for each day
- [ ] Highlight today

### Day 7: Quick Actions Widget
- [ ] Build `QuickActions.tsx` component
- [ ] Create 8 default actions:
  1. New Note → Opens note modal
  2. Log Workout → Logs fitness entry
  3. Add Revenue → Opens revenue form
  4. View Stats → Navigates to stats page
  5. Set Goal → Opens goal modal
  6. Check Email → Opens email client
  7. Run Backup → Triggers backup script
  8. Open Site → Opens main website
- [ ] Implement action handler:
  ```ts
  const handleAction = async (action: string) => {
    switch(action) {
      case 'new_note':
        // Open modal
      case 'log_workout':
        // API call
      case 'add_revenue':
        // Open form
      // ...
    }
  };
  ```
- [ ] Make actions customizable (drag & drop)
- [ ] Add loading states for async actions

### Day 8: System Health Widget
- [ ] Create `/api/health/route.ts`
- [ ] Implement health checks:
  ```ts
  const checks = [
    { name: 'API Gateway', url: 'https://api.example.com/health' },
    { name: 'Database', check: async () => await supabase.from('users').select('count') },
    { name: 'Stripe', url: 'https://api.stripe.com/v1' },
    { name: 'Email Service', check: async () => /* ping email API */ },
  ];
  ```
- [ ] Build `SystemHealth.tsx` component
- [ ] Add status indicators (● green, ⚠️ yellow, ❌ red)
- [ ] Show response times
- [ ] Display recent activity log
- [ ] Auto-refresh every 5 minutes
- [ ] Add manual refresh button

### Day 9: Recent Wins Widget
- [ ] Create `/api/wins/route.ts`
- [ ] Build `RecentWins.tsx` component
- [ ] Display last 7 days of wins
- [ ] Add "Add Win" modal with form
- [ ] Implement auto-detection (optional):
  - New paying customers (from Stripe webhooks)
  - GitHub commits
  - Milestone achievements
- [ ] Add categories/tags
- [ ] Implement archive functionality

### Day 10: Today's Focus & Upcoming Widgets
- [ ] Create `/api/calendar/route.ts`
- [ ] Integrate Google Calendar API:
  ```ts
  import { google } from 'googleapis';
  const calendar = google.calendar('v3');
  // Fetch events for next 48 hours
  ```
- [ ] Build `TodaysFocus.tsx` component
- [ ] Add task management (3 priorities)
- [ ] Implement checkbox interactions
- [ ] Build `Upcoming.tsx` component
- [ ] Display next 48 hours of events
- [ ] Group by day (Today, Tomorrow)
- [ ] Add "Add Event" quick action

---

## 📋 PHASE 3: INTEGRATION & POLISH (Days 11-14)

### Day 11: Real-Time Updates
- [ ] Set up Server-Sent Events (SSE) or WebSockets
- [ ] Implement real-time updates for:
  - System Health (every 5 min)
  - Revenue Tracker (on new transaction)
  - Recent Wins (on new entry)
- [ ] Use Supabase Realtime for database changes:
  ```ts
  supabase
    .channel('wins')
    .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'wins' }, 
      (payload) => {
        // Update UI
      }
    )
    .subscribe();
  ```
- [ ] Add optimistic UI updates

### Day 12: Performance Optimization
- [ ] Implement data caching:
  - Use React Query or SWR for API calls
  - Cache widget data in localStorage
  - Show stale data while revalidating
- [ ] Lazy load widgets:
  ```tsx
  const RevenueTracker = dynamic(() => import('@/components/widgets/RevenueTracker'), {
    loading: () => <WidgetSkeleton />,
  });
  ```
- [ ] Add loading skeletons for each widget
- [ ] Optimize images (use Next.js Image component)
- [ ] Run Lighthouse audit (target: 90+ score)
- [ ] Implement code splitting
- [ ] Add service worker for offline support

### Day 13: Mobile Responsiveness
- [ ] Test all widgets on mobile (iPhone, Android)
- [ ] Adjust grid layout for mobile:
  - Single column on <768px
  - 2 columns on 768-1279px
  - 4 columns on 1280px+
- [ ] Make charts responsive
- [ ] Add swipeable navigation for widgets
- [ ] Implement bottom navigation bar for mobile
- [ ] Test on real devices
- [ ] Fix any touch interaction issues

### Day 14: Error Handling & Edge Cases
- [ ] Add error boundaries around each widget
- [ ] Implement fallback UI for errors
- [ ] Handle API failures gracefully
- [ ] Add retry logic for failed requests
- [ ] Test with network throttling
- [ ] Handle empty states (no data)
- [ ] Add user-friendly error messages
- [ ] Log errors to Sentry or similar

---

## 📋 PHASE 4: ADVANCED FEATURES (Days 15-18)

### Day 15: Widget Customization
- [ ] Build settings panel
- [ ] Allow users to:
  - Show/hide widgets
  - Reorder widgets (drag & drop)
  - Resize widgets (desktop only)
  - Change widget timeframes
- [ ] Use `react-grid-layout` for drag & drop:
  ```tsx
  import GridLayout from 'react-grid-layout';
  ```
- [ ] Save layout preferences to Supabase
- [ ] Add "Reset to Default" option

### Day 16: Data Export & Backup
- [ ] Build export functionality:
  - Export revenue data as CSV
  - Export fitness logs as JSON
  - Generate PDF reports
- [ ] Implement automated backups:
  - Daily database snapshots
  - Store in S3 or similar
- [ ] Add "Download All Data" feature (GDPR compliance)
- [ ] Create backup restore functionality

### Day 17: Notifications & Alerts
- [ ] Build notification system:
  - Browser notifications (Web Push API)
  - Email notifications (for critical events)
  - In-app notification center
- [ ] Set up alerts for:
  - System health issues
  - Revenue milestones
  - Fitness streak breaks
  - Upcoming events (2 hours before)
- [ ] Add notification preferences panel

### Day 18: Analytics & Insights
- [ ] Build analytics dashboard:
  - Most productive days
  - Revenue trends
  - Fitness patterns
  - Time allocation
- [ ] Add AI-powered insights (optional):
  ```ts
  // Use OpenAI/Claude to generate insights
  const insight = await generateInsight(userData);
  ```
- [ ] Display insights in a dedicated widget
- [ ] Track widget usage (which widgets are most viewed)

---

## 📋 PHASE 5: TESTING & DEPLOYMENT (Days 19-21)

### Day 19: Testing
- [ ] Write unit tests for utility functions:
  ```bash
  npm install -D jest @testing-library/react @testing-library/jest-dom
  ```
- [ ] Write integration tests for API routes
- [ ] Test API endpoints with Postman/Insomnia
- [ ] Manual QA testing:
  - All widgets load correctly
  - All buttons/actions work
  - Dark mode works
  - Responsive on all devices
  - No console errors
- [ ] Performance testing (Lighthouse, WebPageTest)
- [ ] Security audit (check API keys, auth, CORS)

### Day 20: Deployment Prep
- [ ] Set up production environment variables
- [ ] Configure Supabase production database
- [ ] Set up Stripe production keys
- [ ] Configure API rate limiting
- [ ] Set up monitoring (Sentry for errors, Vercel Analytics)
- [ ] Create deployment scripts
- [ ] Write README documentation
- [ ] Create user guide (how to use dashboard)

### Day 21: Deploy to Production
- [ ] Deploy to Vercel:
  ```bash
  npx vercel --prod
  ```
- [ ] Configure custom domain (optional)
- [ ] Set up SSL certificate (automatic with Vercel)
- [ ] Test production deployment thoroughly
- [ ] Monitor for errors in first 24 hours
- [ ] Create feedback form for yourself
- [ ] Share with friends for testing

---

## 🛠️ TECH STACK DETAILS

### Frontend
- **Framework:** Next.js 14 (App Router)
- **UI Library:** React 18
- **Styling:** Tailwind CSS
- **Charts:** Recharts or Chart.js
- **Icons:** Lucide React
- **Date handling:** date-fns
- **State management:** React Context or Zustand
- **Forms:** React Hook Form

### Backend
- **API:** Next.js API Routes
- **Database:** Supabase (PostgreSQL)
- **Auth:** Supabase Auth
- **Payments:** Stripe API
- **Calendar:** Google Calendar API
- **Real-time:** Supabase Realtime

### DevOps
- **Hosting:** Vercel
- **Database:** Supabase
- **Version Control:** Git + GitHub
- **CI/CD:** Vercel (automatic)
- **Monitoring:** Sentry + Vercel Analytics

---

## 📊 API INTEGRATION GUIDE

### Stripe Integration
```ts
// /lib/stripe.ts
import Stripe from 'stripe';

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
});

// Fetch transactions
export async function getRevenueData(startDate: Date, endDate: Date) {
  const charges = await stripe.charges.list({
    created: {
      gte: Math.floor(startDate.getTime() / 1000),
      lte: Math.floor(endDate.getTime() / 1000),
    },
    limit: 100,
  });
  
  return charges.data.map(charge => ({
    amount: charge.amount / 100,
    date: new Date(charge.created * 1000),
    source: 'stripe',
  }));
}
```

### Google Calendar Integration
```ts
// /lib/google-calendar.ts
import { google } from 'googleapis';

const oauth2Client = new google.auth.OAuth2(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET,
  process.env.GOOGLE_REDIRECT_URI
);

export async function getUpcomingEvents() {
  const calendar = google.calendar({ version: 'v3', auth: oauth2Client });
  
  const response = await calendar.events.list({
    calendarId: 'primary',
    timeMin: new Date().toISOString(),
    timeMax: new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString(),
    singleEvents: true,
    orderBy: 'startTime',
  });
  
  return response.data.items;
}
```

### Supabase Integration
```ts
// /lib/supabase.ts
import { createClient } from '@supabase/supabase-js';

export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

// Fetch fitness logs
export async function getFitnessLogs(userId: string, startDate: Date) {
  const { data, error } = await supabase
    .from('fitness_logs')
    .select('*')
    .eq('user_id', userId)
    .gte('date', startDate.toISOString())
    .order('date', { ascending: false });
  
  if (error) throw error;
  return data;
}
```

---

## 🎨 UI COMPONENT LIBRARY

Create reusable components:

```tsx
// /components/ui/Card.tsx
export function Card({ children, className }: CardProps) {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 ${className}`}>
      {children}
    </div>
  );
}

// /components/ui/WidgetHeader.tsx
export function WidgetHeader({ title, icon, actions }: WidgetHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-2">
        {icon}
        <h3 className="text-lg font-semibold">{title}</h3>
      </div>
      {actions}
    </div>
  );
}

// /components/ui/LoadingSpinner.tsx
export function LoadingSpinner() {
  return (
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
  );
}
```

---

## ✅ COMPLETION CHECKLIST

### Functionality
- [ ] All 8 widgets working
- [ ] Real-time updates functioning
- [ ] Authentication working
- [ ] Data persisting correctly
- [ ] API integrations successful

### Performance
- [ ] Lighthouse score >90
- [ ] Page load <2 seconds
- [ ] No layout shifts (CLS <0.1)
- [ ] Smooth animations (60fps)

### Design
- [ ] Responsive on all devices
- [ ] Dark mode working
- [ ] Consistent styling
- [ ] Accessible (WCAG AA)

### Deployment
- [ ] Deployed to production
- [ ] Custom domain configured (optional)
- [ ] Monitoring set up
- [ ] Backups automated

---

## 📈 POST-LAUNCH IMPROVEMENTS

### Week 2-4 After Launch
- Add more widget types (mood tracker, book list, etc.)
- Build mobile app (React Native/Expo)
- Add AI insights
- Implement collaborative features (share dashboard)
- Add export/import dashboard configurations
- Build public dashboard feature (share read-only version)

---

**Ready to build?** Start with Phase 1, Day 1. Set a timer for 2 hours, put on focus music, and ship something today. You've got this! 🚀
