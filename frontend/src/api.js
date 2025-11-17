const BASE_URL = import.meta.env.VITE_API_BASE_URL
  || `${window.location.protocol}//${window.location.hostname}:8000/api`;

// ------------------------
// EXPENSES
// ------------------------
export async function getExpenses() {
  const res = await fetch(`${BASE_URL}/expense`);
  return res.json();
}

export async function createExpense(data) {
  const res = await fetch(`${BASE_URL}/expense`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function updateExpense(id, data) {
  const res = await fetch(`${BASE_URL}/expense/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

// ------------------------
// INCOME
// ------------------------
export async function getIncomes() {
  const res = await fetch(`${BASE_URL}/income`);
  return res.json();
}

export async function createIncome(data) {
  const res = await fetch(`${BASE_URL}/income`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function updateIncome(id, data) {
  const res = await fetch(`${BASE_URL}/income/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}
