# DEPLOYMENTS.md - Live URLs & Production Endpoints

## Active Deployments

### Lean - Fitness Tracker App
- **Production URL:** https://lean-fitness-tracker-production.up.railway.app/
- **Platform:** Railway
- **Deployed:** February 14, 2026 (evening)
- **Status:** Live
- **Local Dev:** http://localhost:3000
- **Description:** Smart calorie tracking with voice logging, goal calculator, referral system

### Fitness Tracker Dashboard (Local)
- **URL:** http://10.0.0.18:8080/dashboard/
- **Status:** Running (port 8080)
- **Description:** HTML dashboards for analytics, costs, kanban board

## Staging/Dev Environments
- None currently configured

## Infrastructure
- **Railway Project:** lean-fitness-tracker-production
- **Database:** SQLite (migrating to PostgreSQL recommended for production)
- **Environment Variables:** Managed via Railway dashboard

## Access & Credentials
- Railway login: Via GitHub OAuth
- Admin access: Ross's Railway account

---

*Last updated: 2026-02-15 08:45 CST*
*Always update this file when deploying new services*
