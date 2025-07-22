const vid = document.getElementById("vid");
const canvas = document.getElementById("avatarCanvas");
const ctx = canvas.getContext("2d");
const slideInfo = document.getElementById("slideInfo");

let timestamps = [];
let ws;
let frameImg = new Image();

frameImg.onload = () => ctx.drawImage(frameImg, 0, 0, canvas.width, canvas.height);

function connectWS(uid) {
  const wsProtocol = location.protocol === "https:" ? "wss" : "ws";
  const wsUrl = `${wsProtocol}://${location.host}/ws/avatar/${uid}`;
  console.log("Connecting WebSocket:", wsUrl);
  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log("WebSocket connected.");
  };

  ws.onclose = () => {
    console.warn("WebSocket connection closed.");
  };

  ws.onerror = (err) => {
    console.error("WebSocket error:", err);
  };

  ws.onmessage = e => {
    if (!e.data) return;
    frameImg.src = `data:image/jpeg;base64,${e.data}`;
  };

  vid.onplay = () => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action: "play" }));
    }
  };

  vid.onpause = () => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action: "pause" }));
    }
  };

  vid.onseeked = () => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action: "seek", t: vid.currentTime }));
    }
  };
}

vid.ontimeupdate = () => {
  if (!timestamps.length) return;
  const t = vid.currentTime;
  let idx = timestamps.findIndex((val, i) => t < (timestamps[i + 1] || Infinity));
  if (idx === -1) idx = timestamps.length - 1;
  slideInfo.textContent = `Slide ${idx + 1}`;
};

document.getElementById("uploadBtn").onclick = async () => {
  const v = document.getElementById("videoFile").files[0];
  const a = document.getElementById("audioFile").files[0];
  const j = document.getElementById("timeFile").files[0];
  if (!v || !a || !j) {
    alert("Select all three files");
    return;
  }

  console.log("Upload button clicked. Sending request...");

  const fd = new FormData();
  fd.append("video", v);
  fd.append("audio", a);
  fd.append("times", j);

  try {
    const res = await fetch("/upload", { method: "POST", body: fd });
    if (!res.ok) throw new Error("Upload failed");
    const data = await res.json();
    const uid = data.id;

    console.log("Upload complete. UID:", uid);

    timestamps = await j.text().then(JSON.parse);
    vid.src = `/uploads/${uid}_video.mp4`;
    vid.load();

    connectWS(uid);
  } catch (err) {
    console.error("Upload or playback error:", err);
    alert("Something went wrong. Check console for details.");
  }
};
