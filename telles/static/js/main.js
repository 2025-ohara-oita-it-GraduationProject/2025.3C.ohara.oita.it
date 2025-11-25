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

// ===============================
// カレンダー機能
// ===============================
 
 
// ===============================
// 現在日時を表示（カレンダー用など）
// ===============================
window.addEventListener("load", () => {
  const now = new Date();
  const formatted = `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日 `
                  + `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`;
  const el = document.getElementById("datetime");
  if (el) el.textContent = formatted;
});
// ===============================
// カレンダー生成 + 日付選択処理
// ===============================
document.addEventListener("DOMContentLoaded", () => {
  const calendarBody = document.getElementById("calendar-body");
  const currentMonthLabel = document.getElementById("currentMonth");
  const selectedDateEl = document.getElementById("selected-date");
  const confirmBtn = document.getElementById("confirm-btn");
 
  let current = new Date();
 
  function renderCalendar(date) {
    const year = date.getFullYear();
    const month = date.getMonth();
    currentMonthLabel.textContent = `${year}年 ${month + 1}月`;
 
    const firstDay = new Date(year, month, 1).getDay();
    const lastDate = new Date(year, month + 1, 0).getDate();
 
    calendarBody.innerHTML = "";
    let row = document.createElement("tr");
 
    for (let i = 0; i < firstDay; i++) {
      row.appendChild(document.createElement("td"));
    }
 
    for (let d = 1; d <= lastDate; d++) {
      const cell = document.createElement("td");
      cell.textContent = d;
      cell.addEventListener("click", () => {
      // ① 以前の選択状態をリセット
      const allCells = calendarBody.querySelectorAll("td");
      allCells.forEach(td => td.classList.remove("selected"));
 
      // ② 今クリックしたセルに選択クラスを付与
      cell.classList.add("selected");
 
      // ③ 選択日付を表示
      selectedDateEl.textContent = `${year}年${month + 1}月${d}日`;
    });
 
 
      row.appendChild(cell);
 
      if ((firstDay + d) % 7 === 0 || d === lastDate) {
        calendarBody.appendChild(row);
        row = document.createElement("tr");
      }
    }
  }
 
  document.getElementById("prevMonth").addEventListener("click", () => {
    current.setMonth(current.getMonth() - 1);
    renderCalendar(current);
  });
 
  document.getElementById("nextMonth").addEventListener("click", () => {
    current.setMonth(current.getMonth() + 1);
    renderCalendar(current);
  });
 
  confirmBtn.addEventListener("click", () => {
  const selectedDate = selectedDateEl.textContent;
 
  if (selectedDate === "―" || selectedDate.trim() === "") {
    alert("日付を選択してください。");
    return;
  }
 
  // Django のURLパターンに合わせて遷移（例: /attendance_form/）
  // 選択した日付をクエリパラメータで送る
  const encodedDate = encodeURIComponent(selectedDate);
  window.location.href = `/attendance_form/?date=${encodedDate}`;
  });
  renderCalendar(current);
});
// =============================
// パスワードリセット：行追加
// =============================
document.addEventListener("DOMContentLoaded", function () {

    const addBtn = document.getElementById("add-reset-row-btn");
    const body = document.getElementById("reset-body");

    if (addBtn) {
        addBtn.addEventListener("click", function () {

            const row = document.createElement("div");
            row.className = "signup-row";

            row.innerHTML = `
                <div class="signup-cell signup-wide">
                    <input type="text" name="id[]" required>
                </div>
                <div class="signup-cell signup-wide">
                    <input type="text" name="classroom[]" required>
                </div>
                <div class="signup-cell signup-wide">
                    <input type="text" name="number[]" required>
                </div>
                <div class="signup-cell signup-wide">
                    <input type="text" name="fullname[]" required>
                </div>
                <div class="signup-cell signup-wide">
                    <input type="password" name="new_password[]" required>
                </div>
                <div class="signup-cell signup-wide">
                    <button type="button" class="remove-reset-row">削除</button>
                </div>
            `;

            body.appendChild(row);
        });
    }

    // =============================
    // パスワードリセット：行削除
    // =============================
    document.addEventListener("click", function (e) {
        if (e.target.classList.contains("remove-reset-row")) {
            e.target.closest(".signup-row").remove();
        }
    });

});
document.addEventListener("DOMContentLoaded", () => {
    // student_reset_password_done.html 用のカウントダウン
    const countdownElement = document.getElementById("countdown");
    if (countdownElement) {  // 要素が存在するページだけ実行
        let countdown = 5; // 秒数
        countdownElement.textContent = `${countdown}秒後にログインページに移動します...`;

        const interval = setInterval(() => {
            countdown--;
            if (countdown > 0) {
                countdownElement.textContent = `${countdown}秒後にログインページに移動します...`;
            } else {
                clearInterval(interval);
                // Django の URL を JS に埋め込む場合は data- 属性で渡す
                const loginUrl = countdownElement.dataset.loginUrl;
                window.location.href = loginUrl;
            }
        }, 1000);
    }
});



