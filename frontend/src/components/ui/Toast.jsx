/**
 * Toast component
 * 
 * A simple toast notification component for displaying temporary messages.
 * Typically used with the useToast hook for state management.
 * 
 * Usage:
 *   const toast = useToast();
 *   // ... later
 *   <Toast message={toast.message} type={toast.type} />
 */

import React from 'react';

/**
 * Toast notification component
 * 
 * @param {object} props
 * @param {string|null} props.message - The message to display (null hides the toast)
 * @param {string} props.type - Toast type: 'success', 'error', or 'info' (default: 'info')
 * @param {string} props.className - Additional CSS class names
 */
export default function Toast({ message, type = 'info', className = '' }) {
  if (!message) return null;

  return (
    <div className={`mobile-toast ${className}`} data-type={type}>
      {message}
    </div>
  );
}
