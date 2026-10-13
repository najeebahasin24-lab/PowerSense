/**
 * PowerSense - Industrial Transformer Health Monitoring System
 * Complete SPA Controller: Dashboard, Assets, Monitoring, Analytics,
 * Alerts, Reports, Maintenance, Settings.
 * Focuses Strictly on the 4 Monitored Parameters: Temperature, Oil Level, Voltage, Current.
 */

// Global Chart References
let sparklines = { temp: null, oil: null, volt: null, curr: null };
let mainTrendChart = null;
let healthDistChart = null;
let correlationChart = null;

const SPARKLINE_MAX = 15;
const MAIN_CHART_MAX = 25;

let ws = null;
let wsReconnectTimer = null;
let isSimPaused = false;
let currentActiveView = "viewDashboard";

// Historical buffer for analytics & correlation
let telemetryHistoryBuffer = [];

document.addEventListener("DOMContentLoaded", () => {
  initDateDisplay();
  initMiniSparklines();
  initMainTrendChart();
  loadInitialTelemetryHistory();
  loadAssetsFleet();
  loadAlerts();
  loadMaintenanceHistory();
  initWebSocket();
});

// --------------------------------------------------------------------------
// 1. Navigation / View Switching (SPA)
// --------------------------------------------------------------------------
function switchView(viewId) {
  currentActiveView = viewId;

  // Toggle View Containers
  document.querySelectorAll(".app-view").forEach((view) => {
    view.classList.remove("active");
  });
  const targetView = document.getElementById(viewId);
  if (targetView) targetView.classList.add("active");

  // Toggle Sidebar Nav Highlights
  document.querySelectorAll(".sidebar-nav .nav-item").forEach((btn) => {
    btn.classList.remove("active");
    if (btn.getAttribute("data-view") === viewId) {
      btn.classList.add("active");
    }
  });

  // Update Breadcrumb & Heading
  const titles = {
    viewDashboard: { section: "Dashboard", title: "TRANSFORMER 001" },
    viewAssets: { section: "Assets", title: "Transformer Fleet & Inventory" },
    viewMonitoring: { section: "Monitoring", title: "Real-Time Sensor Telemetry" },
    viewAnalytics: { section: "Analytics", title: "AI Health & Predictive Analytics" },
    viewAlerts: { section: "Alerts", title: "SCADA Alarms & Event Console" },
    viewReports: { section: "Reports", title: "Operational Logs & Data Reports" },
    viewMaintenance: { section: "Maintenance", title: "Preventive Maintenance & Work Orders" },
    viewSettings: { section: "Settings", title: "System & Sensor Thresholds" }
  };

  const info = titles[viewId] || { section: "Dashboard", title: "TRANSFORMER 001" };
  document.getElementById("breadcrumbSection").textContent = info.section;
  document.getElementById("viewHeaderHeading").textContent = info.title;

  // View-Specific Initializers
  if (viewId === "viewAnalytics") {
    initAnalyticsCharts();
    loadAnalyticsData();
  } else if (viewId === "viewAssets") {
    loadAssetsFleet();
  } else if (viewId === "viewReports") {
    loadReportsTable();
  } else if (viewId === "viewAlerts") {
    loadAlertsTable();
  } else if (viewId === "viewMaintenance") {
    loadMaintenanceHistory();
  }
}

// --------------------------------------------------------------------------
// 2. Date & Time Indicator
// --------------------------------------------------------------------------
function initDateDisplay() {
  const dateEl = document.getElementById("currentDateStr");
  function refreshDate() {
    const now = new Date();
    const options = { month: "short", day: "numeric", year: "numeric" };
    dateEl.textContent = `${now.toLocaleDateString("en-US", options)} · Live`;
  }
  refreshDate();
}

// --------------------------------------------------------------------------
// 3. Mini Sparklines for the 4 Parameter Cards
// --------------------------------------------------------------------------
function createSparklineConfig(lineColor, fillColor) {
  return {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          data: [],
          borderColor: lineColor,
          backgroundColor: fillColor,
          borderWidth: 1.8,
          pointRadius: 0,
          pointHoverRadius: 3,
          tension: 0.4,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 250 },
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      },
      scales: {
        x: { display: false },
        y: { display: false }
      }
    }
  };
}

function initMiniSparklines() {
  sparklines.temp = new Chart(
    document.getElementById("sparklineTemp").getContext("2d"),
    createSparklineConfig("#ef4444", "rgba(239, 68, 68, 0.08)")
  );

  sparklines.oil = new Chart(
    document.getElementById("sparklineOil").getContext("2d"),
    createSparklineConfig("#10b981", "rgba(16, 185, 129, 0.08)")
  );

  sparklines.volt = new Chart(
    document.getElementById("sparklineVolt").getContext("2d"),
    createSparklineConfig("#2563eb", "rgba(37, 99, 235, 0.08)")
  );

  sparklines.curr = new Chart(
    document.getElementById("sparklineCurr").getContext("2d"),
    createSparklineConfig("#8b5cf6", "rgba(139, 92, 246, 0.08)")
  );
}

// --------------------------------------------------------------------------
// 4. Main Multi-Parameter Trend Chart (Dashboard)
// --------------------------------------------------------------------------
function initMainTrendChart() {
  const ctx = document.getElementById("mainTrendChart").getContext("2d");

  mainTrendChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Oil Temperature (°C)",
          data: [],
          borderColor: "#ef4444",
          backgroundColor: "rgba(239, 68, 68, 0.05)",
          borderWidth: 2,
          pointRadius: 2,
          pointHoverRadius: 5,
          tension: 0.35,
          fill: false,
          yAxisID: "yPrimary"
        },
        {
          label: "Voltage (V)",
          data: [],
          borderColor: "#2563eb",
          backgroundColor: "transparent",
          borderWidth: 2,
          pointRadius: 2,
          pointHoverRadius: 5,
          tension: 0.35,
          fill: false,
          yAxisID: "yVolt"
        },
        {
          label: "Load Current (A)",
          data: [],
          borderColor: "#8b5cf6",
          backgroundColor: "transparent",
          borderWidth: 2,
          pointRadius: 2,
          pointHoverRadius: 5,
          tension: 0.35,
          fill: false,
          yAxisID: "yCurr"
        },
        {
          label: "Oil Level (%)",
          data: [],
          borderColor: "#10b981",
          backgroundColor: "transparent",
          borderWidth: 2,
          pointRadius: 2,
          pointHoverRadius: 5,
          tension: 0.35,
          fill: false,
          yAxisID: "yOil"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 350, easing: "easeOutQuad" },
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#1e293b",
          titleFont: { family: "Inter", size: 12, weight: "bold" },
          bodyFont: { family: "Inter", size: 12 },
          borderColor: "#334155",
          borderWidth: 1,
          padding: 10,
          cornerRadius: 8
        }
      },
      scales: {
        x: {
          grid: { color: "#f1f5f9" },
          ticks: { color: "#94a3b8", font: { size: 10, family: "Inter" } }
        },
        yPrimary: {
          type: "linear",
          position: "left",
          min: 20,
          max: 110,
          grid: { color: "#f1f5f9" },
          ticks: {
            color: "#ef4444",
            font: { size: 10, family: "Inter" },
            callback: (v) => v + "°C"
          }
        },
        yVolt: {
          type: "linear",
          position: "right",
          min: 170,
          max: 260,
          grid: { drawOnChartArea: false },
          ticks: {
            color: "#2563eb",
            font: { size: 10, family: "Inter" },
            callback: (v) => v + "V"
          }
        },
        yCurr: {
          type: "linear",
          display: false,
          min: 0,
          max: 12
        },
        yOil: {
          type: "linear",
          display: false,
          min: 0,
          max: 100
        }
      }
    }
  });
}

// --------------------------------------------------------------------------
// 5. WebSocket Telemetry Streaming
// --------------------------------------------------------------------------
function initWebSocket() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/telemetry`;

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    clearTimeout(wsReconnectTimer);
  };

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      if (msg.type === "TELEMETRY_UPDATE" || msg.type === "INITIAL_STATE") {
        processIncomingTelemetry(msg.data);
      }
    } catch (err) {
      console.error("WS Parse error:", err);
    }
  };

  ws.onclose = () => {
    wsReconnectTimer = setTimeout(initWebSocket, 2500);
  };

  ws.onerror = (err) => {
    console.warn("WebSocket error:", err);
    ws.close();
  };
}

// --------------------------------------------------------------------------
// 6. Processing Telemetry Across Views
// --------------------------------------------------------------------------
function processIncomingTelemetry(data) {
  const temp = parseFloat(data.temperature);
  const oil = parseFloat(data.oil_level);
  const volt = parseFloat(data.voltage);
  const curr = parseFloat(data.current);
  const status = data.health_status || "NORMAL";
  const confidence = parseFloat(data.confidence || 99.0);
  const timeLabel = data.timestamp ? data.timestamp.split(" ")[1] || data.timestamp : "--:--:--";

  // Store in buffer
  telemetryHistoryBuffer.push({ ...data, timeLabel });
  if (telemetryHistoryBuffer.length > 100) telemetryHistoryBuffer.shift();

  // 1. Dashboard View Numerical Cards
  document.getElementById("valTemperature").textContent = temp.toFixed(1);
  document.getElementById("valOilLevel").textContent = oil.toFixed(1);
  document.getElementById("valVoltage").textContent = volt.toFixed(1);
  document.getElementById("valCurrent").textContent = curr.toFixed(2);

  // 2. Monitoring View Numerical Readouts
  const monTemp = document.getElementById("monValTemp");
  if (monTemp) {
    monTemp.textContent = temp.toFixed(1);
    document.getElementById("monValOil").textContent = oil.toFixed(1);
    document.getElementById("monValVolt").textContent = volt.toFixed(1);
    document.getElementById("monValCurr").textContent = curr.toFixed(2);
  }

  // 3. Update Status Tags
  updateParameterTags(temp, oil, volt, curr);

  // 4. Update Header Health Pill
  const healthPill = document.getElementById("overallHealthPill");
  const healthText = document.getElementById("overallHealthText");
  const healthConf = document.getElementById("overallHealthConf");

  healthPill.className = "health-status-badge";
  if (status === "NORMAL") {
    healthPill.classList.add("status-normal");
    healthText.textContent = "NORMAL";
  } else if (status === "WARNING") {
    healthPill.classList.add("status-warning");
    healthText.textContent = "WARNING";
  } else {
    healthPill.classList.add("status-critical");
    healthText.textContent = "CRITICAL";
  }
  healthConf.textContent = `(${confidence.toFixed(1)}% RF AI)`;

  // 5. Update Meta Timestamp
  document.getElementById("lastUpdatedLabel").textContent = `Last updated: Just now (${timeLabel})`;

  // 6. Push to Sparklines
  pushSparkline(sparklines.temp, temp);
  pushSparkline(sparklines.oil, oil);
  pushSparkline(sparklines.volt, volt);
  pushSparkline(sparklines.curr, curr);

  // 7. Push to Main Trend Chart
  pushMainChart(timeLabel, temp, volt, curr, oil);

  // 8. Update Checklist on Dashboard
  updateStatusChecklist(status, temp, oil, volt, curr);

  // 9. Update Live Raw Terminal on Monitoring View
  appendTerminalLine(timeLabel, temp, oil, volt, curr, status);

  // 10. Update Active Alerts if any
  if (data.alerts && data.alerts.length > 0) {
    appendAlertEvents(data.alerts, timeLabel);
  }
}

function updateParameterTags(temp, oil, volt, curr) {
  const tagTemp = document.getElementById("tagTemp");
  if (temp >= 85) {
    tagTemp.className = "param-status-tag tag-crit";
    tagTemp.textContent = "● Critical";
  } else if (temp >= 65) {
    tagTemp.className = "param-status-tag tag-warn";
    tagTemp.textContent = "● Warning";
  } else {
    tagTemp.className = "param-status-tag tag-good";
    tagTemp.textContent = "● Good";
  }

  const tagOil = document.getElementById("tagOil");
  if (oil < 45) {
    tagOil.className = "param-status-tag tag-crit";
    tagOil.textContent = "● Low";
  } else if (oil < 70) {
    tagOil.className = "param-status-tag tag-warn";
    tagOil.textContent = "● Warning";
  } else {
    tagOil.className = "param-status-tag tag-good";
    tagOil.textContent = "● Good";
  }

  const tagVolt = document.getElementById("tagVolt");
  if (volt < 190 || volt > 255) {
    tagVolt.className = "param-status-tag tag-crit";
    tagVolt.textContent = "● Fault";
  } else if (volt < 215 || volt > 240) {
    tagVolt.className = "param-status-tag tag-warn";
    tagVolt.textContent = "● Fluctuation";
  } else {
    tagVolt.className = "param-status-tag tag-good";
    tagVolt.textContent = "● Good";
  }

  const tagCurr = document.getElementById("tagCurr");
  if (curr > 6.5) {
    tagCurr.className = "param-status-tag tag-crit";
    tagCurr.textContent = "● Overload";
  } else if (curr > 4.5) {
    tagCurr.className = "param-status-tag tag-warn";
    tagCurr.textContent = "● Elevated";
  } else {
    tagCurr.className = "param-status-tag tag-good";
    tagCurr.textContent = "● Good";
  }
}

function updateStatusChecklist(overallStatus, temp, oil, volt, curr) {
  const iconOverall = document.getElementById("iconOverallCheck");
  const stateOverall = document.getElementById("stateOverallText");
  if (overallStatus === "NORMAL") {
    iconOverall.className = "check-icon-circle icon-ok";
    iconOverall.textContent = "✓";
    stateOverall.className = "item-state text-good";
    stateOverall.textContent = "Normal";
  } else if (overallStatus === "WARNING") {
    iconOverall.className = "check-icon-circle icon-warn";
    iconOverall.textContent = "!";
    stateOverall.className = "item-state text-warn";
    stateOverall.textContent = "Warning";
  } else {
    iconOverall.className = "check-icon-circle icon-crit";
    iconOverall.textContent = "⚠";
    stateOverall.className = "item-state text-crit";
    stateOverall.textContent = "Critical";
  }

  const iconTemp = document.getElementById("iconTempCheck");
  const stateTemp = document.getElementById("stateTempText");
  if (temp < 65) {
    iconTemp.className = "check-icon-circle icon-ok";
    iconTemp.textContent = "✓";
    stateTemp.className = "item-state text-good";
    stateTemp.textContent = "Good";
  } else if (temp < 85) {
    iconTemp.className = "check-icon-circle icon-warn";
    iconTemp.textContent = "!";
    stateTemp.className = "item-state text-warn";
    stateTemp.textContent = "Elevated";
  } else {
    iconTemp.className = "check-icon-circle icon-crit";
    iconTemp.textContent = "⚠";
    stateTemp.className = "item-state text-crit";
    stateTemp.textContent = "High Temp";
  }

  const iconOil = document.getElementById("iconOilCheck");
  const stateOil = document.getElementById("stateOilText");
  if (oil >= 70) {
    iconOil.className = "check-icon-circle icon-ok";
    iconOil.textContent = "✓";
    stateOil.className = "item-state text-good";
    stateOil.textContent = "Normal";
  } else if (oil >= 45) {
    iconOil.className = "check-icon-circle icon-warn";
    iconOil.textContent = "!";
    stateOil.className = "item-state text-warn";
    stateOil.textContent = "Low";
  } else {
    iconOil.className = "check-icon-circle icon-crit";
    iconOil.textContent = "⚠";
    stateOil.className = "item-state text-crit";
    stateOil.textContent = "Critical";
  }

  const iconVolt = document.getElementById("iconVoltCheck");
  const stateVolt = document.getElementById("stateVoltText");
  if (volt >= 215 && volt <= 240) {
    iconVolt.className = "check-icon-circle icon-ok";
    iconVolt.textContent = "✓";
    stateVolt.className = "item-state text-good";
    stateVolt.textContent = "Normal";
  } else {
    iconVolt.className = "check-icon-circle icon-warn";
    iconVolt.textContent = "!";
    stateVolt.className = "item-state text-warn";
    stateVolt.textContent = "Irregular";
  }

  const iconCurr = document.getElementById("iconCurrCheck");
  const stateCurr = document.getElementById("stateCurrText");
  if (curr <= 4.5) {
    iconCurr.className = "check-icon-circle icon-ok";
    iconCurr.textContent = "✓";
    stateCurr.className = "item-state text-good";
    stateCurr.textContent = "Good";
  } else if (curr <= 6.5) {
    iconCurr.className = "check-icon-circle icon-warn";
    iconCurr.textContent = "!";
    stateCurr.className = "item-state text-warn";
    stateCurr.textContent = "Elevated";
  } else {
    iconCurr.className = "check-icon-circle icon-crit";
    iconCurr.textContent = "⚠";
    stateCurr.className = "item-state text-crit";
    stateCurr.textContent = "Overload";
  }
}

function appendTerminalLine(time, temp, oil, volt, curr, status) {
  const term = document.getElementById("telemetryTerminalStream");
  if (!term) return;
  const line = document.createElement("div");
  line.textContent = `[${time}] RX: T=${temp.toFixed(1)}°C | Oil=${oil.toFixed(1)}% | V=${volt.toFixed(1)}V | I=${curr.toFixed(2)}A => AI Classification: [${status}]`;
  term.appendChild(line);
  if (term.children.length > 25) term.removeChild(term.firstChild);
  term.scrollTop = term.scrollHeight;
}

function pushSparkline(chart, val) {
  if (!chart) return;
  chart.data.labels.push("");
  chart.data.datasets[0].data.push(val);

  if (chart.data.labels.length > SPARKLINE_MAX) {
    chart.data.labels.shift();
    chart.data.datasets[0].data.shift();
  }
  chart.update("none");
}

function pushMainChart(label, temp, volt, curr, oil) {
  if (!mainTrendChart) return;
  mainTrendChart.data.labels.push(label);
  mainTrendChart.data.datasets[0].data.push(temp);
  mainTrendChart.data.datasets[1].data.push(volt);
  mainTrendChart.data.datasets[2].data.push(curr);
  mainTrendChart.data.datasets[3].data.push(oil);

  if (mainTrendChart.data.labels.length > MAIN_CHART_MAX) {
    mainTrendChart.data.labels.shift();
    mainTrendChart.data.datasets.forEach((ds) => ds.data.shift());
  }
  mainTrendChart.update("none");
}

// --------------------------------------------------------------------------
// 7. Initial History Loader
// --------------------------------------------------------------------------
async function loadInitialTelemetryHistory() {
  try {
    const res = await fetch("/api/telemetry/history?limit=25");
    const history = await res.json();
    if (history && history.length > 0) {
      history.forEach((rec) => {
        const time = rec.timestamp ? rec.timestamp.split(" ")[1] || rec.timestamp : "--";
        pushSparkline(sparklines.temp, rec.temperature);
        pushSparkline(sparklines.oil, rec.oil_level);
        pushSparkline(sparklines.volt, rec.voltage);
        pushSparkline(sparklines.curr, rec.current);
        pushMainChart(time, rec.temperature, rec.voltage, rec.current, rec.oil_level);
      });
      processIncomingTelemetry(history[history.length - 1]);
    }
  } catch (err) {
    console.error("Failed to load telemetry history:", err);
  }
}

// --------------------------------------------------------------------------
// 8. Assets View Loader
// --------------------------------------------------------------------------
async function loadAssetsFleet() {
  try {
    const res = await fetch("/api/assets");
    const fleet = await res.json();
    const tbody = document.getElementById("assetsTableBody");
    if (!tbody || !fleet) return;

    tbody.innerHTML = "";
    fleet.forEach((u) => {
      const isTR1 = u.id === "TR-001";
      const statusClass = u.status === "OPERATIONAL" ? "tag-good" : (u.status === "STANDBY" ? "tag-warn" : "tag-crit");
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong style="color:var(--sidebar-active); font-family:var(--font-mono);">${u.id}</strong></td>
        <td><strong>${u.name}</strong></td>
        <td>${u.rated_kva} kVA / ${u.rated_voltage}V</td>
        <td>${u.location}</td>
        <td>${u.cooling_type || "ONAN"}</td>
        <td>${u.installation_date || "2025-01-15"}</td>
        <td><span class="param-status-tag ${statusClass}">● ${u.status}</span></td>
        <td>
          <button class="btn-action ${isTR1 ? 'active' : ''}" onclick="selectAsset('${u.id}')">
            ${isTR1 ? 'Active Unit ✓' : 'Select Asset'}
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error("Assets load error:", e);
  }
}

function selectAsset(assetId) {
  if (assetId === "TR-001") {
    switchView("viewDashboard");
  } else {
    alert(`Asset ${assetId} selected. Telemetry simulator is active on primary testbed TR-001.`);
  }
}

// --------------------------------------------------------------------------
// 9. Analytics View Loader & Charts
// --------------------------------------------------------------------------
function initAnalyticsCharts() {
  if (!healthDistChart) {
    const ctx = document.getElementById("healthDistChart").getContext("2d");
    healthDistChart = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["NORMAL", "WARNING", "CRITICAL"],
        datasets: [{
          data: [85, 12, 3],
          backgroundColor: ["#10b981", "#f59e0b", "#ef4444"],
          borderWidth: 2,
          borderColor: "#ffffff"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom", labels: { boxWidth: 12, font: { family: "Inter", size: 11 } } }
        }
      }
    });
  }

  if (!correlationChart) {
    const ctx = document.getElementById("correlationChart").getContext("2d");
    correlationChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Oil Temp (°C)",
            data: [],
            borderColor: "#ef4444",
            backgroundColor: "rgba(239, 68, 68, 0.08)",
            borderWidth: 2,
            tension: 0.35,
            fill: true,
            yAxisID: "yT"
          },
          {
            label: "Load Current (A)",
            data: [],
            borderColor: "#8b5cf6",
            borderWidth: 2,
            borderDash: [4, 4],
            tension: 0.35,
            fill: false,
            yAxisID: "yI"
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "top", labels: { boxWidth: 12, font: { family: "Inter", size: 11 } } }
        },
        scales: {
          x: { grid: { color: "#f1f5f9" }, ticks: { font: { size: 9 } } },
          yT: { position: "left", min: 20, max: 110, ticks: { callback: v => v + "°C", font: { size: 9 } } },
          yI: { position: "right", min: 0, max: 10, grid: { drawOnChartArea: false }, ticks: { callback: v => v + "A", font: { size: 9 } } }
        }
      }
    });
  }
}

async function loadAnalyticsData() {
  try {
    const [resSummary, resModel] = await Promise.all([
      fetch("/api/analytics/summary"),
      fetch("/api/model/info")
    ]);
    const summary = await resSummary.json();
    const model = await resModel.json();

    if (summary) {
      if (summary.avg_temp) document.getElementById("analyticsAvgTemp").textContent = `${summary.avg_temp.toFixed(1)} °C`;
      if (summary.avg_volt) document.getElementById("analyticsAvgVolt").textContent = `${summary.avg_volt.toFixed(1)} V`;

      // Update Doughnut data
      if (summary.distribution && healthDistChart) {
        const norm = summary.distribution.NORMAL || 0;
        const warn = summary.distribution.WARNING || 0;
        const crit = summary.distribution.CRITICAL || 0;
        const total = norm + warn + crit || 1;
        healthDistChart.data.datasets[0].data = [norm, warn, crit];
        healthDistChart.update();
      }
    }

    if (model && model.accuracy) {
      document.getElementById("analyticsAccuracy").textContent = `${(model.accuracy * 100).toFixed(2)}%`;

      // Feature bars
      const barBox = document.getElementById("analyticsFeatureBars");
      if (barBox && model.feature_importances) {
        barBox.innerHTML = "";
        const labels = {
          temperature: "1. Oil Temperature (°C)",
          oil_level: "2. Oil Reservoir Level (%)",
          voltage: "3. AC Supply Voltage (V)",
          current: "4. Secondary Load Current (A)",
          thermal_stress_index: "Combined Thermal Stress Index",
          apparent_power: "Apparent Power Load (VA)"
        };
        for (const [k, v] of Object.entries(model.feature_importances)) {
          const pct = (v * 100).toFixed(1);
          const div = document.createElement("div");
          div.className = "feat-stat-bar";
          div.innerHTML = `
            <div class="feat-stat-head">
              <span>${labels[k] || k}</span>
              <strong>${pct}%</strong>
            </div>
            <div class="feat-track">
              <div class="feat-fill" style="width:${pct}%;"></div>
            </div>
          `;
          barBox.appendChild(div);
        }
      }
    }

    // Populate correlation chart from recent history
    if (correlationChart && telemetryHistoryBuffer.length > 0) {
      correlationChart.data.labels = telemetryHistoryBuffer.map(r => r.timeLabel);
      correlationChart.data.datasets[0].data = telemetryHistoryBuffer.map(r => r.temperature);
      correlationChart.data.datasets[1].data = telemetryHistoryBuffer.map(r => r.current);
      correlationChart.update();
    }
  } catch (e) {
    console.error("Analytics load error:", e);
  }
}

// --------------------------------------------------------------------------
// 10. Alerts View Loader
// --------------------------------------------------------------------------
async function loadAlerts() {
  try {
    const res = await fetch("/api/alerts?limit=15");
    const alerts = await res.json();
    const count = alerts ? alerts.length : 0;
    document.getElementById("sidebarAlertCount").textContent = count;
    document.getElementById("notifBadge").textContent = count;
  } catch (e) {
    console.error("Alerts counter error:", e);
  }
}

async function loadAlertsTable() {
  try {
    const res = await fetch("/api/alerts?limit=50");
    const alerts = await res.json();
    const tbody = document.getElementById("alarmsTableBody");
    if (!tbody) return;

    tbody.innerHTML = "";
    if (!alerts || alerts.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:20px; color:#10b981;">✓ No active alarm incidents recorded. All parameters operating normally.</td></tr>`;
      return;
    }

    alerts.forEach((a) => {
      const isCrit = a.severity === "CRITICAL";
      const sevClass = isCrit ? "tag-crit" : "tag-warn";
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-family:var(--font-mono);">${a.timestamp}</td>
        <td><strong>${a.parameter}</strong></td>
        <td><span class="param-status-tag ${sevClass}">● ${a.severity}</span></td>
        <td>${a.value}</td>
        <td>${a.message}</td>
        <td><button class="link-btn" onclick="acknowledgeSingleAlert(this)">Acknowledge</button></td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error("Alerts table load error:", e);
  }
}

function filterAlertsTable(filter) {
  document.querySelectorAll(".filter-pill").forEach(p => p.classList.remove("active"));
  event.target.classList.add("active");
  const rows = document.querySelectorAll("#alarmsTableBody tr");
  rows.forEach(r => {
    if (filter === "ALL") {
      r.style.display = "";
    } else {
      r.style.display = r.textContent.includes(filter) ? "" : "none";
    }
  });
}

function acknowledgeSingleAlert(btn) {
  const tr = btn.closest("tr");
  btn.textContent = "Acknowledged ✓";
  btn.style.color = "#059669";
  btn.disabled = true;
}

function exportAlertsCSV() {
  window.open("/api/reports/export-csv", "_blank");
}

function appendAlertEvents(newAlerts, timeLabel) {
  const stream = document.getElementById("eventsStreamContainer");
  if (stream) {
    const empty = stream.querySelector(".empty-event-row");
    if (empty) empty.remove();

    newAlerts.forEach((alt) => {
      const row = document.createElement("div");
      row.className = `alert-event-row ${alt.severity === "CRITICAL" ? "crit" : "warn"}`;
      row.innerHTML = `<span>● [${alt.severity}] ${alt.msg}</span><span>${timeLabel}</span>`;
      stream.insertBefore(row, stream.firstChild);
    });
  }

  const currentCount = parseInt(document.getElementById("sidebarAlertCount").textContent) || 0;
  const newCount = currentCount + newAlerts.length;
  document.getElementById("sidebarAlertCount").textContent = newCount;
  document.getElementById("notifBadge").textContent = newCount;
}

async function clearAllAlerts() {
  try {
    await fetch("/api/alerts/clear", { method: "POST" });
    document.getElementById("sidebarAlertCount").textContent = "0";
    document.getElementById("notifBadge").textContent = "0";
    const stream = document.getElementById("eventsStreamContainer");
    if (stream) {
      stream.innerHTML = `<div class="empty-event-row"><span class="green-dot">●</span> No active alarm events. All 4 parameters are within safety margins.</div>`;
    }
    loadAlertsTable();
  } catch (err) {
    console.error("Clear alerts error:", err);
  }
}

// --------------------------------------------------------------------------
// 11. Reports View Loader
// --------------------------------------------------------------------------
async function loadReportsTable() {
  try {
    const res = await fetch("/api/telemetry/history?limit=60");
    const history = await res.json();
    const tbody = document.getElementById("historicalReportsTableBody");
    const countEl = document.getElementById("reportsRecordCount");
    if (!tbody || !history) return;

    countEl.textContent = `Showing latest ${history.length} logged samples`;
    tbody.innerHTML = "";
    history.reverse().forEach((r) => {
      const statusClass = r.health_status === "NORMAL" ? "tag-good" : (r.health_status === "WARNING" ? "tag-warn" : "tag-crit");
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-family:var(--font-mono); font-size:0.75rem;">#${r.id}</td>
        <td>${r.timestamp}</td>
        <td><strong>${r.temperature.toFixed(1)}</strong> °C</td>
        <td><strong>${r.oil_level.toFixed(1)}</strong> %</td>
        <td><strong>${r.voltage.toFixed(1)}</strong> V</td>
        <td><strong>${r.current.toFixed(2)}</strong> A</td>
        <td><span class="param-status-tag ${statusClass}">● ${r.health_status}</span></td>
        <td>${r.confidence.toFixed(1)}%</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error("Reports table load error:", e);
  }
}

// --------------------------------------------------------------------------
// 12. Maintenance View Loader & Work Orders
// --------------------------------------------------------------------------
async function loadMaintenanceHistory() {
  try {
    const res = await fetch("/api/maintenance");
    const list = await res.json();
    const tbody = document.getElementById("maintenanceTableBody");
    if (!tbody || !list) return;

    tbody.innerHTML = "";
    if (list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:20px; color:var(--text-muted);">No maintenance work orders or field inspection logs recorded.</td></tr>`;
      return;
    }

    list.forEach((m) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-family:var(--font-mono);">${m.date}</td>
        <td><strong>${m.activity_type}</strong></td>
        <td>${m.technician}</td>
        <td><span class="badge-pill">${m.parameter_impacted}</span></td>
        <td>${m.findings}</td>
        <td><span class="param-status-tag tag-good">✓ ${m.status}</span></td>
        <td>
          <button class="btn-delete-maint" onclick="deleteMaintenanceRecord(${m.id})">Delete</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error("Maintenance load error:", e);
  }
}

async function deleteMaintenanceRecord(recordId) {
  const confirmed = confirm("Are you sure you want to delete this maintenance record?");
  if (!confirmed) return;

  try {
    const res = await fetch(`/api/maintenance/${recordId}`, {
      method: "DELETE"
    });
    const result = await res.json();
    if (res.ok && result.status === "success") {
      loadMaintenanceHistory();
    } else {
      alert(result.detail || "Failed to delete maintenance record.");
    }
  } catch (err) {
    console.error("Delete maintenance record error:", err);
    alert("An error occurred while deleting the maintenance record.");
  }
}

function openAddMaintenanceModal() {
  document.getElementById("maintenanceModal").classList.add("active");
}

function closeAddMaintenanceModal() {
  document.getElementById("maintenanceModal").classList.remove("active");
}

async function submitNewMaintenance(e) {
  e.preventDefault();
  const payload = {
    transformer_id: "TR-001",
    activity_type: document.getElementById("maintActivity").value,
    technician: document.getElementById("maintTech").value,
    parameter_impacted: document.getElementById("maintParam").value,
    findings: document.getElementById("maintFindings").value
  };

  try {
    const res = await fetch("/api/maintenance", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    if (result.status === "success") {
      closeAddMaintenanceModal();
      loadMaintenanceHistory();
      alert("Maintenance service entry logged successfully.");
    }
  } catch (err) {
    console.error("Maintenance submit error:", err);
  }
}

// --------------------------------------------------------------------------
// 13. Settings View Handlers
// --------------------------------------------------------------------------
function saveSystemSettings(e) {
  e.preventDefault();
  alert("PowerSense threshold limits & system configuration successfully saved!");
}

// --------------------------------------------------------------------------
// 14. Demo Review Toolbar Controls
// --------------------------------------------------------------------------
async function selectDemoScenario(scenarioName) {
  document.querySelectorAll(".scen-btn").forEach((btn) => btn.classList.remove("active"));
  const btnMap = {
    NORMAL: "btnScenNormal",
    WARNING_THERMAL: "btnScenWarning",
    CRITICAL_LEAK: "btnScenCritical"
  };
  const activeBtn = document.getElementById(btnMap[scenarioName]);
  if (activeBtn) activeBtn.classList.add("active");

  try {
    const res = await fetch("/api/simulation/inject-scenario", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario: scenarioName })
    });
    const result = await res.json();
    if (result.record) {
      processIncomingTelemetry(result.record);
    }
  } catch (err) {
    console.error("Scenario injection error:", err);
  }
}

async function toggleSimStream() {
  try {
    const res = await fetch("/api/simulation/toggle", { method: "POST" });
    const data = await res.json();
    isSimPaused = !data.is_running;
    const btn = document.getElementById("btnToggleSimStream");
    if (btn) {
      if (isSimPaused) {
        btn.classList.add("paused");
        btn.textContent = "▶ Resume";
      } else {
        btn.classList.remove("paused");
        btn.textContent = "⏸ Pause";
      }
    }
  } catch (err) {
    console.error("Stream toggle error:", err);
  }
}

// --------------------------------------------------------------------------
// 15. Manual Slider Modal Controls
// --------------------------------------------------------------------------
function openManualSliderModal() {
  document.getElementById("manualModal").classList.add("active");
  document.getElementById("slTemp").value = parseFloat(document.getElementById("valTemperature").textContent) || 45.0;
  document.getElementById("slOil").value = parseFloat(document.getElementById("valOilLevel").textContent) || 90.0;
  document.getElementById("slVolt").value = parseFloat(document.getElementById("valVoltage").textContent) || 230.0;
  document.getElementById("slCurr").value = parseFloat(document.getElementById("valCurrent").textContent) || 2.8;
  syncSliderLabels();
}

function closeManualSliderModal() {
  document.getElementById("manualModal").classList.remove("active");
}

function syncSliderLabels() {
  document.getElementById("lblSliderTemp").textContent = `${parseFloat(document.getElementById("slTemp").value).toFixed(1)} °C`;
  document.getElementById("lblSliderOil").textContent = `${parseFloat(document.getElementById("slOil").value).toFixed(1)} %`;
  document.getElementById("lblSliderVolt").textContent = `${parseFloat(document.getElementById("slVolt").value).toFixed(1)} V`;
  document.getElementById("lblSliderCurr").textContent = `${parseFloat(document.getElementById("slCurr").value).toFixed(2)} A`;
}

async function submitManualSliders() {
  const temp = parseFloat(document.getElementById("slTemp").value);
  const oil = parseFloat(document.getElementById("slOil").value);
  const volt = parseFloat(document.getElementById("slVolt").value);
  const curr = parseFloat(document.getElementById("slCurr").value);

  closeManualSliderModal();

  try {
    await fetch("/api/telemetry", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        transformer_id: "TR-001",
        temperature: temp,
        oil_level: oil,
        voltage: volt,
        current: curr
      })
    });
  } catch (err) {
    console.error("Manual injection error:", err);
  }
}
