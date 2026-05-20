#!/usr/bin/env python3
"""
VFR Abbreviations Quiz
Run with:  python vfr_quiz.py
Then open: http://localhost:8080
"""

import http.server
import json
import webbrowser
import threading

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VFR Abbreviations Quiz</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, -apple-system, sans-serif; background: #f5f5f0; color: #1a1a1a; min-height: 100vh; display: flex; align-items: flex-start; justify-content: center; padding: 2rem 1rem; }
  .container { width: 100%; max-width: 640px; }
  h1 { font-size: 1.1rem; font-weight: 600; margin-bottom: 0.25rem; color: #1a1a1a; }
  .subtitle { font-size: 0.85rem; color: #666; margin-bottom: 1.5rem; }
  .progress-bg { height: 4px; background: #ddd; border-radius: 2px; margin-bottom: 1.25rem; }
  .progress-fill { height: 4px; background: #378ADD; border-radius: 2px; transition: width 0.3s; }
  .meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; font-size: 0.85rem; color: #666; }
  .score-badge { background: #e6f1fb; color: #0c447c; padding: 3px 10px; border-radius: 20px; font-weight: 600; font-size: 0.8rem; }
  .question-card { background: #fff; border: 1px solid #e5e5e5; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; text-align: center; }
  .q-label { font-size: 0.7rem; font-weight: 600; color: #999; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.75rem; }
  .q-abbr { font-family: 'Courier New', monospace; font-size: 2.25rem; font-weight: 700; color: #1a1a1a; margin-bottom: 0.75rem; }
  .cat-pill { display: inline-block; font-size: 0.72rem; padding: 3px 10px; border-radius: 20px; font-weight: 600; }
  .cat-wx       { background: #e6f1fb; color: #0c447c; }
  .cat-fuel     { background: #eaf3de; color: #27500a; }
  .cat-nav      { background: #eeedfe; color: #3c3489; }
  .cat-atc      { background: #faeeda; color: #633806; }
  .cat-perf     { background: #faece7; color: #712b13; }
  .cat-airspace { background: #fbeaf0; color: #72243e; }
  .options { display: grid; gap: 8px; margin-bottom: 0.75rem; }
  .opt-btn { width: 100%; text-align: left; padding: 13px 16px; border: 1px solid #ddd; border-radius: 8px; background: #fff; color: #1a1a1a; font-size: 0.9rem; cursor: pointer; line-height: 1.4; display: flex; gap: 12px; align-items: flex-start; transition: background 0.1s, border-color 0.1s; }
  .opt-btn:hover:not(:disabled) { background: #f5f5f0; border-color: #aaa; }
  .opt-btn.correct { background: #eaf3de; border-color: #3b6d11; color: #27500a; }
  .opt-btn.wrong   { background: #fcebeb; border-color: #a32d2d; color: #791f1f; }
  .opt-btn.reveal  { background: #eaf3de; border-color: #3b6d11; color: #27500a; }
  .opt-btn:disabled { cursor: default; }
  .opt-letter { font-weight: 700; font-size: 0.8rem; min-width: 18px; padding-top: 2px; opacity: 0.4; }
  .feedback { font-size: 0.85rem; padding: 10px 14px; border-radius: 8px; line-height: 1.6; margin-bottom: 0.75rem; }
  .feedback.correct { background: #eaf3de; color: #27500a; }
  .feedback.wrong   { background: #fcebeb; color: #791f1f; }
  .next-btn { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; background: #f5f5f0; color: #1a1a1a; font-size: 0.9rem; font-weight: 600; cursor: pointer; }
  .next-btn:hover { background: #eaeae5; }
  .results { text-align: center; background: #fff; border: 1px solid #e5e5e5; border-radius: 12px; padding: 2rem 1.5rem; }
  .results-score { font-size: 3.5rem; font-weight: 700; color: #1a1a1a; margin: 0.5rem 0; }
  .results-sub { font-size: 0.85rem; color: #666; margin-bottom: 1rem; }
  .results-msg { font-size: 0.95rem; color: #1a1a1a; margin-bottom: 1.5rem; line-height: 1.6; }
  .breakdown { text-align: left; border: 1px solid #e5e5e5; border-radius: 10px; overflow: hidden; margin-bottom: 1.5rem; }
  .bd-row { display: grid; grid-template-columns: 60px 1fr 100px 24px; gap: 10px; align-items: center; padding: 10px 14px; border-bottom: 1px solid #f0f0f0; font-size: 0.8rem; }
  .bd-row:last-child { border-bottom: none; }
  .bd-abbr { font-family: 'Courier New', monospace; font-weight: 700; font-size: 0.8rem; }
  .bd-def  { color: #555; line-height: 1.4; }
  .bd-cat  { text-align: right; }
  .tick { color: #3b6d11; font-weight: 700; font-size: 1rem; }
  .cross { color: #a32d2d; font-weight: 700; font-size: 1rem; }
  .restart-btn { padding: 12px 36px; border: 1px solid #ddd; border-radius: 8px; background: #f5f5f0; color: #1a1a1a; font-size: 0.9rem; font-weight: 600; cursor: pointer; }
  .restart-btn:hover { background: #eaeae5; }
  #feedback-area { min-height: 0; }
</style>
</head>
<body>
<div class="container">
  <h1>VFR Abbreviations Quiz</h1>
  <p class="subtitle">EGMC &rarr; EGJJ &mdash; 10 random questions each round</p>
  <div id="app"></div>
</div>

<script>
const CAT_NAMES  = { wx:"Weather", fuel:"Fuel", nav:"Navigation", atc:"ATC / Comms", perf:"Performance", airspace:"Airspace" };
const CAT_CLASS  = { wx:"cat-wx", fuel:"cat-fuel", nav:"cat-nav", atc:"cat-atc", perf:"cat-perf", airspace:"cat-airspace" };

const ALL = [
  ["OFP","nav","Operational Flight Plan — your full SimBrief flight document",["Outbound Flight Path — the planned departure track","Official Fuel Procedure — refuelling sign-off checklist","Overflight Permit — diplomatic clearance for foreign airspace"]],
  ["VFR","atc","Visual Flight Rules — flying by visual reference to the ground",["Verified Flight Record — logged data from the FMC","Variable Frequency Radio — multi-band comms unit","Vertical Fix Reference — a charted altitude constraint"]],
  ["IFR","atc","Instrument Flight Rules — flying solely by instruments, no visual reference required",["Initial Fix Report — position call at the first waypoint","In-Flight Radar — weather radar system","Integrated Frequency Range — radio spectrum allocation"]],
  ["FL","nav","Flight Level — altitude in hundreds of feet above standard pressure (1013hPa)",["Fixed Limit — maximum permitted speed at a given altitude","Forward Leg — the outbound segment of a route","Fuel Load — total usable fuel quantity on board"]],
  ["TAS","perf","True Airspeed — actual speed through the air, corrected for altitude and temperature",["Traffic Advisory System — TCAS display mode","Transponder Activation Signal — SSR interrogation pulse","Terminal Approach Speed — Vref for landing"]],
  ["GS","perf","Ground Speed — your speed over the ground after wind is factored in",["Glide Slope — the vertical component of an ILS approach","Gate Signal — ATC pushback approval call","Gust Spread — difference between steady wind and gust speed"]],
  ["QNH","wx","Altimeter setting that makes your altimeter read true altitude above sea level",["Qualified Navigation Heading — verified magnetic track","Queue Notification Hold — ground delay programme message","Quadrant Navigation Height — sector safe altitude"]],
  ["CAVOK","wx","Ceiling And Visibility OK — visibility 10km+, no significant cloud below 5,000ft, no weather",["Controlled Airspace Vertical Overlay Keep-out zone","Civil Aviation Operator Knowledge assessment","Cruise Altitude Verified OK — dispatcher confirmation"]],
  ["METAR","wx","Meteorological Aerodrome Report — current actual weather observation at an airfield",["Mandatory En-route Traffic Advisory Report","Minimum En-route Terrain Altitude Reading","Multi-Engine Training Approval Record"]],
  ["TAF","wx","Terminal Aerodrome Forecast — weather forecast for an airfield, typically 24 hours ahead",["Traffic Advisory Frequency — UNICOM or AFIS channel","Transponder Acknowledgement Frame — SSR data packet","Taxiway Allocation Form — apron management document"]],
  ["SIGMET","wx","Significant Meteorological Information — warning of serious en-route hazards like TS or icing",["Standard Instrument Go-around Minimum Entry Time","Secondary ILS Guidance Monitoring Equipment","Squawk Identification Ground Met Entry Tag"]],
  ["AIRMET","wx","Airmen's Meteorological Information — lower-level weather advisory aimed at light aircraft",["Airspace Management Entry Tag — sector boundary label","Airport Meteorological Equipment Test schedule","Altitude Indicator Reading — Met office instrument"]],
  ["TS","wx","Thunderstorm — active convective storm with lightning, a serious flight hazard",["Transition Symbol — procedure turn marker on a chart","Traffic Separation — minimum distance standard between aircraft","Taxiway Surface — pavement condition report code"]],
  ["TSRA","wx","Thunderstorm with rain — a thunderstorm cell accompanied by rainfall",["Terminal Standard Radar Approach procedure","Transponder Signal Range Attenuation factor","Traffic Separation — Radar Advisory service"]],
  ["SHRA","wx","Shower rain — intermittent rainfall, not continuous precipitation",["Standard Holding and Route Assignment","Secondary Hazard Reporting Area designation","Squawk Hold — Radar Approach instruction"]],
  ["BR","wx","Mist — visibility reduced to between 1,000m and 9,999m by water droplets",["Braking Report — runway friction measurement","Base Report — field elevation and obstacle data","Block Release — ATC pushback approval code"]],
  ["FG","wx","Fog — visibility below 1,000m, extremely serious for VFR flight",["Flight Guard — terrain proximity warning active","Fuel Gauge — cockpit quantity indicator reading","Final Gate — last hold-short point before the runway"]],
  ["BKN","wx","Broken cloud — covering 5 to 7 oktas (more than half the sky)",["Beacon — ground-based navigation transmitter","Braking action Known — confirmed runway friction","Block Negative — ATC clearance refused"]],
  ["FEW","wx","Few cloud — covering only 1 to 2 oktas of the sky",["Final Entry Waypoint on an approach procedure","Fuel Endurance Warning activation threshold","Forward Edge Waypoint — GPS fix at route boundary"]],
  ["SCT","wx","Scattered cloud — covering 3 to 4 oktas (less than half the sky)",["Standard Cruise Track — planned route centreline","Secondary Control Transponder unit","Speed Control Threshold — approach deceleration point"]],
  ["OVC","wx","Overcast — complete 8-okta cloud cover across the entire sky",["Obstacle Vertical Clearance — minimum terrain separation","On-board Voice Communications system","Outbound Vector Change — ATC radar heading instruction"]],
  ["CB","wx","Cumulonimbus — the thunderstorm cloud, always avoid in flight",["Control Boundary — edge of a controlled airspace sector","Compass Bearing — magnetic direction to a fix","Circuit Breaker — electrical protection device in the panel"]],
  ["TCU","wx","Towering Cumulus — large developing storm cloud, a precursor to CB",["Terminal Control Unit — ATC radar approach facility","Transponder Code Update — squawk reassignment","Traffic Conflict Uplink — TCAS resolution advisory"]],
  ["PROB","wx","Probability — the percentage chance of a weather event occurring in a TAF",["Prohibited — designation for restricted airspace","Planned Route of Business — dispatcher scheduling term","Pressure Reading On Board — cabin altitude reference"]],
  ["TEMPO","wx","Temporary — a weather change in a TAF lasting less than one hour at a time",["Temperature Offset — ISA deviation value in degrees","Terminal Point — final fix before the destination","Transponder Emergency Override activation"]],
  ["BECMG","wx","Becoming — a gradual permanent weather change occurring over a stated time period",["Below Cloud — meteorological ceiling descriptor","Beacon Course Management Group — navaid admin body","Braking Efficiency Change — runway condition update"]],
  ["EGMC","nav","ICAO code for Southend Airport — your departure airfield on this flight",["ICAO code for Manchester Airport","ICAO code for East Midlands Airport","ICAO code for London Stansted Airport"]],
  ["EGJJ","nav","ICAO code for Jersey Airport — your destination on this flight",["ICAO code for Guernsey Airport","ICAO code for Isle of Man Airport","ICAO code for Alderney Airport"]],
  ["LFRS","nav","ICAO code for Nantes Atlantique — your designated alternate airport in France",["ICAO code for Paris Charles de Gaulle","ICAO code for Brest Bretagne Airport","ICAO code for Rennes Saint-Jacques Airport"]],
  ["LFRR","airspace","Brest FIR — the French flight information region you enter mid-Channel",["Paris Control — upper airspace authority for central France","Lyon Radar — southern French ATC sector","Bordeaux FIR — southwest French airspace region"]],
  ["EGTT","airspace","London FIR — the UK flight information region covering England and Wales",["London TMA — terminal manoeuvring area around Heathrow","Thames Radar — lower airspace sector identifier","London ATIS — recorded weather broadcast designator"]],
  ["FIR","airspace","Flight Information Region — a defined block of airspace managed by one ATC authority",["Final Instrument Radial — last bearing before a fix","Fuel Indication Reading — cockpit gauge value","Forward ILS Reference — approach intercept point"]],
  ["DET","nav","Detling VOR — the first route fix after departure from Southend, ident 117.30",["Direct Entry Track — how you enter a holding pattern","Descent Entry Time — the point to begin descending","Departure End Threshold — the far end of the runway"]],
  ["LYD","nav","Lydd VOR — the coast-out navigation fix in Kent, ident 114.05",["Lyon Directional beacon in southern France","Lower Yielding Distance — a fuel planning term","Landing Yield Data — aircraft performance calculation"]],
  ["VOR","nav","VHF Omnidirectional Range — ground-based radio navaid that gives you a bearing to or from it",["Vertical Obstacle Reference — charted high terrain marker","Variable Output Radial — GPS computed track label","Verified Overflight Request — diplomatic clearance document"]],
  ["DCT","nav","Direct — fly straight to the next fix with no airway or procedure joining required",["Descent Clearance Time — when ATC clears you to descend","Deferred Crew Transfer — operations scheduling term","Digital Chart Track — GPS moving map display mode"]],
  ["STAR","nav","Standard Terminal Arrival Route — a published arrival procedure into an airfield",["Short Term Altitude Restriction — temporary height limit","Squawk Transponder Acknowledgement Report","Secondary Traffic Advisory Radar system"]],
  ["CDI","nav","Course Deviation Indicator — the needle showing if you are left or right of your planned track",["Cockpit Display Interface — primary flight screen","Controlled Departure Interval — ATC slot timing","Communication Data Input — radio programming port"]],
  ["TOW","perf","Takeoff Weight — the total aircraft weight at the moment of departure",["Top Of Waypoint — where a procedure turn begins","Transponder Output Wattage rating","Traffic Ordering Window — ATC sequence slot"]],
  ["LAW","perf","Landing Weight — the estimated aircraft weight on arrival after burning off fuel",["Low Altitude Warning — GPWS activation threshold","Lateral Advisory Window — RNP corridor limit","Local Aerodrome Weather — alternative term for ATIS"]],
  ["ZFW","perf","Zero Fuel Weight — aircraft weight with everything loaded except fuel",["Zone Flight Warning — restricted area alert","Zenith Fix Waypoint — highest point on a route","Zone of Fixed Weather — stable air mass descriptor"]],
  ["MTOW","perf","Maximum Takeoff Weight — the heaviest the aircraft is certified to depart at (2,150 lbs for the Cherokee)",["Minimum Takeoff Weather — lowest VFR conditions allowed","Max Track Over Water — oceanic route distance limit","Mandatory Transponder Output Wattage requirement"]],
  ["USG","fuel","US Gallons — the volume unit for avgas; the Cherokee 140 holds 50 USG total",["Upper Sector Guard — frequency monitoring service","Unserviceable Ground equipment tag","Universal Signal Generator — ILS test equipment"]],
  ["CONT","fuel","Contingency fuel — the buffer carried for unexpected routing, weather or wind deviations",["Continuous — TAF descriptor for persistent weather","Contact — ATC instruction to call a new frequency","Controlled — the prefix used for controlled airspace"]],
  ["ALTN","fuel","Alternate fuel — the fuel planned to fly to your divert airport if the destination is unusable",["Altitude — generic height reference in a flight plan","Along Track — distance measured on the planned route","Alerting — ATC emergency phase declaration"]],
  ["FINRES","fuel","Final Reserve — the minimum fuel that must remain in the tanks at the point of landing",["Final Restriction — last airspace boundary before destination","Finished Route Segment — the last leg of a flight plan","Frequency In Reserve — standby radio channel"]],
  ["BLOCK","fuel","Block fuel — total fuel loaded before taxi, covering trip, contingency, alternate and reserve",["Block time — the total door-to-door scheduled flight time","Blocked — ATC term for a stepped-on radio transmission","Block altitude — a range of cruise levels approved by ATC"]],
  ["TOC","nav","Top of Climb — the geographic point in the flight where you level off at cruise altitude",["Track Over Course — angular difference from planned route","Time on Course — elapsed flying time since departure fix","Transponder Output Check — pre-flight serviceability test"]],
  ["TOD","nav","Top of Descent — the point where you begin descending toward your destination",["Time of Departure — the wheels-off recorded time","Track Omni Deviation — VOR needle deflection reading","Transponder Off Date — maintenance schedule entry"]],
  ["MORA","nav","Minimum Off-Route Altitude — the lowest safe altitude in an area, including terrain clearance buffer",["Maximum Operational Radar Altitude for ATC coverage","Mandatory Oceanic Reporting Area boundary","Minimum Obstacle Reception Angle for VOR signal"]],
  ["EFOB","fuel","Estimated Fuel On Board — the predicted fuel remaining at each waypoint along the route",["En-route Fix Over a Beacon — position reporting point","Emergency Frequency On Board — 121.5 monitoring note","Extended Final On Base — circuit joining position"]],
  ["TMA","airspace","Terminal Manoeuvring Area — the block of controlled airspace surrounding a busy airport",["Transponder Mandatory Altitude — the level requiring Mode C","Track Made good Average — a navigation accuracy measure","Temporary Movement Area — an apron access restriction"]],
  ["ATC","atc","Air Traffic Control — the ground-based service that manages the separation of aircraft",["Automatic Track Correction — GPS steering function","Aerodrome Traffic Circuit — the standard joining pattern","Altitude Transition Check — pressurisation step"]],
  ["ATIS","atc","Automatic Terminal Information Service — recorded broadcast of weather and runway in use",["Air Traffic Intercept Signal — military scramble term","Airborne Terrain Imaging System","Approach Transition Identification Segment"]],
  ["ICAO","atc","International Civil Aviation Organisation — the UN body that sets global aviation standards",["Integrated Civil Airspace Operations body","International Controller and Airman Organisation","Inter-Continental Aviation Oversight authority"]],
  ["NOTAM","atc","Notice To Airmen — an official notice of any change or hazard that could affect your flight",["Night Operations Traffic and Movement log","Navigation Options Timing and Altitude Memo","Non-standard Operations Tracking and Monitoring"]],
  ["OBS","nav","Omni Bearing Selector — the knob on the GNS 430 or VOR indicator that sets your desired course",["On-Board System — generic avionics reference term","Obstacle — charted high terrain or man-made structure","Outbound Bearing Segment — the departing leg of a hold"]],
  ["UTC","atc","Coordinated Universal Time — the single standard time zone used across all of aviation worldwide",["Upper Track Clearance — cruise flight level approval","Uniform Traffic Code — ICAO transponder standard","Ultra-high frequency Transmission Channel"]],
  ["PBN","nav","Performance Based Navigation — navigation using certified GPS accuracy and integrity standards",["Pilot Briefing Note — pre-flight information document","Primary Beacon Network — VOR and NDB ground infrastructure","Pressure Based Navigation — altimetry system mode"]],
  ["RVSM","atc","Reduced Vertical Separation Minima — permits 1,000ft vertical separation above FL290",["Radar Vector Standard Minimum — ATC lateral spacing rule","Required VHF Squelch Modulation setting","Runway Visual Segment Marker on approach lighting"]],
  ["OAT","wx","Outside Air Temperature — the temperature of the air at your current altitude",["On Approach Track — the final inbound course to a runway","Oceanic Area Transition — the entry point to oceanic airspace","Outbound Approach Track — the departing radial from a VOR"]],
  ["ISA","wx","International Standard Atmosphere — the standard model used for all aircraft performance calculations",["Instrument Separation Altitude — IFR vertical spacing standard","Integrated Situational Awareness — avionics display mode","In-sector Alert — ATC conflict warning system"]],
  ["ETA","nav","Estimated Time of Arrival — your expected time of arrival at the destination",["En-route Track Adjustment — ATC re-route instruction","Emergency Transponder Activation procedure","Elevation Threshold Altitude — approach minimum height"]],
  ["EET","nav","Estimated Elapsed Time — time from departure to reach a specific waypoint or destination",["En-route Entry Time — when you enter controlled airspace","Emergency Equipment Test — pre-flight check item","Extended Endurance Time — maximum fuel duration"]],
  ["W/C","wx","Wind Component — the headwind or tailwind element that directly affects your ground speed",["Weather Check — the pre-flight briefing stage","Weight and Centre of gravity — loading document","Waypoint Confirmation — GPS fix successfully verified"]],
];

function shuffle(a) {
  const arr = [...a];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

let questions = [], current = 0, score = 0, answered = false, results = [];

function makeQuestions() {
  return shuffle(ALL).slice(0, 10).map(([abbr, cat, correct, wrongs]) => ({
    abbr, cat, correct, options: shuffle([correct, ...wrongs])
  }));
}

function init() {
  questions = makeQuestions();
  current = 0; score = 0; answered = false; results = [];
  render();
}

function render() {
  const app = document.getElementById("app");
  if (current >= 10) { renderResults(app); return; }
  const q = questions[current];
  const pct = Math.round((current / 10) * 100);
  const letters = ["A", "B", "C", "D"];
  app.innerHTML = `
    <div class="progress-bg"><div class="progress-fill" style="width:${pct}%"></div></div>
    <div class="meta">
      <span>Question ${current + 1} of 10</span>
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
    <button class="next-btn" onclick="nextQ()">${current < 9 ? "Next question" : "See results"}</button>
  `;
}

function nextQ() { current++; answered = false; render(); }

function renderResults(app) {
  const pct = Math.round((score / 10) * 100);
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
      <div class="results-score">${score}/10</div>
      <div class="results-sub">${pct}% correct</div>
      <div class="results-msg">${msg}</div>
      <div class="breakdown">${rows}</div>
      <button class="restart-btn" onclick="init()">New random quiz</button>
    </div>
  `;
}

init();
</script>
</body>
</html>"""


class QuizHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode("utf-8"))

    def log_message(self, format, *args):
        pass  # suppress console noise


PORT = 8080

def open_browser():
    webbrowser.open(f"http://localhost:{PORT}")

if __name__ == "__main__":
    server = http.server.HTTPServer(("", PORT), QuizHandler)
    print(f"VFR Quiz running at http://localhost:{PORT}")
    print("Press Ctrl+C to stop.\n")
    threading.Timer(1.0, open_browser).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nQuiz server stopped.")

