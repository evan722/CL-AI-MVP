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
  ws = new WebSocket(`${wsProtocol}://${location.host}/ws/avatar/${uid}`);
  ws.onmessage = e => {
    if (!e.data) return;
    frameImg.src = `data:image/jpeg;base64,${e.data}`;
  };
  vid.onplay = () => ws.send(JSON.stringify({ action: "play" }));
  vid.onpause = () => ws.send(JSON.stringify({ action: "pause" }));
  vid.onseeked = () => ws.send(JSON.stringify({ action: "seek", t: vid.currentTime }));
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

  const fd = new FormData();
  fd.append("video", v);
  fd.append("audio", a);
  fd.append("times", j);
  const res = await fetch("/upload", { method: "POST", body: fd }).then(r => r.json());
  const uid = res.id;

  vid.src = `/uploads/${uid}_video.mp4`;
  vid.load();
  connectWS(uid);

  timestamps = await j.text().then(JSON.parse);
};
