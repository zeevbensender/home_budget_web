/**
 * useToast hook
 * 
 * Provides a simple interface for showing temporary toast messages.
 * This hook manages toast state and auto-dismisses messages after a timeout.
 * 
 * Usage:
 *   const toast = useToast();
 * 
 *   // Show a success message
 *   toast.show('Transaction saved!', 'success');
 * 
 *   // Show an error message
 *   toast.show('Failed to save', 'error');
 * 
 *   // Access current toast state
 *   toast.message // current message text or null
 *   toast.type // 'success', 'error', or 'info'
 */

import { useState, useCallback } from 'react';

/**
 * Custom hook for managing toast notifications
 * 
 * @param {number} defaultTimeout - Default auto-dismiss timeout in milliseconds (default: 3000)
 * @returns {object} Toast state and show function
 */
export function useToast(defaultTimeout = 3000) {
  const [message, setMessage] = useState(null);
  const [type, setType] = useState('info');

  /**
   * Show a toast message
   * 
   * @param {string} msg - The message to display
   * @param {string} t - Toast type: 'success', 'error', or 'info' (default: 'info')
   * @param {number} timeout - Auto-dismiss timeout in ms (uses defaultTimeout if not specified)
   */
  const show = useCallback((msg, t = 'info', timeout = defaultTimeout) => {
    setMessage(msg);
    setType(t);
    setTimeout(() => setMessage(null), timeout);
  }, [defaultTimeout]);

  return { message, type, show };
}
