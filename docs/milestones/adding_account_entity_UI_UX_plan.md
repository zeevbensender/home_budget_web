# UI/UX Plan: Managing Bank Accounts, Credit Cards, and Cash (Manual Entry)



## Entity Model (UI-Facing)
- **Shared fields (single table):** nickname, institution (free text), type flag, currency (default ₪), 
 - **Type-specific, progressive disclosure:**
  - **Credit card:** credit limit, statement day, payment due date.
  - **Bank account:** opening balance, type toggle (current/savings), overdraft limit (optional).
  - **Cash:** opening balance only.
- **Onboarding:** Empty state with one primary CTA: **“Add account.”**  - 
- Fields appear/vanish based on selected type to keep the mobile form short.

## Navigation & Layout
- **Home:** current landing page with ability to add / edit expenses / incomes. Account field autocomplete or ability to create a new account
- **Home / Accounts list:** stacked cards or rows with balance, type pill, masked trailing digits when provided. Quick actions: Edit, Update balance, Archive; reorder with drag handle (desktop) or long-press (mobile).
- **Add / Edit surface:** full-height modal drawer on mobile; centered modal on larger screens. Primary actions pinned to bottom (Save, Cancel) for reachability.
- **Empty state:** illustration placeholder + concise copy + "Add account" CTA; secondary link to static help ("How to organize accounts").

## Core Flows (Borrowed Patterns)
1. **Add account/card** — Monzo/Revolut simplicity
   - Step 1: Choose type via pill buttons.
   - Step 2: Core fields (nickname, institution, optional masked number, currency defaulted to ₪, opening/starting balance).
   - Step 3: Type-specific fields expand inline; optional extras behind **“Add more details.”**
   - Validation: required nickname, type, and either opening balance (bank/cash) or credit limit (cards); date pickers for statement/due dates; inline errors.
2. **Edit details**
   - Open from card or row; same modal with data prefilled.
   - Changing type allowed only if conflicting type-specific fields are cleared; prompt before switching.
3. **List management**
   - Group by **type** with sticky headers (Bank accounts, Credit cards, Cash) for scannability.
   - Custom ordering; archived/closed items collapsed under **Archived**.

## Visual Style References
- **Account cards:** clean tiles with type badge (color-coded), bold balance, masked trailing digits, and secondary metadata (institution + last updated).
- **Credit-card specifics (Apple Card influence):** space for utilization ring and statement-cycle text (e.g., “Next due in 5 days”) when enabled later.
- **Buttons/CTAs:** primary filled for Save/Add; ghost secondary for Cancel/Archive.

## Accessibility & Safety
- Touch targets ≥ 44px, clear focus outlines, labels always visible, helper text for optional fields.
- Inline error messaging under fields; toast confirmation after save.

## Minimal Checkpoints for This Milestone
- Empty state with Add CTA; responsive list cards; Add/Edit modal with progressive disclosure.
- Manual balance update action per account.
- Masking behavior and basic validation in place.

## Migration
- One time migration process from incomes and expenses tables (account column) to the new table(s)
