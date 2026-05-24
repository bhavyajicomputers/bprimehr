const QUEUE_KEY = "b_prime_hr_queue_v1";
const LOG_KEY = "b_prime_hr_log_v1";
const RUNNING_ACTIVITY_KEY = "b_prime_hr_running_activity";

let pendingActivityAction = null;
let bootstrap = null;

document.addEventListener("DOMContentLoaded", async () => {
    bindEvents();
    updateOnlineStatus();
    renderQueue();
    renderLog();
    await loadBootstrap();

    if ("serviceWorker" in navigator) {
        try {
            await navigator.serviceWorker.register("/assets/b_prime_hr/js/service_worker.js");
        } catch (e) {
            console.warn("Service worker registration failed", e);
        }
    }

    window.addEventListener("online", () => {
        updateOnlineStatus();
        syncQueue();
    });
    window.addEventListener("offline", updateOnlineStatus);
});

function bindEvents() {
    document.querySelectorAll("[data-action]").forEach(btn => {
        btn.addEventListener("click", () => handleAction(btn.dataset.action));
    });

    document.getElementById("syncButton").addEventListener("click", syncQueue);
    document.getElementById("cancelActivity").addEventListener("click", () => {
        pendingActivityAction = null;
        document.getElementById("activityForm").hidden = true;
    });
    document.getElementById("confirmActivity").addEventListener("click", () => {
        captureAndQueue("ACTIVITY_START", {
            activity: document.getElementById("activity").value,
            customer_name: document.getElementById("customerName").value,
            remarks: document.getElementById("remarks").value,
        });
        document.getElementById("activityForm").hidden = true;
    });
}

async function loadBootstrap() {
    try {
        const r = await frappe.call("b_prime_hr.api.get_bootstrap");
        bootstrap = r.message;
        document.getElementById("companyName").textContent = bootstrap.company_name || "Company HR";
        document.getElementById("employeeName").textContent = bootstrap.employee_name || bootstrap.employee || "";
        const initials = (bootstrap.company_name || "Company HR")
            .split(/\s+/)
            .slice(0, 2)
            .map(w => w[0])
            .join("")
            .toUpperCase();
        document.getElementById("brandLogo").textContent = initials || "HR";
    } catch (e) {
        addLog("Bootstrap Failed", "Please login to ERPNext before opening this page.");
    }
}

function handleAction(action) {
    if (action === "ACTIVITY_START") {
        document.getElementById("activityForm").hidden = false;
        return;
    }

    if (action === "ACTIVITY_STOP") {
        const activityName = localStorage.getItem(RUNNING_ACTIVITY_KEY) || "";
        captureAndQueue(action, { activity_name: activityName });
        return;
    }

    captureAndQueue(action, {});
}

function captureAndQueue(action, extra) {
    if (!navigator.geolocation) {
        alert("Location is not supported by this browser/device.");
        return;
    }

    setBusy(true);

    navigator.geolocation.getCurrentPosition(
        pos => {
            const payload = {
                local_id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
                action,
                latitude: pos.coords.latitude,
                longitude: pos.coords.longitude,
                accuracy: pos.coords.accuracy,
                client_time: new Date().toISOString().slice(0, 19).replace("T", " "),
                captured_offline: !navigator.onLine,
                ...extra,
            };

            queueEvent(payload);
            showLastLocation(payload);
            addLog(action, `Captured ${payload.latitude}, ${payload.longitude}. ${navigator.onLine ? "Syncing..." : "Saved offline."}`);

            if (navigator.onLine) {
                syncQueue();
            } else {
                renderQueue();
            }

            setBusy(false);
        },
        err => {
            setBusy(false);
            alert("Could not capture location. Please allow location permission and try again.");
            console.warn(err);
        },
        {
            enableHighAccuracy: true,
            timeout: 20000,
            maximumAge: 0,
        }
    );
}

function queueEvent(payload) {
    const queue = getQueue();
    queue.push(payload);
    localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
    renderQueue();
}

function getQueue() {
    try {
        return JSON.parse(localStorage.getItem(QUEUE_KEY) || "[]");
    } catch {
        return [];
    }
}

function setQueue(queue) {
    localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
    renderQueue();
}

async function syncQueue() {
    if (!navigator.onLine) {
        addLog("Sync Skipped", "Device is offline.");
        return;
    }

    let queue = getQueue();
    if (!queue.length) {
        renderQueue();
        return;
    }

    setBusy(true);
    const remaining = [];

    for (const item of queue) {
        try {
            const r = await frappe.call({
                method: "b_prime_hr.api.sync_event",
                args: { payload: item },
            });

            const msg = r.message || {};
            addLog(`${item.action} Synced`, `Checkin: ${msg.checkin || "-"} Activity: ${msg.activity || "-"}`);

            if (item.action === "ACTIVITY_START" && msg.activity) {
                localStorage.setItem(RUNNING_ACTIVITY_KEY, msg.activity);
            }
            if (item.action === "ACTIVITY_STOP") {
                localStorage.removeItem(RUNNING_ACTIVITY_KEY);
            }
        } catch (e) {
            console.warn("Sync failed", e);
            remaining.push(item);
            addLog(`${item.action} Sync Failed`, "Will retry later.");
        }
    }

    setQueue(remaining);
    setBusy(false);
}

function renderQueue() {
    document.getElementById("pendingCount").textContent = getQueue().length;
}

function updateOnlineStatus() {
    const el = document.getElementById("connectionStatus");
    el.textContent = navigator.onLine ? "Online" : "Offline";
    el.style.color = navigator.onLine ? "#15803d" : "#b91c1c";
}

function showLastLocation(payload) {
    document.getElementById("lastLocation").textContent =
        `${payload.latitude}, ${payload.longitude} | Accuracy: ${Math.round(payload.accuracy || 0)} m | ${payload.client_time}`;
}

function addLog(title, detail) {
    const logs = getLogs();
    logs.unshift({ title, detail, at: new Date().toLocaleString() });
    localStorage.setItem(LOG_KEY, JSON.stringify(logs.slice(0, 20)));
    renderLog();
}

function getLogs() {
    try {
        return JSON.parse(localStorage.getItem(LOG_KEY) || "[]");
    } catch {
        return [];
    }
}

function renderLog() {
    const container = document.getElementById("eventLog");
    const logs = getLogs();
    container.innerHTML = logs.length
        ? logs.map(l => `<div class="event"><strong>${escapeHtml(l.title)}</strong><span>${escapeHtml(l.at)} — ${escapeHtml(l.detail)}</span></div>`).join("")
        : `<p class="small-note">No events yet.</p>`;
}

function setBusy(isBusy) {
    document.querySelectorAll("button").forEach(btn => btn.disabled = isBusy);
}

function escapeHtml(str) {
    return String(str || "").replace(/[&<>"']/g, s => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
    }[s]));
}
