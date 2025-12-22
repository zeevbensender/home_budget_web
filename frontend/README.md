# Home Budget Web — Frontend

## Overview

The frontend is a React application built with Vite that manages expenses and incomes. It provides a unified interface for CRUD operations on both transaction types using generic, reusable patterns.

## Technology Stack

- **React 19** - UI framework
- **Vite** - Build tool and dev server
- **Bootstrap 5** - CSS framework
- **TanStack Table** - Table component library
- **Vitest** - Testing framework

## Project Structure

```
src/
├── api/                    # API layer
│   └── transactions.js     # Generic transactions API factory
├── components/             # React components
│   ├── ui/                # Reusable UI components
│   │   └── Toast.jsx      # Toast notification component
│   └── TableBudget/       # Table-related components
│       ├── TableBudget.jsx   # Main table component
│       ├── AddRow.jsx        # Inline add row component
│       ├── columns.jsx       # Column definitions
│       └── ...
├── hooks/                  # Custom React hooks
│   ├── useTransactions.js  # Generic CRUD hook for transactions
│   ├── useToast.js         # Toast notification hook
│   └── useIsMobile.js      # Mobile detection hook
├── utils/                  # Utility functions
│   └── formatNumber.js     # Number formatting helper
├── tests/                  # Test files
├── App.jsx                 # Main application component
├── api.js                  # Legacy API exports (backward compatible)
└── main.jsx               # Application entry point
```

## Key Design Patterns

### 1. Generic Transaction Handling

Instead of duplicating code for expenses and incomes, we use a generic pattern:

**API Layer** (`src/api/transactions.js`):
```javascript
const api = transactionsApi('expense'); // or 'income'
await api.list();
await api.create(data);
await api.update(id, data);
await api.remove(id);
await api.bulkRemove(ids);
```

**Data Hook** (`src/hooks/useTransactions.js`):
```javascript
const expenses = useTransactions('expense');
const incomes = useTransactions('income');

// Access data
expenses.data      // array of transactions
expenses.loading   // boolean
expenses.error     // error object or null

// Perform operations
await expenses.add(data);
await expenses.update(id, data);
await expenses.remove(id);
await expenses.bulkRemove(ids);
await expenses.refresh();
```

### 2. Centralized UI Feedback

Toast notifications are managed through a custom hook:

```javascript
const toast = useToast();

toast.show('Transaction saved!', 'success');
toast.show('Error occurred', 'error');

// Render
<Toast message={toast.message} type={toast.type} />
```

### 3. Responsive Design

The app adapts to mobile and desktop views:
- **Desktop**: Inline add/edit in tables
- **Mobile**: Modal-based add/edit with floating action button

Detection is handled by `useIsMobile()` hook.

## Main Components

### App.jsx

Main application component that:
- Manages expenses and incomes using `useTransactions` hook
- Handles mobile modal state for add/edit operations
- Provides unified handlers for both transaction types
- Renders separate tables for expenses and incomes

**Key responsibilities**:
- Data orchestration (uses hooks, doesn't manage raw state)
- Mobile/desktop interaction routing
- Toast notification management

### TableBudget.jsx

Generic table component that works for both expenses and incomes:
- Displays transactions in a responsive table
- Supports inline add (desktop)
- Single and bulk delete operations
- Select mode for bulk operations
- Mobile tap-to-edit

**Props**:
- `data` - Array of transactions
- `type` - 'expense' or 'income'
- `onCreateLocal` - Handler for creating new transaction
- `onLocalDelete` - Handler for single delete
- `onLocalDeleteBulk` - Handler for bulk delete
- `onMobileEdit` - Handler for mobile edit tap

### TransactionModal.jsx

Mobile modal for adding/editing transactions:
- Handles both add and edit modes
- Dynamic fields based on transaction type
- Form validation
- Delegates submission to parent component

## Data Lifecycle

### 1. Initial Load

```
App mounts
  ↓
useTransactions('expense') & useTransactions('income') hooks initialize
  ↓
Hooks automatically fetch data via transactionsApi(type).list()
  ↓
Data stored in hook state (expenses.data, incomes.data)
  ↓
Data passed to TableBudget components
```

### 2. Create Transaction

```
User clicks "Add" (desktop) or FAB (mobile)
  ↓
Form displayed (inline row or modal)
  ↓
User submits form
  ↓
Parent calls transactionHook.add(data)
  ↓
Hook calls transactionsApi(type).create(data)
  ↓
API returns created transaction
  ↓
Hook updates local state optimistically
  ↓
Table re-renders with new data
  ↓
Toast notification shown
```

### 3. Update Transaction

```
User clicks edit (desktop inline or mobile tap)
  ↓
Form pre-filled with existing data
  ↓
User submits changes
  ↓
Parent calls transactionHook.update(id, data)
  ↓
Hook calls transactionsApi(type).update(id, data)
  ↓
API returns updated transaction
  ↓
Hook updates local state (replaces old item)
  ↓
Table re-renders with updated data
  ↓
Toast notification shown
```

### 4. Delete Transaction

```
User clicks delete button
  ↓
TableBudget calls api.remove(id) directly
  ↓
On success, calls onLocalDelete(id)
  ↓
Parent's transactionHook.remove(id) updates state
  ↓
Table re-renders without deleted item
```

## Error Handling

Errors are handled at multiple levels:

1. **API Layer**: Throws errors with HTTP status and message
2. **Hook Layer**: Catches errors, logs them, and sets error state
3. **Component Layer**: Catches errors and shows toast notifications

Example:
```javascript
try {
  await expenses.add(data);
  toast.show('Success!', 'success');
} catch (err) {
  console.error('Error:', err);
  toast.show('Failed to save', 'error');
}
```

## Development

```bash
npm install     # Install dependencies
npm run dev     # Start dev server
npm run build   # Build for production
npm run lint    # Lint code
npm test        # Run tests
```

## Tests

The frontend uses **Vitest** for minimal logic tests.

### Test Types

- **Unit tests**  
  Pure JavaScript logic (no DOM), located in: `src/tests/`

- **E2E smoke tests**  
  Currently **skipped by default**.  
  Enable manually by setting:
  ```
  BACKEND_URL=http://localhost:8000 npm test
  ```

### Notes
- No component rendering tests during Variant A
- Avoid introducing UI-level coupling in tests
- Keep diffs minimal

## Adding New Features

### Adding a new transaction field:

1. Update backend API to accept new field
2. No changes needed in `transactionsApi` (it's generic)
3. Update `TransactionModal.jsx` to include new field in form
4. Update column definitions in `src/components/TableBudget/columns.jsx`

### Adding a new transaction type:

1. Update backend to support new type
2. Add new hook instance: `const transfers = useTransactions('transfer')`
3. Add new table in `App.jsx`
4. No other changes needed (all code is generic)

## Best Practices

1. **Use hooks for data management**: Don't manage transaction state directly in components
2. **Leverage the generic API**: Use `transactionsApi(type)` instead of creating new functions
3. **Centralize error handling**: Always show toast notifications for user feedback
4. **Keep components focused**: Separate concerns (data, UI, interaction)
5. **Add comments**: Explain complex logic, especially for backend developers new to React

## Common Pitfalls

1. **Don't bypass hooks**: Always use the exposed hook methods (add, update, remove) rather than calling API directly and managing state manually
2. **Don't duplicate logic**: If you find yourself writing similar code for expenses and incomes, use the generic patterns
3. **Remember mobile**: Test both desktop and mobile views when making UI changes

## Resources

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [TanStack Table](https://tanstack.com/table)
- [Bootstrap 5](https://getbootstrap.com)
