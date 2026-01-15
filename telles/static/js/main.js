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
      // 実際の遷移例: window.location.href = "/attendance/";
    });
  });

  // 学科・クラスが変更されたら全行更新
  setupDepartmentClassSync();

  // 初期年度セット
  autoFillAcedemicYear();

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

function addRow() {
  const body = document.getElementById("signup-body");

  // 最新の学科・クラスの選択値を取得（最初の行または画面上の select）
  const firstDeptSelect = document.querySelector("select[name='department[]']");
  // 選択値がなければ空文字ではなく最初の option を使う（安全策）
  const departmentValue = firstDeptSelect ? firstDeptSelect.value : "";

  const newRow = document.createElement("div");
  newRow.className = "signup-row";

  newRow.innerHTML = `
    <div class="signup-cell signup-wide">
        <input type="text" name="academic_year[]" placeholder="例: 2024" required>
    </div>

    <div class="signup-cell department-cell">
        <input type="hidden" name="department[]" value="${departmentValue}">
        <select class="lock-select" disabled>
            ${firstDeptSelect ? firstDeptSelect.innerHTML : ""}
        </select>
    </div>

    <div class="signup-cell signup-wide">
        <input type="text" name="student_id[]" placeholder="ID" required>
    </div>

    <div class="signup-cell signup-wide">
        <input type="password" name="password[]" placeholder="パスワード" required>
    </div>

    <div class="signup-cell signup-wide">
        <input type="text" name="number[]" placeholder="出席番号" required>
    </div>

    <div class="signup-cell signup-wide">
        <input type="text" name="fullname[]" placeholder="氏名" required>
    </div>

    <div class="signup-cell signup-wide">
        <button type="button" onclick="removeRow(this)">削除</button>
    </div>
  `;

  body.appendChild(newRow);

  // select（表示用）の値を合わせる
  newRow.querySelectorAll("select")[0].value = departmentValue;
  // 年度自動入力
  newRow.querySelector("input[name='academic_year[]']").value = new Date().getFullYear();

  // 1行目の上4桁を反映
  propagateFirstRow();
  updateSignupBodyScroll();
}

//行削除
function removeRow(button) {
  const row = button.closest('.signup-row');
  if (row) row.remove();
  updateSignupBodyScroll();
}

// ===============================
// 全行へ「学科・クラス」を同期（hidden も更新）
// ===============================
function setupDepartmentClassSync() {
  const firstDept = document.querySelector("select[name='department[]']");
  if (!firstDept) return;

  function sync() {
    const deptVal = firstDept.value;
    document.querySelectorAll(".signup-row").forEach(row => {
      const deptSelect = row.querySelector("select.lock-select");
      const deptHidden = row.querySelector("input[name='department[]']");
      if (deptSelect) deptSelect.value = deptVal;
      if (deptHidden) deptHidden.value = deptVal;
    });
  }

  firstDept.addEventListener("change", sync);
}

// ===============================
// 年度自動入力（最初の行）
// ===============================
function autoFillAcedemicYear() {
  const yearInput = document.querySelector("input[name='academic_year[]']");
  if (yearInput && !yearInput.value) {
    const now = new Date();
    yearInput.value = now.getFullYear();
  }
}

function updateSignupBodyScroll() {
  const body = document.getElementById("signup-body");
  const rows = body.querySelectorAll(".signup-row");
  body.style.overflowY = rows.length > 1 ? "auto" : "hidden";
}

// addRow() の最後に追加
addRow = (function(original){
  return function() {
    original();
    updateSignupBodyScroll();
  }
})(addRow);

// removeRow() の最後にも追加
function removeRow(button) {
  const row = button.closest('.signup-row');
  if (row) row.remove();
  updateSignupBodyScroll();
}

// 初期ロード時もチェック
window.addEventListener("DOMContentLoaded", () => {
  updateSignupBodyScroll();
});

// -----------------------------
// 1行目の上4桁を2行目以降に反映
// -----------------------------
function propagateFirstRow() {
  const rows = document.querySelectorAll(".signup-row");
  if (rows.length < 2) return; // 2行目がない場合は何もしない

  const firstRow = rows[0];
  const firstId = firstRow.querySelector("input[name='student_id[]']").value.slice(0, 4);
  const firstPass = firstRow.querySelector("input[name='password[]']").value.slice(0, 4);
  const firstNum = firstRow.querySelector("input[name='number[]']").value.slice(0, 4);

  // 2行目以降に反映
  for (let i = 1; i < rows.length; i++) {
    if (firstId) rows[i].querySelector("input[name='student_id[]']").value = firstId;
    if (firstPass) rows[i].querySelector("input[name='password[]']").value = firstPass;
    if (firstNum) rows[i].querySelector("input[name='number[]']").value = firstNum;
  }
}

function saveFormState() {
  const rows = document.querySelectorAll(".signup-row");
  const allData = [];

  rows.forEach((row) => {
    const rowData = {};
    row.querySelectorAll("input, select").forEach((el) => {
      if (el.name) rowData[el.name] = el.value;
    });
    allData.push(rowData);
  });

  sessionStorage.setItem("signupForm", JSON.stringify(allData));
}

function restoreFormState() {
  const saved = sessionStorage.getItem("signupForm");
  if (!saved) return;

  const data = JSON.parse(saved);

  const body = document.getElementById("signup-body");
  body.innerHTML = "";

  data.forEach((rowData) => {
    const newRow = document.createElement("div");
    newRow.className = "signup-row";

    newRow.innerHTML =  `
      <div class="signup-cell signup-wide">
          <input type="text" name="academic_year[]" placeholder="例: 2024">
      </div>

      <div class="signup-cell signup-wide">
          <input type="hidden" name="department[]">
          <select class="lock-select" disabled></select>
      </div>

      <div class="signup-cell signup-wide">
          <input type="text" name="student_id[]" placeholder="ID">
      </div>

      <div class="signup-cell signup-wide">
          <input type="password" name="password[]" placeholder="パスワード">
      </div>

      <div class="signup-cell signup-wide">
          <input type="text" name="number[]" placeholder="出席番号">
      </div>

      <div class="signup-cell signup-wide">
          <input type="text" name="fullname[]" placeholder="氏名">
      </div>

      <div class="signup-cell signup-wide">
          <button type="button" onclick="removeRow(this)">削除</button>
      </div>
    `;

    body.appendChild(newRow);

    newRow.querySelectorAll("input, select").forEach((el) => {
      if (rowData[el.name] != undefined) {
        el.value = rowData[el.name];
      }
    });
  });

  updateSignupBodyScroll();
}

function initAutoSave() {
  document.addEventListener("input", (e) =>{
    if (e.target.matches("input, select")){
      saveFormState();
    }
  });
}

function initFormSubmitClear() {
  const form = document.querySelector("form");
  if (!form) return;

  form.addEventListener("submit", () => {
    sessionStorage.removeItem("signupForm")
  })
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
      const now = new Date();
    if (
      year === now.getFullYear() &&
      month === now.getMonth() &&
      d === now.getDate()
    ) {
      cell.classList.add("today");
    }
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
 
const prevBtn = document.getElementById("prevMonth");
if (prevBtn) {
  prevBtn.addEventListener("click", () => {
    current.setMonth(current.getMonth() - 1);
    renderCalendar(current);
  });
}

const nextBtn = document.getElementById("nextMonth");
if (nextBtn) {
  nextBtn.addEventListener("click", () => {
    current.setMonth(current.getMonth() + 1);
    renderCalendar(current);
  });
}

 
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
    const countdownElement = document.getElementById("countdown");
    const countdownNumber = document.getElementById("countdown-number");

    if (countdownElement && countdownNumber) {
        let countdown = parseInt(countdownNumber.textContent, 10);
        const loginUrl = countdownElement.dataset.loginUrl;

        const interval = setInterval(() => {
            countdown--;
            if (countdown >= 0) {
                countdownNumber.textContent = countdown;
            }

            if (countdown < 0) {
                clearInterval(interval);
                if (loginUrl) {
                    window.location.href = loginUrl;
                } else {
                    console.error("loginUrl が設定されていません");
                }
            }
        }, 1000);
    }
});


// ===============================
// 1行目 input 監視
// ===============================
function setupFirstRowInputSync() {
  const firstRow = document.querySelector(".signup-row");
  if (!firstRow) return;

  ["student_id[]", "password[]", "number[]"].forEach(name => {
    const input = firstRow.querySelector(`input[name='${name}']`);
    if (input) {
      input.addEventListener("input", propagateFirstRow);
    }
  });
}
