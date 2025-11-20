// FRONTEND/src/api.js

// ----------------------------------------------
// Determine API base URL
// ----------------------------------------------
const apiUrl = process.env.REACT_APP_API_URL;
const BASE_URL =
  process.env.REACT_APP_API_URL ||
  `https://${window.location.hostname}/api`;
//  'https://hbw-backend.onrender.com/api';


console.log("==> API Base URL:", BASE_URL);
console.log("==> process.env.REACT_APP_API_URL:", process.env.REACT_APP_API_URL);
console.log("==> import.meta.env.REACT_APP_API_URL:", import.meta.env.REACT_APP_API_URL);
console.log("==> apiUrl:", apiUrl);

// Helper for JSON requests
async function request(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json().catch(() => null);
}

// ----------------------------------------------
// EXPENSES
// ----------------------------------------------

export function getExpenses() {
  return request(`${BASE_URL}/expense`);
}

export function createExpense(data) {
  return request(`${BASE_URL}/expense`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function updateExpense(id, data) {
  return request(`${BASE_URL}/expense/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function deleteExpense(id) {
  return fetch(`${BASE_URL}/expense/${id}`, {
    method: "DELETE",
  });
}

export function bulkDeleteExpenses(ids) {
  return fetch(`${BASE_URL}/expense/bulk-delete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ids }),
  });
}

// ----------------------------------------------
// INCOME
// ----------------------------------------------

export function getIncomes() {
  return request(`${BASE_URL}/income`);
}

export function createIncome(data) {
  return request(`${BASE_URL}/income`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function updateIncome(id, data) {
  return request(`${BASE_URL}/income/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function deleteIncome(id) {
  return fetch(`${BASE_URL}/income/${id}`, {
    method: "DELETE",
  });
}

export function bulkDeleteIncomes(ids) {
  return fetch(`${BASE_URL}/income/bulk-delete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ids }),
  });
}
