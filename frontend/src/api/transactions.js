/**
 * Generic transactions API module
 * 
 * This module provides a unified interface for both expense and income API operations.
 * Instead of having separate functions for expenses and incomes, we use a generic
 * transactionsApi factory function that creates API methods based on the transaction type.
 * 
 * Usage:
 *   const api = transactionsApi('expense');
 *   const expenses = await api.list();
 *   const created = await api.create({ date: '2025-01-01', amount: 100, ... });
 *   const updated = await api.update(id, { amount: 150 });
 *   await api.remove(id);
 *   await api.bulkRemove([id1, id2, id3]);
 */

// ----------------------------------------------
// Determine API base URL
// ----------------------------------------------
const BASE_URL =
  import.meta.env.VITE_REACT_APP_API_URL ||
  `http://${window.location.hostname}:8000/api/v1`;

/**
 * Generic request helper with error handling
 * Handles both JSON responses and non-JSON responses (like DELETE)
 */
async function request(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  
  // For DELETE requests and other methods that may not return JSON,
  // check content type before parsing
  const contentType = res.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return res.json();
  }
  
  // Return true for successful non-JSON responses (like DELETE)
  return true;
}

/**
 * Generic transactions API factory
 * 
 * Creates a set of API methods for a specific transaction type (expense or income).
 * This eliminates the need for duplicate API functions.
 * 
 * @param {string} type - The transaction type: 'expense' or 'income'
 * @returns {object} API methods: { list, create, update, remove, bulkRemove }
 */
export function transactionsApi(type) {
  if (type !== 'expense' && type !== 'income') {
    throw new Error(`Invalid transaction type: ${type}. Must be 'expense' or 'income'.`);
  }

  return {
    /**
     * Fetch all transactions of this type
     */
    list: () => {
      return request(`${BASE_URL}/${type}`);
    },

    /**
     * Create a new transaction
     * @param {object} data - Transaction data
     */
    create: (data) => {
      return request(`${BASE_URL}/${type}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
    },

    /**
     * Update an existing transaction
     * @param {number|string} id - Transaction ID
     * @param {object} data - Updated transaction data
     */
    update: (id, data) => {
      return request(`${BASE_URL}/${type}/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
    },

    /**
     * Delete a single transaction
     * @param {number|string} id - Transaction ID
     */
    remove: (id) => {
      return request(`${BASE_URL}/${type}/${id}`, {
        method: "DELETE",
      });
    },

    /**
     * Delete multiple transactions at once
     * @param {Array<number|string>} ids - Array of transaction IDs
     */
    bulkRemove: (ids) => {
      return request(`${BASE_URL}/${type}/bulk-delete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ids }),
      });
    },
  };
}
