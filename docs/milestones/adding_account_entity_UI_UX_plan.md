# UI/UX Plan: Managing Bank Accounts, Credit Cards, and Cash (Manual Entry)



## Entity Model (UI-Facing)
- **Shared fields (single table):** nickname, institution (free text), type flag, currency (default ₪), opening/starting balance, statement day (optional), payment due date (optional), notes.
- **Type-specific, progressive disclosure:**
  - **Credit card:** credit limit, statement day, payment due date, minimum payment (optional), autopay account selector (free text for now).
  - **Bank account:** opening balance, type toggle (current/savings), overdraft limit (optional).
  - **Cash:** opening balance only.
- **Onboarding:** Empty state with one primary CTA: **“Add account.”**  - 
- Fields appear/vanish based on selected type to keep the mobile form short.

## Navigation & Layout
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
4. **Balance updates (manual)**
   - Quick **Update balance** opens numeric keypad; enforces currency format; optional reconciliation note.
5. **Alerts (future-ready placeholder)**
   - Non-blocking banners on cards for upcoming due dates or high utilization; hidden until feature is enabled.

## Data Entry Patterns (Manual-First)
- Currency defaults to ₪; if multi-currency is added later, reuse the same control (dropdown disabled for now to avoid confusion).
- Masked number input pattern: `•••• 1234` with tap-to-reveal for the session; auto-hide on blur.
- Institution: simple free-text field, autocomplete-ready for a static suggestions list later.

## Visual Style References
- **Account cards:** clean tiles with type badge (color-coded), bold balance, masked trailing digits, and secondary metadata (institution + last updated).
- **Credit-card specifics (Apple Card influence):** space for utilization ring and statement-cycle text (e.g., “Next due in 5 days”) when enabled later.
- **Buttons/CTAs:** primary filled for Save/Add; ghost secondary for Cancel/Archive.

## Accessibility & Safety
- Touch targets ≥ 44px, clear focus outlines, labels always visible, helper text for optional fields.
- Inline error messaging under fields; toast confirmation after save.

## Migration & Future-Proofing (UI Only)
- Temporary banner: **“We now support account types—edit entries to set their type.”** Opens the Edit modal for existing rows.
- Single-table layout retained with visible type chips; chips should be filter/search ready.
- Reserve space in layouts for future: institution logos, connection status, alerts, budgeting hooks (net worth, utilization tags).

## Minimal Checkpoints for This Milestone
- Empty state with Add CTA; responsive list cards; Add/Edit modal with progressive disclosure.
- Manual balance update action per account.
- Masking behavior and basic validation in place.
