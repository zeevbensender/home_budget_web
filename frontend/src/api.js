/**
 * FRONTEND/src/api.js
 * 
 * This file maintains backward compatibility for existing code while
 * delegating to the new generic transactions API.
 * 
 * The new recommended approach is to use the generic transactionsApi directly:
 *   import { transactionsApi } from './api/transactions.js';
 *   const api = transactionsApi('expense');
 *   await api.list();
 */

import { transactionsApi } from './api/transactions.js';

// Create API instances for each transaction type
const expenseApi = transactionsApi('expense');
const incomeApi = transactionsApi('income');

// Export the generic API for direct use
export { transactionsApi };

// ----------------------------------------------
// EXPENSES (legacy compatibility)
// ----------------------------------------------

export function getExpenses() {
  return expenseApi.list();
}

export function createExpense(data) {
  return expenseApi.create(data);
}

export function updateExpense(id, data) {
  return expenseApi.update(id, data);
}

export function deleteExpense(id) {
  return expenseApi.remove(id);
}

export function bulkDeleteExpenses(ids) {
  return expenseApi.bulkRemove(ids);
}

// ----------------------------------------------
// INCOME (legacy compatibility)
// ----------------------------------------------

export function getIncomes() {
  return incomeApi.list();
}

export function createIncome(data) {
  return incomeApi.create(data);
}

export function updateIncome(id, data) {
  return incomeApi.update(id, data);
}

export function deleteIncome(id) {
  return incomeApi.remove(id);
}

export function bulkDeleteIncomes(ids) {
  return incomeApi.bulkRemove(ids);
}
