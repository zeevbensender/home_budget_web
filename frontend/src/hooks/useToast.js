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

import { useState, useCallback, useRef, useEffect } from 'react';

/**
 * Custom hook for managing toast notifications
 * 
 * @param {number} defaultTimeout - Default auto-dismiss timeout in milliseconds (default: 3000)
 * @returns {object} Toast state and show function
 */
export function useToast(defaultTimeout = 3000) {
  const [message, setMessage] = useState(null);
  const [type, setType] = useState('info');
  const timeoutRef = useRef(null);

  // Cleanup timeout on unmount to prevent memory leaks
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  /**
   * Show a toast message
   * 
   * @param {string} msg - The message to display
   * @param {string} t - Toast type: 'success', 'error', or 'info' (default: 'info')
   * @param {number} timeout - Auto-dismiss timeout in ms (uses defaultTimeout if not specified)
   */
  const show = useCallback((msg, t = 'info', timeout = defaultTimeout) => {
    // Clear any existing timeout to prevent race conditions
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    setMessage(msg);
    setType(t);
    
    // Set new timeout
    timeoutRef.current = setTimeout(() => {
      setMessage(null);
      timeoutRef.current = null;
    }, timeout);
  }, [defaultTimeout]);

  return { message, type, show };
}
