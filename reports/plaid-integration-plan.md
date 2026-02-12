# Plaid Integration Plan - Personal Finance Dashboard

**Date:** February 12, 2026  
**Purpose:** Setup guide for Sunday's financial dashboard build  
**Target:** Track personal finances, net worth, Florida Fund progress

---

## What is Plaid?

**Plaid = Bank account connectivity API**
- Connects to 12,000+ financial institutions
- Pulls account balances, transactions, identity data
- Secure OAuth authentication (no storing passwords)
- Free tier: Up to 100 connected accounts

**What we'll use it for:**
- Real-time account balances
- Transaction history
- Net worth calculation
- Florida Fund tracking
- Spending categorization

---

## Setup Steps (Before Sunday Build)

### 1. Create Plaid Developer Account ✅ (I'll do this today)
- Go to https://dashboard.plaid.com/signup
- Use: bigmeatyclawd@gmail.com (Jarvis account)
- Get API keys:
  - Client ID
  - Sandbox secret (for testing)
  - Development secret (for real accounts, limited)
  - Production secret (later, requires approval)

### 2. Environment Setup
Start in **Sandbox** (test data), then move to **Development** (real accounts with limits)

**Credentials needed:**
- `PLAID_CLIENT_ID`
- `PLAID_SECRET` (Sandbox initially)
- `PLAID_ENV` (sandbox/development/production)

### 3. Quickstart Clone & Test
```bash
cd ~/clawd
git clone https://github.com/plaid/quickstart.git plaid-quickstart
cd plaid-quickstart
cp .env.example .env
# Add credentials to .env
npm install
./start.sh  # Backend
npm start   # Frontend (separate terminal)
```

Test with Sandbox credentials:
- Username: `user_good`
- Password: `pass_good`
- 2FA code: `1234`

---

## Architecture (Sunday Build)

### Backend (Node.js/Express)
```javascript
// Server endpoints needed:

1. POST /api/create_link_token
   - Generates temporary token for Plaid Link
   - Returns link_token to frontend

2. POST /api/exchange_public_token
   - Exchanges public_token for access_token
   - Stores access_token securely (encrypted DB or 1Password)
   - Associates with Ross's user account

3. GET /api/accounts
   - Fetches account balances
   - Returns account data to frontend

4. GET /api/transactions
   - Fetches recent transactions
   - Returns categorized transaction list

5. GET /api/balance/refresh
   - Triggers manual balance refresh
   - Returns updated balances
```

### Frontend (React or Next.js)
```javascript
// Components needed:

1. PlaidLinkButton
   - Opens Plaid Link modal
   - Handles OAuth flow
   - Sends public_token to backend

2. AccountsList
   - Displays connected accounts
   - Shows current balances
   - Color-coded by account type

3. NetWorthChart
   - Calculates total across all accounts
   - Visualizes trends over time
   - Highlights Florida Fund progress

4. TransactionsList
   - Recent transactions (last 30 days)
   - Categorized spending
   - Search and filter

5. Dashboard
   - Overview: Net worth, Florida Fund progress
   - Quick stats: Monthly spending, savings rate
   - Charts: Spending by category, net worth trend
```

---

## Data Flow

```
1. User clicks "Connect Bank Account"
   ↓
2. Frontend requests link_token from backend
   ↓
3. Backend calls Plaid /link/token/create
   ↓
4. Backend returns link_token to frontend
   ↓
5. Frontend opens Plaid Link modal with link_token
   ↓
6. User authenticates with bank (OAuth)
   ↓
7. Plaid Link returns public_token to frontend
   ↓
8. Frontend sends public_token to backend
   ↓
9. Backend exchanges public_token for access_token
   ↓
10. Backend stores access_token securely
    ↓
11. Backend fetches account data using access_token
    ↓
12. Backend returns account data to frontend
    ↓
13. Frontend displays balances and transactions
```

---

## Database Schema

### Accounts Table
```sql
CREATE TABLE accounts (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  plaid_account_id TEXT NOT NULL,
  plaid_item_id TEXT NOT NULL,
  name TEXT,
  official_name TEXT,
  type TEXT,  -- depository, credit, loan, investment
  subtype TEXT,  -- checking, savings, credit card, etc.
  mask TEXT,  -- Last 4 digits
  balance_current REAL,
  balance_available REAL,
  currency_code TEXT DEFAULT 'USD',
  last_synced TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
  id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL,
  plaid_transaction_id TEXT NOT NULL,
  amount REAL,
  date TEXT,
  name TEXT,
  merchant_name TEXT,
  category_primary TEXT,
  category_detailed TEXT,
  pending BOOLEAN,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (account_id) REFERENCES accounts(id)
);
```

### Items Table (Plaid connections)
```sql
CREATE TABLE plaid_items (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  plaid_item_id TEXT NOT NULL,
  access_token TEXT NOT NULL,  -- ENCRYPTED
  institution_id TEXT,
  institution_name TEXT,
  status TEXT DEFAULT 'active',
  last_synced TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Security Considerations

### Access Token Storage
**NEVER store access_tokens in plain text**

**Options:**
1. Encrypt in database (recommended for MVP)
2. Store in 1Password API (most secure)
3. Use environment variables (only for single-user app)

**Implementation (encryption):**
```javascript
const crypto = require('crypto');

const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY; // 32-byte key
const IV_LENGTH = 16;

function encrypt(text) {
  const iv = crypto.randomBytes(IV_LENGTH);
  const cipher = crypto.createCipheriv('aes-256-cbc', Buffer.from(ENCRYPTION_KEY), iv);
  let encrypted = cipher.update(text);
  encrypted = Buffer.concat([encrypted, cipher.final()]);
  return iv.toString('hex') + ':' + encrypted.toString('hex');
}

function decrypt(text) {
  const parts = text.split(':');
  const iv = Buffer.from(parts.shift(), 'hex');
  const encryptedText = Buffer.from(parts.join(':'), 'hex');
  const decipher = crypto.createDecipheriv('aes-256-cbc', Buffer.from(ENCRYPTION_KEY), iv);
  let decrypted = decipher.update(encryptedText);
  decrypted = Buffer.concat([decrypted, decipher.final()]);
  return decrypted.toString();
}
```

### Webhook Security
Plaid sends webhooks when account data changes. Verify webhook signatures to prevent spoofing.

---

## Features to Build (Sunday)

### Phase 1: Core Connection (1 hour)
- Plaid Link integration
- OAuth flow
- Access token storage (encrypted)
- Basic account list display

### Phase 2: Balance Display (1 hour)
- Fetch account balances
- Display current and available balances
- Calculate net worth (sum of all accounts)
- Auto-refresh on page load

### Phase 3: Florida Fund Tracking (30 min)
- Designate specific account(s) as "Florida Fund"
- Track progress toward $50K goal
- Progress bar visualization
- "Days until goal" calculation

### Phase 4: Transaction History (1 hour)
- Fetch recent transactions (30 days)
- Display in table format
- Basic categorization (Plaid auto-categorizes)
- Search and filter

### Phase 5: Dashboard View (30 min)
- Net worth overview card
- Florida Fund progress card
- Monthly spending summary
- Quick stats: Savings rate, top spending categories

---

## Environment Selection Strategy

### Sandbox (Testing - Start here)
- **Use:** Initial development and testing
- **Credentials:** Test data (user_good/pass_good)
- **Limits:** Unlimited, fake data
- **Cost:** Free

### Development (Real accounts - Move here after testing)
- **Use:** Connect Ross's real accounts
- **Credentials:** Real bank login
- **Limits:** 100 connected accounts
- **Cost:** Free

### Production (Live app - Later, requires approval)
- **Use:** If building for others/public launch
- **Requires:** Plaid approval process
- **Cost:** Pay per connected account

**For Sunday:** Start Sandbox, move to Development once working.

---

## Accounts to Connect (Ross's Personal)

Based on profile:
1. **Primary Checking** (daily expenses)
2. **Savings Account(s)** (emergency fund, Florida Fund)
3. **Investment Accounts** (401k, crypto might not be supported)
4. **Credit Cards** (spending tracking)

**Note:** Crypto (BTC, XRP) likely requires manual entry - Plaid doesn't support most crypto exchanges.

---

## Florida Fund Calculation

**Goal:** $50,000  
**Current:** TBD (will pull from connected accounts)

**Formula:**
```javascript
const floridaFundAccounts = accounts.filter(a => a.name.includes('Florida') || a.subtype === 'savings');
const floridaFundBalance = floridaFundAccounts.reduce((sum, a) => sum + a.balance_current, 0);
const floridaFundProgress = (floridaFundBalance / 50000) * 100;
const remainingToGoal = 50000 - floridaFundBalance;
```

---

## Implementation Checklist (Sunday)

### Pre-build Setup
- [ ] Plaid developer account created
- [ ] API keys obtained (Sandbox)
- [ ] Quickstart tested locally
- [ ] Database schema designed
- [ ] Encryption key generated

### Build Steps
- [ ] Clone Quickstart or build from scratch
- [ ] Backend: /create_link_token endpoint
- [ ] Backend: /exchange_public_token endpoint
- [ ] Backend: /accounts endpoint
- [ ] Backend: /transactions endpoint
- [ ] Frontend: PlaidLinkButton component
- [ ] Frontend: AccountsList component
- [ ] Frontend: NetWorthCard component
- [ ] Frontend: FloridaFundProgress component
- [ ] Frontend: TransactionsList component
- [ ] Test in Sandbox environment
- [ ] Switch to Development environment
- [ ] Connect Ross's real accounts
- [ ] Verify data accuracy
- [ ] Deploy (localhost for now, Vercel later)

### Security Checklist
- [ ] Access tokens encrypted
- [ ] Environment variables not committed to git
- [ ] HTTPS enforced (localhost exempt)
- [ ] Webhook signature verification
- [ ] Rate limiting on API endpoints

---

## Open Questions for Ross (Sunday)

1. **Which accounts to connect?**
   - All checking/savings?
   - Credit cards included?
   - Investment accounts?

2. **Florida Fund definition:**
   - Specific account(s)?
   - Or sum of all savings accounts?

3. **Update frequency:**
   - Real-time (fetch on page load)?
   - Manual refresh button?
   - Daily auto-refresh?

4. **Transaction lookback:**
   - 30 days?
   - 90 days?
   - Full year?

5. **Categorization:**
   - Use Plaid's auto-categories?
   - Custom category mapping?
   - Manual override option?

---

## Tech Stack (Sunday Build)

**Backend:**
- Node.js + Express (simple, fast)
- SQLite (local database, easy setup)
- Plaid Node SDK

**Frontend:**
- React (or Next.js for SSR)
- Tailwind CSS (fast styling)
- Chart.js or Recharts (visualizations)

**Deployment:**
- Localhost initially
- Vercel (later, for public access)

**Alternative (Faster MVP):**
- Use Plaid Quickstart as base
- Customize frontend for Ross's needs
- Add Florida Fund tracking on top

---

## Cost Estimates

**Plaid Pricing:**
- Development environment: Free (100 accounts)
- Production: Pay only if launching publicly

**Our use case:** Free tier is sufficient (single user, <100 accounts)

---

## Timeline

**Today (While Ross is at work):**
- [x] Create Plaid developer account → **DONE**
- [ ] Test Quickstart locally
- [ ] Document setup process

**Sunday PM (Ross + Jarvis):**
- [ ] Clone/customize Quickstart (30 min)
- [ ] Build Florida Fund tracking (30 min)
- [ ] Customize dashboard layout (30 min)
- [ ] Connect Ross's accounts (15 min)
- [ ] Test and verify data (15 min)

**Total Sunday build time:** ~2 hours

---

**Status:** Research complete, ready for Sunday implementation  
**Next:** Test local model quality
