const CAT_NAMES = { wx: "Weather", fuel: "Fuel", nav: "Navigation", atc: "ATC / Comms", perf: "Performance", airspace: "Airspace" };
const CAT_CLASS = { wx: "cat-wx", fuel: "cat-fuel", nav: "cat-nav", atc: "cat-atc", perf: "cat-perf", airspace: "cat-airspace" };

let questions = [], current = 0, score = 0, answered = false, results = [];

async function init() {
  const app = document.getElementById("app");
  app.innerHTML = '<div class="loading">Loading questions…</div>';
  const res = await fetch("/api/questions");
  questions = await res.json();
  current = 0; score = 0; answered = false; results = [];
  render();
}

function render() {
  const app = document.getElementById("app");
  if (current >= questions.length) { renderResults(app); return; }
  const q = questions[current];
  const pct = Math.round((current / questions.length) * 100);
  const letters = ["A", "B", "C", "D"];
  app.innerHTML = `
    <div class="progress-bg"><div class="progress-fill" style="width:${pct}%"></div></div>
    <div class="meta">
      <span>Question ${current + 1} of ${questions.length}</span>
      <span class="score-badge">${score} correct</span>
    </div>
    <div class="question-card">
      <div class="q-label">What does this abbreviation mean?</div>
      <div class="q-abbr">${q.abbr}</div>
      <span class="cat-pill ${CAT_CLASS[q.cat]}">${CAT_NAMES[q.cat]}</span>
    </div>
    <div class="options" id="opts">
      ${q.options.map((opt, i) => `<button class="opt-btn" id="opt${i}" onclick="answer(${i})"><span class="opt-letter">${letters[i]}</span>${opt}</button>`).join("")}
    </div>
    <div id="feedback-area"></div>
  `;
}

function answer(idx) {
  if (answered) return;
  answered = true;
  const q = questions[current];
  const isCorrect = q.options[idx] === q.correct;
  if (isCorrect) score++;
  results.push({ abbr: q.abbr, cat: q.cat, correct: q.correct, isCorrect });

  document.querySelectorAll(".opt-btn").forEach((b, i) => {
    b.disabled = true;
    if (q.options[i] === q.correct) b.classList.add(isCorrect && i === idx ? "correct" : "reveal");
    else if (i === idx && !isCorrect) b.classList.add("wrong");
  });

  document.getElementById("feedback-area").innerHTML = `
    <div class="feedback ${isCorrect ? "correct" : "wrong"}" style="margin-bottom:0.75rem">
      ${isCorrect ? "Correct!" : "Not quite &mdash; <strong>" + q.abbr + "</strong> = " + q.correct}
    </div>
    <button class="next-btn" onclick="nextQ()">${current < questions.length - 1 ? "Next question" : "See results"}</button>
  `;
}

function nextQ() { current++; answered = false; render(); }

function renderResults(app) {
  const pct = Math.round((score / questions.length) * 100);
  const msg = score <= 3 ? "Keep at it &mdash; run it again and those will start sticking."
    : score <= 6 ? "Not bad! A few more rounds and you'll nail these."
    : score <= 8 ? "Good flying &mdash; just a couple of gaps to iron out."
    : "Excellent! You know your abbreviations cold.";

  const rows = results.map(r => `
    <div class="bd-row">
      <span class="bd-abbr">${r.abbr}</span>
      <span class="bd-def">${r.correct}</span>
      <span class="bd-cat"><span class="cat-pill ${CAT_CLASS[r.cat]}">${CAT_NAMES[r.cat]}</span></span>
      <span class="${r.isCorrect ? "tick" : "cross"}">${r.isCorrect ? "&#10003;" : "&#10007;"}</span>
    </div>`).join("");

  app.innerHTML = `
    <div class="results">
      <div class="q-label">Quiz complete</div>
      <div class="results-score">${score}/${questions.length}</div>
      <div class="results-sub">${pct}% correct</div>
      <div class="results-msg">${msg}</div>
      <div class="breakdown">${rows}</div>
      <button class="restart-btn" onclick="init()">New random quiz</button>
    </div>
  `;
}

init();
