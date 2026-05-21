const CAT_NAMES = { wx: "Weather", fuel: "Fuel", nav: "Navigation", atc: "ATC / Comms", perf: "Performance", airspace: "Airspace" };
const CAT_CLASS = { wx: "cat-wx", fuel: "cat-fuel", nav: "cat-nav", atc: "cat-atc", perf: "cat-perf", airspace: "cat-airspace" };

// Session state
let sessionPool    = [];       // all questions for this session
let sessionCorrect = new Set(); // abbrs answered correctly at least once
let sessionScore   = 0;        // total correct answers across all rounds
let sessionTotal   = 0;        // total answers given across all rounds
let round          = 0;

// Round state
let questions    = [];
let currentOpts  = [];         // shuffled options for the current question
let current      = 0;
let score        = 0;
let answered     = false;
let results      = [];

function getCat() {
  return new URLSearchParams(window.location.search).get("cat");
}

function remaining() {
  return sessionPool.filter(q => !sessionCorrect.has(q.abbr));
}

// ── Session start ────────────────────────────────────────────────────────────

async function startSession() {
  document.getElementById("app").innerHTML = '<div class="loading">Loading questions…</div>';
  const cat = getCat();
  const url = cat
    ? `/api/questions?all=true&cat=${encodeURIComponent(cat)}`
    : "/api/questions?all=true";
  const res  = await fetch(url);
  sessionPool    = await res.json();
  sessionCorrect = new Set();
  sessionScore   = 0;
  sessionTotal   = 0;
  round          = 0;
  loadNextBatch();
}

// ── Round management ─────────────────────────────────────────────────────────

function loadNextBatch() {
  const pool = remaining();
  if (pool.length === 0) { renderSessionComplete(); return; }
  round++;
  questions = shuffle(pool).slice(0, 10);
  current   = 0;
  score     = 0;
  answered  = false;
  results   = [];
  updateSubtitle();
  render();
}

function shuffle(arr) {
  return [...arr].sort(() => Math.random() - 0.5);
}

function updateSubtitle() {
  const subtitle = document.querySelector(".subtitle");
  if (!subtitle) return;
  const cat = getCat();
  const label = cat && CAT_NAMES[cat] ? CAT_NAMES[cat] : "All categories";
  const rem   = remaining().length;
  subtitle.textContent = `${label} — Round ${round} — ${rem} question${rem !== 1 ? "s" : ""} remaining`;
}

// ── Render question ──────────────────────────────────────────────────────────

function render() {
  const app = document.getElementById("app");
  if (current >= questions.length) { renderResults(app); return; }
  const q      = questions[current];
  const pct    = Math.round((current / questions.length) * 100);
  const letters = ["A", "B", "C", "D"];
  currentOpts  = shuffle(q.options);

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
      ${currentOpts.map((opt, i) => `<button class="opt-btn" id="opt${i}" onclick="answer(${i})"><span class="opt-letter">${letters[i]}</span>${opt}</button>`).join("")}
    </div>
    <div id="feedback-area"></div>
  `;
}

// ── Answer handling ──────────────────────────────────────────────────────────

function answer(idx) {
  if (answered) return;
  answered = true;
  const q         = questions[current];
  const isCorrect = currentOpts[idx] === q.correct;
  if (isCorrect) {
    score++;
    sessionScore++;
    sessionCorrect.add(q.abbr);
  }
  sessionTotal++;
  results.push({ abbr: q.abbr, cat: q.cat, correct: q.correct, isCorrect });

  document.querySelectorAll(".opt-btn").forEach((b, i) => {
    b.disabled = true;
    if (currentOpts[i] === q.correct) b.classList.add(isCorrect && i === idx ? "correct" : "reveal");
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

// ── Round results ────────────────────────────────────────────────────────────

function renderResults(app) {
  const pct      = Math.round((score / questions.length) * 100);
  const mastered = sessionCorrect.size;
  const total    = sessionPool.length;
  const rem      = remaining().length;
  const mastPct  = Math.round((mastered / total) * 100);

  const msg = score === questions.length
    ? "Perfect round — all correct!"
    : score >= questions.length * 0.8 ? "Great round — nearly there."
    : score >= questions.length * 0.5 ? "Good effort — keep going."
    : "Keep at it — repetition is the key.";

  const rows = results.map(r => `
    <div class="bd-row">
      <span class="bd-abbr">${r.abbr}</span>
      <span class="bd-def">${r.correct}</span>
      <span class="bd-cat"><span class="cat-pill ${CAT_CLASS[r.cat]}">${CAT_NAMES[r.cat]}</span></span>
      <span class="${r.isCorrect ? "tick" : "cross"}">${r.isCorrect ? "&#10003;" : "&#10007;"}</span>
    </div>`).join("");

  app.innerHTML = `
    <div class="results">
      <div class="q-label">Round ${round} complete</div>
      <div class="results-score">${score}/${questions.length}</div>
      <div class="results-sub">${pct}% correct this round</div>
      <div class="session-progress">
        <div class="session-bar-bg">
          <div class="session-bar-fill" style="width:${mastPct}%"></div>
        </div>
        <p class="session-label">${mastered} of ${total} mastered &mdash; ${rem} still to go</p>
      </div>
      <div class="results-msg">${msg}</div>
      <div class="breakdown">${rows}</div>
      ${rem > 0
        ? `<button class="restart-btn" onclick="loadNextBatch()">Next round &rarr;</button>`
        : `<button class="restart-btn" onclick="renderSessionComplete()">See final score &rarr;</button>`
      }
      <button class="restart-btn secondary-btn" onclick="startSession()">Start over</button>
    </div>
  `;
}

// ── Session complete ─────────────────────────────────────────────────────────

function renderSessionComplete() {
  const app     = document.getElementById("app");
  const total   = sessionPool.length;
  const accPct  = sessionTotal > 0 ? Math.round((sessionScore / sessionTotal) * 100) : 0;

  app.innerHTML = `
    <div class="results">
      <div class="q-label">Session complete</div>
      <div class="results-score session-complete-tick">&#10003;</div>
      <div class="results-sub">All ${total} questions mastered</div>
      <div class="results-msg">
        Excellent — you know every abbreviation in this set.<br>
        Start a new session to mix it up again.
      </div>
      <div class="session-stats">
        <div class="stat"><span class="stat-val">${total}</span><span class="stat-label">Questions</span></div>
        <div class="stat"><span class="stat-val">${round}</span><span class="stat-label">Rounds</span></div>
        <div class="stat"><span class="stat-val">${accPct}%</span><span class="stat-label">Accuracy</span></div>
      </div>
      <button class="restart-btn" onclick="startSession()">New session</button>
    </div>
  `;
}

startSession();
