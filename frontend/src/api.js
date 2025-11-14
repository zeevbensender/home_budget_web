// Dynamically build the backend base URL based on current location
const getBaseUrl = () => {
  const { protocol, hostname } = window.location;
  const port = 8000; // backend always listens on 8000 inside compose
  return `${protocol}//${hostname}:${port}`;
};

export async function getHealth() {
  const url = `${getBaseUrl()}/api/health`;

  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Request failed: ${response.status}`);
    return await response.text();
  } catch (error) {
    console.error('Health check failed:', error);
    return 'Error';
  }
}

export async function getExpenses() {
  const { protocol, hostname } = window.location;
  const port = 8000;
  const url = `${protocol}//${hostname}:${port}/api/expense`;
  const res = await fetch(url);
  return res.json();
}

export async function getIncomes() {
  const { protocol, hostname } = window.location;
  const port = 8000;
  const url = `${protocol}//${hostname}:${port}/api/income`;
  const res = await fetch(url);
  return res.json();
}
