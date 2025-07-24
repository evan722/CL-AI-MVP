const vid = document.getElementById("vid");
const canvas = document.getElementById("avatarCanvas");
const ctx = canvas.getContext("2d");
const slideInfo = document.getElementById("slideInfo");

let timestamps = [];
let ws = null;
let frameImg = new Image();

// Draw avatar when frame is received
frameImg.onload = () => {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(frameImg, 0, 0, canvas.width, canvas.height);
};

function connectWS(uid) {
  const wsProtocol = location.protocol === "https:" ? "wss" : "ws";
  const wsUrl = `${wsProtocol}://${location.host}/ws/avatar/${uid}`;
  console.log("Connecting WebSocket:", wsUrl);

  if (ws) ws.close();
  ws = new WebSocket(wsUrl);

  ws.onopen = () => console.log("✅ WebSocket connected.");
  ws.onmessage = e => {
    if (!e.data) return;
    frameImg.src = `data:image/jpeg;base64,${e.data}`;
  };
  ws.onerror = err => console.error("WebSocket error:", err);
  ws.onclose = () => console.warn("WebSocket connection closed.");

  vid.onplay = () => ws?.readyState === 1 && ws.send(JSON.stringify({ action: "play" }));
  vid.onpause = () => ws?.readyState === 1 && ws.send(JSON.stringify({ action: "pause" }));
  vid.onseeked = () => ws?.readyState === 1 && ws.send(JSON.stringify({ action: "seek", t: vid.currentTime }));
}

// Update slide info based on timestamp
vid.ontimeupdate = () => {
  if (!timestamps.length) return;
  const t = vid.currentTime;
  let idx = timestamps.findIndex((_, i) => t < (timestamps[i + 1] || Infinity));
  if (idx === -1) idx = timestamps.length - 1;
  slideInfo.textContent = `Slide ${idx + 1}`;
};

// Handle upload
document.getElementById("uploadBtn").onclick = async () => {
  const v = document.getElementById("videoFile").files[0];
  const a = document.getElementById("audioFile").files[0];
  const j = document.getElementById("timeFile").files[0];

  if (!v || !a || !j) {
    alert("Please select all three files.");
    return;
  }

  const fd = new FormData();
  fd.append("video", v);
  fd.append("audio", a);
  fd.append("times", j);

  console.log("📤 Upload button clicked.");
  try {
    const res = await fetch("/upload", { method: "POST", body: fd });
    const data = await res.json();
    const uid = data.id;

    console.log("✅ Upload complete. UID:", uid);
    vid.src = `/uploads/${uid}_video.mp4`;
    vid.load();

    connectWS(uid);

    const jsonText = await j.text();
    timestamps = JSON.parse(jsonText);
  } catch (err) {
    console.error("❌ Upload failed:", err);
    alert("Upload failed. See console.");
  }
};
