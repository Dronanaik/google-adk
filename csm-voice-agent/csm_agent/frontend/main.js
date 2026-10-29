// csm-voice-agent — Live Customer Service Management client.
// Built on the exact WebSocket + 16kHz AudioWorklet + 24kHz PCM playback + barge-in
// architecture of `live-dj/adk_tools/frontend/main.js`, adapted for Customer & Order
// Lookup, Order Support Actions, and the CSM Policy Gate.

const $ = (id) => document.getElementById(id);
const orb = $("orb"), statusEl = $("status"), bannerEl = $("banner"), txEl = $("transcript");
const actEl = $("actionlog"), custCard = $("customer-card"), orderCard = $("order-card");
const policyPill = $("policy-pill");

if (new URLSearchParams(location.search).get("log") === "0") {
  document.querySelector(".actions").style.display = "none";
}

const BARGE_RMS = 0.02;
let ws, audioCtx, workletNode, micStream;
let nextStart = 0;
let activeSources = [];
let speaking = false;
let actionLogCleared = false;

function setOrb(state) { orb.className = "orb " + state; } // idle | listening | thinking | speaking
function setStatus(t) { statusEl.textContent = t; }
function setBanner(t, blocked = false) {
  bannerEl.textContent = t || "";
  bannerEl.className = "banner" + (blocked ? " blocked" : "");
}

function addLine(role, text) {
  const p = document.createElement("div");
  p.className = "line " + role;
  p.textContent = (role === "aria" ? "aria  " : "you   ") + text;
  txEl.appendChild(p);
  txEl.scrollTop = txEl.scrollHeight;
}

// ---------- Customer & Order Inspector rendering ----------
function renderCustomer(cust, orders = []) {
  if (!cust) return;
  const verBadge = cust.verified
    ? `<span class="badge verified">PIN verified</span>`
    : `<span class="badge">${cust.tier}</span>`;
  const orderIds = orders.map((o) => `${o.order_id} (${o.status})`).join(", ") || (cust.orders || []).join(", ");
  custCard.innerHTML = `
    <div class="card-header">
      <span class="card-title">${cust.name} · ${cust.customer_id}</span>
      ${verBadge}
    </div>
    <div class="meta-row"><span>Email</span><span class="val">${cust.email}</span></div>
    <div class="meta-row"><span>Phone / PIN</span><span class="val">${cust.phone} (PIN: ${cust.pin || "****"})</span></div>
    <div class="meta-row"><span>Account Status</span><span class="val">${cust.account_status}</span></div>
    <div class="meta-row"><span>Orders</span><span class="val">${orderIds}</span></div>
  `;
}

function renderOrder(order, lastTicket = null, escalation = null) {
  if (!order) return;
  const itemsHtml = (order.items || [])
    .map((i) => `<div>• ${i.qty}× ${i.name} — $${Number(i.price).toFixed(2)}</div>`)
    .join("");
  const extraBanner = [];
  if (order.refund_amount) {
    extraBanner.push(`<div class="meta-row"><span>Refund Issued</span><span class="val">$${Number(order.refund_amount).toFixed(2)} (${order.refund_reason || ""})</span></div>`);
  }
  if (lastTicket && lastTicket.order_id === order.order_id) {
    extraBanner.push(`<div class="meta-row"><span>Ticket Created</span><span class="val">${lastTicket.ticket_id} · ${lastTicket.priority}</span></div>`);
  }
  if (escalation && escalation.order_id === order.order_id) {
    extraBanner.push(`<div class="meta-row"><span>Escalation</span><span class="val">${escalation.escalation_id} → ${escalation.department}</span></div>`);
  }

  orderCard.innerHTML = `
    <div class="card-header">
      <span class="card-title">${order.order_id} · $${Number(order.total).toFixed(2)}</span>
      <span class="badge ${order.status}">${order.status.replace("_", " ")}</span>
    </div>
    <div class="meta-row"><span>Customer</span><span class="val">${order.customer_name} (${order.customer_id})</span></div>
    <div class="meta-row"><span>Carrier / ETA</span><span class="val">${order.carrier} · ${order.eta}</span></div>
    <div class="meta-row"><span>Tracking</span><span class="val">${order.tracking_number}</span></div>
    <div class="meta-row"><span>Ship To</span><span class="val">${order.shipping_address}</span></div>
    ${extraBanner.join("")}
    <div class="items-list">${itemsHtml}</div>
  `;
}

function handleCsmState(m) {
  const snap = m.snapshot || {};
  if (snap.active_customer) {
    renderCustomer(snap.active_customer, snap.customer_orders || []);
  }
  if (snap.active_order) {
    renderOrder(snap.active_order, snap.last_ticket, snap.escalation);
  }
  if (m.action === "lookup_customer" && snap.active_customer) {
    setBanner(`✓ Loaded customer ${snap.active_customer.name} (${snap.active_customer.customer_id})`);
  } else if (m.action === "lookup_order" && snap.active_order) {
    setBanner(`✓ Loaded order ${snap.active_order.order_id} (${snap.active_order.status})`);
  } else if (m.action === "verify_customer_pin" && snap.active_customer) {
    setBanner(
      snap.active_customer.verified
        ? `✓ Security PIN verified for ${snap.active_customer.name}`
        : `⛔ Invalid PIN provided`,
      !snap.active_customer.verified
    );
  } else if (m.action === "issue_refund" && snap.active_order) {
    setBanner(`✓ Refunded $${Number(snap.active_order.refund_amount || m.amount).toFixed(2)} on ${snap.active_order.order_id}`);
  } else if (m.action === "update_shipping_address" && snap.active_order) {
    setBanner(`✓ Updated shipping address on ${snap.active_order.order_id}`);
  } else if (m.action === "create_support_ticket" && snap.last_ticket) {
    setBanner(`✓ Created ticket ${snap.last_ticket.ticket_id} (${snap.last_ticket.priority})`);
  } else if (m.action === "escalate_to_human" && snap.escalation) {
    setBanner(`✓ Escalated (${snap.escalation.escalation_id}) to ${snap.escalation.department}`);
  } else if (m.action === "blocked") {
    setBanner(`⛔ Policy Gate blocked ${m.tool}: ${m.reason}`, true);
  }
}

// ---------- Policy Gate Action Log ----------
function addAction(m) {
  if (!actionLogCleared) {
    actEl.innerHTML = "";
    actionLogCleared = true;
  }
  const div = document.createElement("div");
  div.className = "act" + (m.status === "blocked" ? " blocked" : "");
  const args = Object.entries(m.args || {})
    .map(([k, v]) => `${k}: ${JSON.stringify(v)}`)
    .join(", ");
  const call = document.createElement("div");
  call.textContent = `▸ ${m.tool}(${args})`;
  const verdict = document.createElement("span");
  verdict.className = "verdict";
  verdict.textContent = m.status === "blocked" ? `⛔ blocked · ${m.reason || ""}` : "✓ allowed";
  div.appendChild(call);
  div.appendChild(verdict);
  actEl.appendChild(div);
  actEl.scrollTop = actEl.scrollHeight;
}

// ---------- Voice playback (24 kHz PCM from the server) ----------
function ensureAudioContext() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (audioCtx.state === "suspended") {
    audioCtx.resume().catch(() => {});
  }
}

function playVoice(buf) {
  ensureAudioContext();
  const int16 = new Int16Array(buf);
  const f32 = new Float32Array(int16.length);
  for (let i = 0; i < int16.length; i++) f32[i] = int16[i] / 0x8000;
  const ab = audioCtx.createBuffer(1, f32.length, 24000);
  ab.getChannelData(0).set(f32);
  const src = audioCtx.createBufferSource();
  src.buffer = ab;
  src.connect(audioCtx.destination);
  const now = audioCtx.currentTime;
  if (nextStart < now) nextStart = now;
  src.start(nextStart);
  nextStart += ab.duration;
  activeSources.push(src);
  src.onended = () => {
    activeSources = activeSources.filter((s) => s !== src);
    if (!activeSources.length) {
      speaking = false;
      setOrb("listening");
    }
  };
  speaking = true;
  setOrb("speaking");
}

function stopVoice() {
  activeSources.forEach((s) => {
    try { s.stop(); } catch {}
  });
  activeSources = [];
  nextStart = 0;
  speaking = false;
  setOrb("listening");
}

// ---------- Live WebSocket connection ----------
function connect() {
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    return;
  }
  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${proto}://${location.host}/ws`);
  ws.binaryType = "arraybuffer";
  ws.onopen = () => {
    setStatus("connected · listening for customer…");
    setOrb("listening");
  };
  ws.onclose = () => {
    setStatus("line disconnected — tap 🎙 talk or send a message to reconnect");
    setOrb("idle");
    $("talk").disabled = false;
    $("talk").textContent = "🎙 talk";
  };
  ws.onmessage = (evt) => {
    if (typeof evt.data !== "string") {
      playVoice(evt.data);
      return;
    }
    const m = JSON.parse(evt.data);
    if (m.type === "transcript") {
      if (m.role === "user") setOrb("thinking");
      addLine(m.role, m.text);
    } else if (m.type === "csm_state") {
      handleCsmState(m);
    } else if (m.type === "action") {
      addAction(m);
    } else if (m.type === "interrupted") {
      stopVoice();
    } else if (m.type === "error") {
      setStatus("error: " + m.message);
      console.error(m.message);
    }
  };
}

async function startMic() {
  ensureAudioContext();
  await audioCtx.audioWorklet.addModule("/pcm-processor.js");
  micStream = await navigator.mediaDevices.getUserMedia({
    audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true, autoGainControl: true },
  });
  const source = audioCtx.createMediaStreamSource(micStream);
  workletNode = new AudioWorkletNode(audioCtx, "pcm-processor");
  workletNode.port.onmessage = (e) => {
    if (ws && ws.readyState === WebSocket.OPEN) ws.send(e.data.pcm);
    if (e.data.rms >= BARGE_RMS && speaking) stopVoice(); // client-side barge-in
  };
  source.connect(workletNode);
  workletNode.connect(audioCtx.destination);
}

async function go() {
  $("talk").disabled = true;
  setStatus("connecting to aria…");
  setOrb("thinking");
  try {
    await startMic();
  } catch (err) {
    console.warn("Microphone unavailable or denied; continuing with text + audio output mode:", err);
  }
  connect();
  $("talk").textContent = "● live";
}

function sendTextPrompt(text) {
  if (!text || !text.trim()) return;
  ensureAudioContext();
  stopVoice();
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    connect();
    setTimeout(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "text", text: text.trim() }));
      }
    }, 600);
  } else {
    ws.send(JSON.stringify({ type: "text", text: text.trim() }));
  }
}

$("talk").addEventListener("click", go);

$("text-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const input = $("text-input");
  if (input.value.trim()) {
    sendTextPrompt(input.value.trim());
    input.value = "";
  }
});

document.querySelectorAll(".sample-chip").forEach((btn) => {
  btn.addEventListener("click", () => {
    const prompt = btn.getAttribute("data-prompt");
    sendTextPrompt(prompt);
  });
});

$("reset-btn").addEventListener("click", async () => {
  try {
    const res = await fetch("/api/reset", { method: "POST" });
    const data = await res.json();
    setBanner("↺ Demo store reset to initial state");
    if (data.snapshot && data.snapshot.all_customers && data.snapshot.all_customers[0]) {
      renderCustomer(data.snapshot.all_customers[0], data.snapshot.all_orders.slice(0, 2));
      renderOrder(data.snapshot.all_orders[0]);
    }
  } catch (e) {
    console.error("Failed to reset store:", e);
  }
});

// Load initial state preview on page open
(async function initPreview() {
  try {
    const res = await fetch("/api/state");
    const data = await res.json();
    if (data.policy) {
      policyPill.textContent = `policy gate · max auto-refund $${data.policy.max_auto_refund}`;
    }
    const snap = data.snapshot || {};
    if (snap.all_customers && snap.all_customers[0]) {
      renderCustomer(snap.all_customers[0], snap.all_orders.filter((o) => o.customer_id === "CUST-101"));
    }
    if (snap.all_orders && snap.all_orders[0]) {
      renderOrder(snap.all_orders[0]);
    }
  } catch {}
})();

