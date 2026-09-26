document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-loading-form]").forEach((form) => {
    form.addEventListener("submit", () => {
      const button = form.querySelector("button[type='submit']");
      if (!button) return;
      button.disabled = true;
      const text = button.querySelector("span:first-child");
      if (text) text.textContent = "Working…";
    });
  });
});

async function deleteUser(userId) {
  if (!confirm(`Delete ${userId} and its stored plan?`)) return;
  const response = await fetch(`/api/users/${encodeURIComponent(userId)}`, { method: "DELETE" });
  if (response.ok) window.location.reload();
  else alert("Delete failed. Please check admin credentials/session.");
}
