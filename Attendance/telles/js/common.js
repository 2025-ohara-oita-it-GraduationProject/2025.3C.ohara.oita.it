// ================================
// 現在日時を表示
// ================================
window.onload = function() {
  const now = new Date();
  const formatted = now.getFullYear() + "/" +
    String(now.getMonth() + 1).padStart(2, '0') + "/" +
    String(now.getDate()).padStart(2, '0') + " " +
    String(now.getHours()).padStart(2, '0') + ":" +
    String(now.getMinutes()).padStart(2, '0');
  const dateElem = document.getElementById("datetime");
  if (dateElem) dateElem.textContent = formatted;
};
