# Vibe Coding - 10 Practice Projects

Progressive difficulty: Easy → Hard. Each project builds real skills while pair-programming with AI.

---

## 🌱 BEGINNER PROJECTS (Week 1-2)

### 1. Personal Portfolio Website
**Difficulty:** ⭐☆☆☆☆  
**Time:** 4-6 hours  
**Skills:** HTML, CSS, basic JavaScript

**What you'll build:**
A responsive single-page website showcasing your work, skills, and contact info.

**Key features:**
- Hero section with intro
- Projects/work gallery
- About me section
- Contact form
- Smooth scrolling navigation

**AI collaboration approach:**
- Ask AI to explain HTML structure
- Get CSS layout suggestions
- Request responsive design patterns
- Debug styling issues together

**Vibe coding in action:**
```
You: "I want a hero section with my name and a gradient background"
AI: Generates HTML + CSS with gradient
You: "Make it more vibrant, add animation"
AI: Updates with animation + color tweaks
```

**Tech stack:**
- HTML5
- CSS3 (or Tailwind CSS)
- Vanilla JavaScript
- Deployed on: Vercel, Netlify, or GitHub Pages

---

### 2. Todo List App
**Difficulty:** ⭐⭐☆☆☆  
**Time:** 6-8 hours  
**Skills:** JavaScript, DOM manipulation, local storage

**What you'll build:**
A functional task manager with add, edit, delete, and persistence.

**Key features:**
- Add new todos
- Mark complete/incomplete
- Delete todos
- Filter (all, active, completed)
- Save to localStorage (persists after refresh)

**AI collaboration approach:**
- Learn event listeners together
- Understand array methods (map, filter, reduce)
- Implement localStorage with AI guidance
- Refactor code for cleanliness

**Key learning moments:**
- "How do I save data without a database?" → localStorage
- "How can I filter todos?" → Array methods
- "Why isn't my button working?" → Event delegation

**Tech stack:**
- Vanilla JavaScript
- HTML/CSS
- Optional: React or Vue for extra challenge

**Bonus challenges:**
- Add due dates
- Implement priority levels
- Add categories/tags
- Dark mode toggle

---

### 3. Weather Dashboard
**Difficulty:** ⭐⭐☆☆☆  
**Time:** 8-10 hours  
**Skills:** API integration, async JavaScript, error handling

**What you'll build:**
A weather app that fetches real-time data and displays it beautifully.

**Key features:**
- Search by city name
- Display current weather (temp, conditions, humidity)
- 5-day forecast
- Weather icons
- Background changes based on conditions

**AI collaboration approach:**
- Learn fetch API and promises
- Understand JSON data structures
- Handle API errors gracefully
- Format dates and units properly

**API to use:**
- OpenWeatherMap API (free tier)
- WeatherAPI (free tier)

**Key learning moments:**
- "What's an API?" → AI explains and shows examples
- "How do I make async requests?" → Fetch/async-await
- "API returned an error" → Error handling patterns

**Tech stack:**
- JavaScript (fetch API)
- HTML/CSS
- API: OpenWeatherMap

---

## 🌿 INTERMEDIATE PROJECTS (Week 2-3)

### 4. Markdown Note-Taking App
**Difficulty:** ⭐⭐⭐☆☆  
**Time:** 12-15 hours  
**Skills:** React, state management, markdown parsing

**What you'll build:**
A split-pane markdown editor with live preview and save functionality.

**Key features:**
- Live markdown preview (type on left, see rendered on right)
- Save notes to localStorage
- Note list sidebar
- Create/edit/delete notes
- Search notes

**AI collaboration approach:**
- Learn React components and state
- Integrate markdown library (marked.js or react-markdown)
- Build reusable UI components
- Implement search logic

**Key learning moments:**
- "How do I manage state in React?" → useState, useEffect
- "How do I parse markdown?" → Libraries and how to use them
- "How can I make the UI responsive?" → Flexbox/Grid

**Tech stack:**
- React
- marked.js or react-markdown
- localStorage
- Tailwind CSS or styled-components

**Bonus challenges:**
- Export notes as PDF
- Syntax highlighting for code blocks
- Tag system
- Cloud sync (Firebase)

---

### 5. Budget Tracker
**Difficulty:** ⭐⭐⭐☆☆  
**Time:** 15-18 hours  
**Skills:** Forms, data validation, charts, date handling

**What you'll build:**
A personal finance app to track income and expenses with visualizations.

**Key features:**
- Add income/expense transactions
- Categorize transactions
- Monthly/weekly views
- Charts (pie chart for categories, line chart for trends)
- Running balance calculation
- Filter by date range

**AI collaboration approach:**
- Design data structure together
- Learn form validation
- Integrate Chart.js or Recharts
- Implement date filtering logic

**Key learning moments:**
- "How do I calculate totals?" → Array reduce method
- "How do I create charts?" → Chart libraries
- "How do I validate user input?" → Form validation patterns

**Tech stack:**
- React or Vue
- Chart.js or Recharts
- date-fns or Day.js (date utilities)
- localStorage or IndexedDB

---

### 6. Movie Search & Watchlist
**Difficulty:** ⭐⭐⭐☆☆  
**Time:** 12-15 hours  
**Skills:** API integration, complex UI, state management

**What you'll build:**
Search for movies (via API) and create a personal watchlist.

**Key features:**
- Search movies by title
- Display results with posters, ratings, descriptions
- Add movies to watchlist
- Mark as watched/unwatched
- Rating system
- Persist watchlist in localStorage

**AI collaboration approach:**
- Work with TMDB API
- Handle pagination
- Build card-based UI
- Implement search debouncing (don't API call on every keystroke)

**API to use:**
- The Movie Database (TMDB) API
- OMDb API

**Key learning moments:**
- "How do I prevent too many API calls?" → Debouncing
- "How do I display images?" → Image optimization
- "How do I handle loading states?" → Loading spinners

**Tech stack:**
- React
- TMDB API
- Tailwind CSS
- localStorage

---

## 🌳 ADVANCED PROJECTS (Week 3-4)

### 7. Full-Stack Flask Blog
**Difficulty:** ⭐⭐⭐⭐☆  
**Time:** 20-25 hours  
**Skills:** Python, Flask, databases, authentication

**What you'll build:**
A complete blog platform with user accounts and CRUD operations.

**Key features:**
- User registration/login
- Create, edit, delete blog posts
- Markdown support for posts
- Comments on posts
- User profiles
- Admin dashboard

**AI collaboration approach:**
- Learn Flask routing and templates
- Understand SQLAlchemy (ORM)
- Implement user authentication (Flask-Login)
- Build forms with Flask-WTF
- Deploy to production (Heroku, Railway, or Fly.io)

**Key learning moments:**
- "What's a database?" → SQL vs NoSQL, tables, relationships
- "How do I store passwords?" → Hashing (bcrypt)
- "How do I handle forms?" → Flask-WTF and validation

**Tech stack:**
- Backend: Python + Flask
- Database: SQLite (dev) / PostgreSQL (prod)
- Frontend: Jinja2 templates + Bootstrap/Tailwind
- Auth: Flask-Login

**Bonus challenges:**
- Image upload for posts
- Tags and categories
- Search functionality
- RSS feed

---

### 8. Real-Time Chat Application
**Difficulty:** ⭐⭐⭐⭐☆  
**Time:** 25-30 hours  
**Skills:** WebSockets, real-time communication, backend

**What you'll build:**
A live chat app where multiple users can talk in real-time.

**Key features:**
- Multiple chat rooms
- Real-time messaging (WebSockets)
- User nicknames
- "User is typing..." indicator
- Message history
- Online user list

**AI collaboration approach:**
- Understand WebSockets vs HTTP
- Learn Socket.io (makes WebSockets easier)
- Build Node.js/Express backend
- Handle concurrent connections
- Deploy to cloud platform

**Key learning moments:**
- "How does real-time work?" → WebSockets explained
- "How do I broadcast to all users?" → Socket.io rooms
- "How do I scale this?" → Redis adapter (advanced)

**Tech stack:**
- Backend: Node.js + Express + Socket.io
- Frontend: React + Socket.io-client
- Database: MongoDB or PostgreSQL (optional, for history)
- Deploy: Railway, Fly.io, or Heroku

---

### 9. E-Commerce Product Page
**Difficulty:** ⭐⭐⭐⭐☆  
**Time:** 25-30 hours  
**Skills:** Complex state, Stripe integration, checkout flow

**What you'll build:**
A realistic product store with cart and payment processing.

**Key features:**
- Product catalog with filtering/sorting
- Product detail pages
- Shopping cart (add/remove items)
- Checkout flow
- Stripe payment integration (test mode)
- Order confirmation page

**AI collaboration approach:**
- Design component architecture
- Implement cart state management (Context API or Redux)
- Learn Stripe API integration
- Build responsive product grids
- Handle edge cases (out of stock, etc.)

**Key learning moments:**
- "How do I manage cart state across pages?" → Context API
- "How do I accept payments?" → Stripe Checkout
- "How do I calculate totals with tax/shipping?" → Business logic

**Tech stack:**
- Frontend: Next.js or React
- Payments: Stripe
- State: Context API or Zustand
- Styling: Tailwind CSS

**Bonus challenges:**
- User accounts
- Order history
- Product reviews
- Inventory management

---

### 10. Full-Stack SaaS Dashboard
**Difficulty:** ⭐⭐⭐⭐⭐  
**Time:** 40+ hours  
**Skills:** Everything combined + deployment

**What you'll build:**
A mini SaaS product with authentication, subscriptions, and dashboard.

**Key features:**
- User registration/login (OAuth + email)
- Subscription plans (Stripe Billing)
- Protected dashboard with user data
- Settings page (profile, billing, account)
- Admin panel
- Email notifications
- Analytics tracking

**AI collaboration approach:**
- Design database schema together
- Implement JWT authentication
- Set up Stripe subscriptions
- Build reusable component library
- Write tests with AI guidance
- Deploy to production (CI/CD pipeline)

**Key learning moments:**
- "How do I structure a production app?" → Architecture patterns
- "How do I handle subscriptions?" → Stripe webhooks
- "How do I secure my app?" → Auth best practices
- "How do I test this?" → Unit + integration tests

**Tech stack:**
- Frontend: Next.js or React
- Backend: Next.js API routes, Express, or FastAPI
- Database: PostgreSQL (Supabase or Neon)
- Auth: NextAuth.js or Clerk
- Payments: Stripe
- Deploy: Vercel, Railway, or Fly.io

**This is your capstone project!** By the end, you'll have built a real SaaS that you could actually launch.

---

## 🎯 PROJECT SELECTION STRATEGY

### Week 1: Projects 1-3
Pick 2 of these to complete. Focus on fundamentals.

### Week 2: Projects 4-6
Complete 2-3. Start integrating libraries and APIs.

### Week 3: Projects 7-8
Pick 1 and go deep. Learn backend or real-time features.

### Week 4: Project 9 or 10
Choose your final project based on interest:
- **Project 9** if you want e-commerce skills
- **Project 10** if you want full SaaS experience

---

## 💡 HOW TO APPROACH EACH PROJECT

### 1. Planning Phase (with AI)
- "I want to build [project]. What's the best tech stack?"
- "Break this down into smaller tasks"
- "What are the main features I need?"

### 2. Building Phase (with AI)
- Start with basic structure (HTML/component skeleton)
- Add functionality one feature at a time
- Ask AI to explain confusing concepts
- Request code reviews: "Can you review this code and suggest improvements?"

### 3. Debugging Phase (with AI)
- "I'm getting this error: [paste error]"
- "My function isn't working as expected: [paste code]"
- "How can I optimize this?"

### 4. Polish Phase (with AI)
- "How can I make this UI look more professional?"
- "What accessibility improvements should I make?"
- "How do I deploy this?"

---

## 🏆 COMPLETION CRITERIA

For each project, consider it done when:
- ✅ All key features work
- ✅ Code is reasonably clean (no major duplication)
- ✅ Basic error handling exists
- ✅ Works on mobile and desktop
- ✅ Deployed somewhere (even if just GitHub Pages)
- ✅ You understand 80%+ of the code (AI wrote it WITH you, not FOR you)

---

## 📦 PROJECT TEMPLATES

**Starter repositories:**
- `vibe-coding/project-1-portfolio`
- `vibe-coding/project-2-todo`
- `vibe-coding/project-3-weather`
- ... etc

Each includes:
- Basic file structure
- README with requirements
- Starter code (just enough to begin)
- Links to relevant docs

---

## 🎓 LEARNING CHECKPOINTS

After each project, ask yourself:
1. What did I learn?
2. What was hardest?
3. What would I do differently?
4. What do I want to learn next?

Document these in a `learning-log.md` file.

---

**Remember:** The goal isn't perfect code. It's understanding. If you can explain what each line does and why it's there, you've succeeded. AI is your pair programmer, not your replacement. 💪
