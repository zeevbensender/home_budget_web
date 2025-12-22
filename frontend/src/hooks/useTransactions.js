/**
 * useTransactions hook
 * 
 * Generic hook for managing transaction data (expenses or incomes).
 * This hook eliminates duplicate logic for CRUD operations by providing
 * a unified interface for both transaction types.
 * 
 * Features:
 * - Automatic data fetching on mount
 * - Optimistic local state updates
 * - Loading and error state management
 * - Unified CRUD operations (add, update, remove)
 * 
 * Usage:
 *   const expenses = useTransactions('expense');
 *   const incomes = useTransactions('income');
 * 
 *   // Access data
 *   expenses.data // array of transactions
 *   expenses.loading // boolean
 *   expenses.error // error object or null
 * 
 *   // Perform operations
 *   await expenses.add({ date: '2025-01-01', amount: 100, ... });
 *   await expenses.update(id, { amount: 150 });
 *   await expenses.remove(id);
 *   await expenses.bulkRemove([id1, id2]);
 *   await expenses.refresh(); // re-fetch from server
 */

import { useEffect, useState, useCallback } from 'react';
import { transactionsApi } from '../api/transactions.js';

/**
 * Custom hook for managing transactions (expenses or incomes)
 * 
 * @param {string} type - Transaction type: 'expense' or 'income'
 * @returns {object} Transaction state and operations
 */
export function useTransactions(type) {
  const api = transactionsApi(type);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Refresh data from the server
   */
  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const items = await api.list();
      setData(items);
      setError(null);
    } catch (e) {
      setError(e);
      console.error(`Error fetching ${type}s:`, e);
    } finally {
      setLoading(false);
    }
  }, [api, type]);

  // Fetch data on mount
  useEffect(() => {
    refresh();
  }, [refresh]);

  /**
   * Add a new transaction
   * Updates local state optimistically after successful API call
   */
  const add = useCallback(async (payload) => {
    try {
      const created = await api.create(payload);
      setData(prev => [created, ...prev]);
      return created;
    } catch (e) {
      console.error(`Error creating ${type}:`, e);
      throw e;
    }
  }, [api, type]);

  /**
   * Update an existing transaction
   * Updates local state optimistically after successful API call
   */
  const update = useCallback(async (id, payload) => {
    try {
      const updated = await api.update(id, payload);
      setData(prev => prev.map(i => i.id === id ? updated : i));
      return updated;
    } catch (e) {
      console.error(`Error updating ${type}:`, e);
      throw e;
    }
  }, [api, type]);

  /**
   * Remove a single transaction
   * Updates local state optimistically after successful API call
   */
  const remove = useCallback(async (id) => {
    try {
      await api.remove(id);
      setData(prev => prev.filter(i => i.id !== id));
    } catch (e) {
      console.error(`Error deleting ${type}:`, e);
      throw e;
    }
  }, [api, type]);

  /**
   * Remove multiple transactions at once
   * Updates local state optimistically after successful API call
   */
  const bulkRemove = useCallback(async (ids) => {
    try {
      await api.bulkRemove(ids);
      setData(prev => prev.filter(i => !ids.includes(i.id)));
    } catch (e) {
      console.error(`Error bulk deleting ${type}s:`, e);
      throw e;
    }
  }, [api, type]);

  return {
    data,
    loading,
    error,
    add,
    update,
    remove,
    bulkRemove,
    refresh,
  };
}
