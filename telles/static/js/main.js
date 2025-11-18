// ===============================
// main.js - 共通スクリプト
// ===============================

// ページ読み込み完了時
window.addEventListener("DOMContentLoaded", () => {
  console.log("main.js loaded!");

  // 日時を更新（1分ごとに再描画）
  updateDateTime();
  setInterval(updateDateTime, 60000);

  // ログアウト確認イベント
  const logoutBtn = document.querySelector(".logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", (e) => {
      const ok = confirm("本当にログアウトしますか？");
      if (!ok) e.preventDefault();
    });
  }

  // サイドバーのメニュークリックイベント
  const menuItems = document.querySelectorAll(".sidebar li");
  menuItems.forEach(item => {
    item.addEventListener("click", () => {
      alert(`${item.textContent.trim()} ページに移動します。`);
      // 実際の遷移例: window.location.href = "/attendance/";
    });
  });
});

// ===============================
// 関数：現在日時を更新
// ===============================
function updateDateTime() {
  const el = document.getElementById("datetime");
  if (el) {
    const now = new Date();
    const formatted =
      now.getFullYear() + "/" +
      String(now.getMonth() + 1).padStart(2, "0") + "/" +
      String(now.getDate()).padStart(2, "0") + " " +
      String(now.getHours()).padStart(2, "0") + ":" +
      String(now.getMinutes()).padStart(2, "0");
    el.textContent = formatted;
  }
}

//生徒サインアップ行追加
function addRow() {
  const body = document.getElementById("signup-body");
  //新しい行を作る
  const newRow = document.createElement("div");
  newRow.className = "signup-row";

  newRow.innerHTML = `
    <div class="signup-cell signup-wide">
        <input type="text" name="id[]" required>
    </div>
    <div class="signup-cell signup-wide">
        <input type="text" name="classroom[]" required>
    </div>
    <div class="signup-cell signup-wide">
        <input type="password" name="password[]" required>
    </div>
    <div class="signup-cell signup-wide">
        <input type="text" name="number[]" required>
    </div>
    <div class="signup-cell signup-wide">
        <input type="text" name="fullname[]" required>
    </div>
    <div class="signup-cell signup-wide">
        <button type="button" onclick="removeRow(this)">削除</button>
    </div>
  `;
  body.appendChild(newRow);
  body.scrollTop = body.scrollHeight;
}

//行削除
function removeRow(button) {
  const row = button.closest('.signup-row');
  if (row) {
    row.remove();
  }
}