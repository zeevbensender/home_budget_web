export default function usePatchBackend() {
  const patch = async (type, row, field, value) => {
    if (!row?.id) return;

    const base = `${window.location.protocol}//${window.location.hostname}:8000`;
    const endpoint =
      type === "expense"
        ? `/api/expense/${row.id}`
        : `/api/income/${row.id}`;
    const url = `${base}${endpoint}`;

    console.log(`PATCH → ${url} (${field}=${value})`);

    try {
      const res = await fetch(url, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ field, value }),
      });

      if (!res.ok) {
        console.error("PATCH failed", res.status);
      } else {
        console.log(`✅ Updated ${type} ${row.id} field ${field}`);
      }
    } catch (err) {
      console.error("PATCH error:", err);
    }
  };

  return patch;
}
