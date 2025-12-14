# Milestone: Account Entity Implementation

## Overview
This document outlines the plan to transform the account field from a simple text field in expenses/incomes into a dedicated entity with full CRUD operations, enabling better account management and future features like balance tracking and reconciliation.

## Current State (As of December 2024)

### ✅ Completed
- PostgreSQL migration complete (Phase 5 - Full Database Mode)
- Expenses and incomes tables have `account` field (String, 100 chars)
- Basic account name entry in expense/income forms (free text)
- No validation or normalization of account names

### ❌ Not Implemented
- No separate Account entity/table
- No account list management UI
- No account balance tracking
- No account type differentiation (bank/credit card/cash)
- No account metadata (institution, currency settings, etc.)

---

## Migration Strategy

### Phase 1: Backend - Account Entity Foundation
**Goal:** Create the core Account entity and CRUD operations

#### 1.1 Database Schema
Create accounts table with:
- `id` (Primary Key, Integer, Auto-increment)
- `nickname` (String, 100 chars, required, unique)
- `institution` (String, 255 chars, optional)
- `account_type` (Enum: 'bank_account', 'credit_card', 'cash', required)
- `currency` (String, 10 chars, default '₪')
  - **Note:** Currently hardcoded to Israeli Shekel for MVP. Consider using ISO currency codes (e.g., 'ILS') for better internationalization in future iterations.
- `is_archived` (Boolean, default false)
- `created_at` (Timestamp)
- `updated_at` (Timestamp)

**Best Practice:** Use Alembic migration following existing conventions:
```bash
cd backend
alembic revision -m "add_accounts_table"
```

#### 1.2 Type-Specific Fields (JSONB)
Store type-specific data in a flexible JSONB column:
- `metadata` (JSONB, nullable) - stores type-specific fields:
  - **Bank Account:** 
    - `opening_balance` (Decimal/String)
    - `account_subtype` (String: 'current' or 'savings')
    - `overdraft_limit` (Decimal/String, optional)
  - **Credit Card:** 
    - `credit_limit` (Decimal/String, required)
    - `statement_day` (Integer, 1-31)
    - `payment_due_day` (Integer, 1-31)
  - **Cash:** 
    - `opening_balance` (Decimal/String)

**Best Practice:** JSONB allows schema flexibility without multiple tables while maintaining queryability.

#### 1.3 Repository Pattern
Create `AccountRepository` following existing pattern:
- Inherit from `BaseRepository`
- Implement account-specific queries:
  - `get_by_nickname()`
  - `get_active_accounts()` (excludes archived)
  - `get_by_type(account_type)`
  - `archive_account(id)`

**File:** `backend/app/repositories/account_repository.py`

#### 1.4 Service Layer
Create `AccountService` with business logic:
- Validate unique nicknames
- Handle metadata validation per account type
- Prevent deletion of accounts with transactions (soft delete via archive)

**File:** `backend/app/services/account_service.py`

#### 1.5 API Endpoints
Create `AccountRouter` with RESTful endpoints:
- `GET /api/v1/accounts` - List accounts (with optional type filter)
- `GET /api/v1/accounts/{id}` - Get account details
- `POST /api/v1/accounts` - Create account
- `PATCH /api/v1/accounts/{id}` - Update account
- `DELETE /api/v1/accounts/{id}` - Archive account (soft delete)

**File:** `backend/app/routers/account_router.py`

#### 1.6 Testing
- Unit tests for repository (SQLite)
- Integration tests for API endpoints (PostgreSQL)
- Test unique constraint violations
- Test archival prevents deletion with existing transactions
- Achieve 85%+ coverage

---

### Phase 2: Data Migration & Foreign Keys
**Goal:** Migrate existing account strings to Account entities

#### 2.1 Extract Unique Accounts
Create migration script to:
1. Extract all unique account names from expenses and incomes
2. Create Account records (type='bank_account' as default)
3. Preserve data integrity

**Best Practice:** Make migration idempotent and include rollback script.

#### 2.2 Add Foreign Key Relationships
- Add `account_id` (FK to accounts.id, nullable initially)
- Populate `account_id` based on account name matching
- Update services to use `account_id` for new records
- Maintain `account` (string) temporarily for rollback safety

**Phased Approach:**
1. Add `account_id` column (nullable)
2. Backfill data
3. Switch application to use `account_id`
4. Mark `account` string column deprecated (remove in future milestone)

#### 2.3 Data Validation
- Verify all expenses/incomes have matching account_id
- Handle edge cases (account names with variations)
- Create manual review report for unmapped records

---

### Phase 3: Frontend - Account Management UI
**Goal:** Build user interface for managing accounts

#### 3.1 Account List View
**Navigation:** Add "Accounts" link to main navigation

**Layout:**
- Grouped by type (Bank Accounts, Credit Cards, Cash)
- Card-based layout with visual hierarchy:
  - Account nickname (prominent)
  - Type badge (color-coded)
  - Institution name (secondary)
  - Balance placeholder (future)
  - Last updated timestamp
  
**Actions per card:**
- Edit (pencil icon)
- Archive (trash icon with confirmation)
- Drag to reorder (desktop) / long-press (mobile)

**Empty State:**
- Illustration placeholder
- "Add your first account" CTA
- Link to help documentation

**Files:**
- `frontend/src/components/Accounts/AccountList.jsx`
- `frontend/src/components/Accounts/AccountCard.jsx`

#### 3.2 Add/Edit Account Modal
**Progressive Disclosure Pattern (Monzo/Revolut style):**

**Step 1:** Choose account type (pill buttons)
- Bank Account
- Credit Card  
- Cash

**Step 2:** Core fields (always visible)
- Nickname* (required, auto-focus)
- Institution (optional)
- Currency (default ₪)

**Step 3:** Type-specific fields (expand based on selection)
- **Bank Account:**
  - Opening balance
  - Account type (Current/Savings toggle)
  - Overdraft limit (optional, collapsed under "More details")
  
- **Credit Card:**
  - Credit limit*
  - Statement day (date picker)
  - Payment due day (date picker)
  
- **Cash:**
  - Opening balance

**Validation:**
- Real-time validation with inline errors
- Required field indicators
- Unique nickname check (debounced API call)
- Numeric validation for amounts/limits
- Date validation for statement/due dates

**Accessibility:**
- Touch targets ≥ 44px
- Clear focus outlines
- Labels always visible (no placeholder-only labels)
- Screen reader announcements for errors
- Keyboard navigation support

**Files:**
- `frontend/src/components/Accounts/AccountModal.jsx`
- `frontend/src/components/Accounts/AccountTypeSelector.jsx`

#### 3.3 Integration with Transaction Forms
**Update Transaction Modal:**
- Replace free-text account input with dropdown
- Dropdown populated from active accounts
- Option to "Add new account" inline (quick add modal)
- Autocomplete for fast account selection
- Show account type icon next to account name

**Files to modify:**
- `frontend/src/components/TransactionModal.jsx`
- `frontend/src/components/TableBudget/AddRow.jsx`

#### 3.4 API Integration
Create account service layer:
- `frontend/src/services/accountService.js`
- CRUD operations matching backend API
- Error handling and loading states
- Optimistic updates for better UX

---

### Phase 4: Visual Polish & UX Refinements
**Goal:** Apply consistent design language

#### 4.1 Visual Design System
**Color-coded type badges:**
- Bank Account: Blue (#2563EB)
- Credit Card: Purple (#7C3AED)
- Cash: Green (#059669)

**Account Cards:**
- Clean tile design with subtle shadow
- Bold account nickname (font-size: 18px)
- Type badge (pill shape, 8px padding)
- Metadata in muted color (#6B7280)
- Hover state for interactive feedback

**Responsive Design:**
- Mobile: Full-width cards, stacked vertically
- Tablet: 2-column grid
- Desktop: 3-column grid with drag-and-drop reordering

#### 4.2 Animation & Feedback
- Smooth transitions for modal open/close
- Toast notifications:
  - "Account created successfully"
  - "Account updated"
  - "Account archived"
- Loading states with skeleton screens
- Optimistic updates for instant feedback

#### 4.3 Credit Card Specific Features (Future Enhancement)
- Utilization ring (visual indicator of credit usage)
- Statement cycle countdown ("Next due in 5 days")
- Payment reminders (notification system)

**Note:** These are marked as future enhancements, not required for initial milestone.

---

## Testing & Quality Assurance

### Backend Testing
- [ ] Repository unit tests (SQLite, 100% coverage target)
- [ ] Service layer business logic tests
- [ ] API endpoint integration tests (PostgreSQL)
- [ ] Migration script tests (dry-run validation)
- [ ] Edge case handling (duplicate nicknames, orphaned accounts)

### Frontend Testing
- [ ] Component unit tests (Vitest/React Testing Library)
- [ ] Integration tests for account CRUD flows
- [ ] Form validation tests
- [ ] Accessibility tests (axe-core)
- [ ] Responsive design tests (mobile/tablet/desktop)

### Manual QA Checklist
- [ ] Create account of each type
- [ ] Edit account and verify persistence
- [ ] Archive account and verify it's hidden from active list
- [ ] Add expense/income with new account dropdown
- [ ] Verify unique nickname validation
- [ ] Test responsive layouts on multiple devices
- [ ] Screen reader navigation test
- [ ] Keyboard-only navigation test

---

## Rollout & Safety

### Feature Flag Approach
Use feature flags for safe rollout:
- `FF_ENABLE_ACCOUNT_ENTITY` - Master flag for account features
- `FF_ACCOUNT_READONLY_MODE` - Display-only mode during testing

### Rollout Phases
1. **Phase A:** Backend deployed, feature flag OFF (no visible changes)
2. **Phase B:** Enable for internal testing (team members only)
3. **Phase C:** Enable for beta users (monitor for issues)
4. **Phase D:** Full rollout to all users

### Rollback Plan
If issues arise:
1. Disable feature flag immediately
2. Application falls back to string-based account field
3. No data loss (both `account` and `account_id` maintained)
4. Investigate and fix issues before re-enabling

---

## Success Metrics

### Technical Metrics
- Account API response time < 200ms (p95)
- Zero data loss during migration
- 85%+ test coverage maintained
- No increase in error rates after rollout

### User Experience Metrics
- Account creation completion rate > 90%
- Form validation prevents 95%+ of invalid submissions
- Mobile usability score > 90 (Lighthouse)
- Accessibility score > 95 (Lighthouse)

### Business Metrics
- % of users creating at least one account: Track adoption
- Average accounts per user: Understand usage patterns
- % reduction in duplicate account names: Measure data quality improvement

---

## Future Enhancements (Post-MVP)

### Account Balance Tracking
- Auto-calculate balance from transactions
- Manual balance adjustment with audit log
- Balance history visualization
- Reconciliation workflow

### Account Insights
- Spending by account
- Account utilization trends (credit cards)
- Multi-account overview dashboard

### Import/Export
- CSV/OFX import for transaction history
- Bank connection via Plaid/similar (long-term)

### Multi-Currency Support
- Enhanced currency handling per account
- Exchange rate tracking
- Multi-currency reporting

---

## References & Best Practices

### Design Inspiration
- **Monzo/Revolut:** Simple, progressive disclosure in forms
- **Apple Card:** Clean card design, utilization visualization
- **YNAB:** Account categorization and organization

### Technical Standards
- Follow repository pattern (see `backend/app/repositories/base_repository.py`)
- Use Alembic for migrations (see `backend/migrations/`)
- Follow existing API patterns (see `backend/app/routers/`)
- Maintain test coverage standards (85%+ target)
- Follow React component structure (see `frontend/src/components/`)

### Database Guidelines
- Use Alembic migrations for all schema changes
- Include both upgrade and downgrade paths
- Follow naming conventions: `snake_case` for columns
- Document complex queries
- Use indexes for frequently queried fields

### API Guidelines
- RESTful design principles
- Consistent error responses
- Input validation with Pydantic models
- OpenAPI documentation auto-generation
- Version endpoints (`/api/v1/`)

---

## Timeline Estimate

| Phase                       | Estimated Effort | Dependencies       |
|-----------------------------|------------------|--------------------|
| Phase 1: Backend Foundation | 2-3 days         | None               |
| Phase 2: Data Migration     | 1-2 days         | Phase 1 complete   |
| Phase 3: Frontend UI        | 3-4 days         | Phase 1 complete   |
| Phase 4: Visual Polish      | 1-2 days         | Phase 3 complete   |
| Testing & QA                | 1-2 days         | All phases         |
| Total                       | 8-13 days        |                    |

**Note:** Timeline assumes one developer working full-time. Adjust based on team capacity.

---

## Approval & Sign-off

- [ ] Technical design reviewed and approved
- [ ] UI/UX mockups reviewed and approved
- [ ] Migration strategy validated
- [ ] Testing plan approved
- [ ] Rollout plan approved

---

**Document Version:** 2.0  
**Last Updated:** December 2024  
**Status:** Ready for Implementation
