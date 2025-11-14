export default function AddFloatingButton({ onClick, title = "Add Transaction" }) {
  return (
    <button
      onClick={onClick}
      title={title}
      style={{
        position: "fixed",
        right: "20px",
        bottom: "20px",
        width: "56px",
        height: "56px",
        borderRadius: "50%",
        border: "none",
        fontSize: "28px",
        lineHeight: "0",
        cursor: "pointer",
        boxShadow: "0 6px 16px rgba(0,0,0,0.2)",
        background: "#2563eb",
        color: "#fff",
      }}
    >
      +
    </button>
  );
}
