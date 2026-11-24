// Study garden: a timer that grows a plant. Only finished sessions are saved.
const box = document.getElementById("garden");
const pet = document.getElementById("pet");
const plant = document.getElementById("plant");
const timeEl = document.getElementById("time");
const startBtn = document.getElementById("start");
const resetBtn = document.getElementById("reset");
const bubble = document.getElementById("bubble");
const fill = document.getElementById("fill");

let info = JSON.parse(box.dataset.info);   // numbers calculated by Python (logic/garden.py)
let minutes = 25;                          // chosen session length
let remaining = minutes * 60;              // seconds left
let endAt = 0;                             // clock time when the session ends
let timer = null;                          // setInterval id while the timer runs

const say = (text) => { bubble.textContent = text; };
const pad = (n) => String(n).padStart(2, "0");
const show = (s) => { timeEl.textContent = `${pad(Math.floor(s / 60))}:${pad(s % 60)}`; };

// Parts of the plant pop in or out depending on the stage (CSS does the animation).
function showStage(stage) {
  plant.querySelectorAll(".part").forEach((part) => {
    const from = Number(part.dataset.from);
    const to = part.dataset.to === undefined ? Infinity : Number(part.dataset.to);
    part.classList.toggle("on", stage >= from && stage <= to);
  });
}

// The plant and the bar grow smoothly while a session runs.
function grow(extraMinutes) {
  const span = info.stage_end === null ? 1 : info.stage_end - info.stage_start;
  const share = info.stage_end === null ? 1 : (info.total + extraMinutes - info.stage_start) / span;
  const p = Math.min(1, Math.max(0, share));
  plant.style.transform = `scale(${0.8 + 0.2 * p})`;
  fill.style.width = `${Math.round(p * 100)}%`;
}

function updateText() {
  document.getElementById("stage-name").textContent = info.stage_name;
  document.getElementById("total").textContent = info.total;
  document.getElementById("today").textContent = info.today;
  document.getElementById("streak").textContent = info.streak;
  document.getElementById("left").textContent = info.stage_end === null
    ? "Fully grown. What a tree!"
    : `${info.minutes_left} min to go until it becomes a ${info.next_name.toLowerCase()}.`;
}

// Little hearts or stars that fly out of the plant.
function burst(symbol, count) {
  for (let i = 0; i < count; i++) {
    const s = document.createElement("span");
    s.className = symbol === "★" ? "pop star" : "pop";
    s.textContent = symbol;
    s.style.setProperty("--dx", `${Math.round(Math.random() * 220 - 110)}px`);
    s.style.setProperty("--dy", `${-Math.round(60 + Math.random() * 140)}px`);
    box.querySelector(".field").append(s);
    s.addEventListener("animationend", () => s.remove());
  }
}

function setMode(mode) {                   // "", "running" or "paused"
  box.classList.remove("running", "paused");
  if (mode) box.classList.add(mode);
}

function reset() {
  clearInterval(timer);
  timer = null;
  remaining = minutes * 60;
  show(remaining);
  setMode("");
  startBtn.textContent = "Start";
  grow(0);
  say("Ready when you are!");
}

async function finish() {
  clearInterval(timer);
  timer = null;
  setMode("");
  startBtn.textContent = "Start";
  try {
    const res = await fetch(box.dataset.url, { method: "POST", body: new URLSearchParams({ minutes }) });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error);
    const grew = data.stage > info.stage;
    info = data;
    showStage(info.stage);
    updateText();
    burst(grew ? "★" : "♥", grew ? 14 : 6);
    say(grew ? `I grew into a ${info.stage_name.toLowerCase()}!` : "Great session! Thank you!");
  } catch (error) {
    say(`Could not save: ${error.message}`);
  }
  remaining = minutes * 60;
  show(remaining);
  grow(0);
}

function tick() {
  // Using the clock (not counting ticks) keeps the time right even in a background tab.
  remaining = Math.max(0, Math.round((endAt - Date.now()) / 1000));
  show(remaining);
  grow((minutes * 60 - remaining) / 60);
  if (remaining === 0) finish();
}

startBtn.addEventListener("click", () => {
  if (timer) {                             // pause
    clearInterval(timer);
    timer = null;
    setMode("paused");
    startBtn.textContent = "Resume";
    say("I'll wait for you.");
  } else {                                 // start or resume
    endAt = Date.now() + remaining * 1000;
    timer = setInterval(tick, 250);
    setMode("running");
    startBtn.textContent = "Pause";
    say("Growing... keep going!");
    burst("♥", 2);
  }
});

resetBtn.addEventListener("click", reset);

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    if (box.classList.contains("running") || box.classList.contains("paused")) return;
    minutes = Number(chip.dataset.min);
    document.querySelectorAll(".chip").forEach((c) => c.classList.toggle("on", c === chip));
    reset();
  });
});

// Petting the plant: it boings, hearts fly out, and it says something nice.
const cheers = ["Hehe!", "That tickles!", "You can do it!", "I believe in you!", "Water me with focus!"];
function petPlant() {
  pet.classList.remove("boing");
  void pet.getBoundingClientRect();        // lets the animation restart if clicked quickly
  pet.classList.add("boing");
  burst("♥", 3);
  say(cheers[Math.floor(Math.random() * cheers.length)]);
}
pet.addEventListener("click", petPlant);
pet.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); petPlant(); } });
pet.addEventListener("animationend", (e) => { if (e.animationName === "boing") pet.classList.remove("boing"); });

window.addEventListener("beforeunload", (e) => { if (timer) e.preventDefault(); });

showStage(info.stage);
updateText();
show(remaining);
grow(0);
