export function formatNumber(value) {
  const num = Number(value);
  if (Number.isNaN(num)) return null;
  return num.toFixed(2);
}
