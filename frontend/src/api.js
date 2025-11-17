// FRONTEND/src/api.js

// Values injected by Render if deployed:
const host = import.meta.env.VITE_API_BASE_URL_HOST;
const port = import.meta.env.VITE_API_BASE_URL_PORT;

// -----------------------------
// URL building logic
// -----------------------------

let BASE_URL;

// Render hosting (VITE_API_BASE_URL_HOST will be defined)
if (host) {
  // Render exposes HTTPS on port 443 — no need to append :port
  BASE_URL = `https://${host}/api`;
} else {
  // Local development (docker-compose OR local vite)
  const localHost = window.location.hostname;
  BASE_URL = `http://${localHost}:8000/api`;
}

console.log("API Base URL:", BASE_URL);

// -----------------------------
// API calls
// -----------------------------

export async function getExpenses() {
  const r = await fetch(`${BASE_URL}/expense`);
  return r.json();
}

export async function getIncomes() {
  const r = await fetch(`${BASE_URL}/income`);
  return r.json();
}

export async function createExpense(data) {
  const r = await fetch(`${BASE_URL}/expense`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return r.json();
}

export async function createIncome(data) {
  const r = await fetch(`${BASE_URL}/income`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return r.json();
}

export async function updateExpense(id, data) {
  const r = await fetch(`${BASE_URL}/expense/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return r.json();
}

export async function updateIncome(id, data) {
  const r = await fetch(`${BASE_URL}/income/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return r.json();
}

export async function deleteExpense(id) {
  return fetch(`${BASE_URL}/expense/${id}`, { method: "DELETE" });
}

export async function deleteIncome(id) {
  return fetch(`${BASE_URL}/income/${id}`, { method: "DELETE" });
}

export async function bulkDeleteExpenses(ids) {
  return fetch(`${BASE_URL}/expense/bulk-delete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ids }),
  });
}

export async function bulkDeleteIncomes(ids) {
  return fetch(`${BASE_URL}/income/bulk-delete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ids }),
  });
}
