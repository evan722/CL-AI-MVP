const outputVideo = document.getElementById('outputVideo');
const slidesVideo = document.getElementById('slidesVideo');
const slideInfo = document.getElementById('slideInfo');
const avatarFrame = document.getElementById('avatarFrame');
const playPauseBtn = document.getElementById('playPauseBtn');
const backBtn = document.getElementById('backBtn');
const forwardBtn = document.getElementById('forwardBtn');
const chatInput = document.getElementById('chatInput');
const chatBtn = document.getElementById('chatBtn');
const chatAnswer = document.getElementById('chatAnswer');
const chatVideo = document.getElementById('chatVideo');
const uploadBtn = document.getElementById('uploadBtn');

let timestamps = [];
let currentId = null;

function startStreaming() {
  if (!currentId) return;
  const ws = new WebSocket(`ws://${location.host}/ws/avatar/${currentId}`);
  let seenFrame = false;


  ws.onmessage = ev => {
    if (ev.data.startsWith('RESULT::')) {
      outputVideo.src = `/outputs/${ev.data.substring(8)}`;
      outputVideo.style.display = 'block';
      avatarFrame.style.display = 'none';
      outputVideo.play();
    } else {
      if (!seenFrame) {
        avatarFrame.style.display = 'block';
        outputVideo.style.display = 'none';
        seenFrame = true;
      }
      avatarFrame.src = 'data:image/jpeg;base64,' + ev.data;
    }
  };
  ws.onclose = () => {
    if (!seenFrame) {
      outputVideo.style.display = 'block';
      avatarFrame.style.display = 'none';
    }
    console.log('stream closed');
  };

}

async function loadInitial() {
  const params = new URLSearchParams(window.location.search);
  currentId = params.get('id') || 'default';

  outputVideo.src = `/outputs/${currentId}.mp4`;
  slidesVideo.src = `/uploads/${currentId}_slides.mp4`;
  try {
    const res = await fetch(`/uploads/${currentId}_timestamps.json`);
    timestamps = await res.json();
  } catch {
    timestamps = [];
  }

  outputVideo.style.display = 'block';
  avatarFrame.style.display = 'none';
  outputVideo.load();
  slidesVideo.load();
  outputVideo.play().catch(() => {});
  slidesVideo.play().catch(() => {});


  startStreaming();
}

window.addEventListener('load', loadInitial);

playPauseBtn.onclick = () => {
  if (outputVideo.paused) {
    outputVideo.play();
  } else {
    outputVideo.pause();
  }
};

backBtn.onclick = () => {
  const newTime = Math.max(0, outputVideo.currentTime - 5);
  outputVideo.currentTime = newTime;
  slidesVideo.currentTime = newTime;
};

forwardBtn.onclick = () => {
  const dur = isNaN(outputVideo.duration) ? Infinity : outputVideo.duration;
  const newTime = Math.min(dur, outputVideo.currentTime + 5);
  outputVideo.currentTime = newTime;
  slidesVideo.currentTime = newTime;
};

outputVideo.onplay = () => {
  slidesVideo.currentTime = outputVideo.currentTime;
  slidesVideo.play();
  playPauseBtn.textContent = 'Pause';
};

outputVideo.onpause = () => {
  slidesVideo.pause();
  playPauseBtn.textContent = 'Play';
};

outputVideo.ontimeupdate = () => {
  const t = outputVideo.currentTime;
  slidesVideo.currentTime = t;
  if (!timestamps.length) return;
  let idx = timestamps.findIndex((_, i) => t < (timestamps[i + 1] || Infinity));
  if (idx === -1) idx = timestamps.length - 1;
  slideInfo.textContent = `Slide ${idx + 1}`;
};

chatBtn.onclick = async () => {
  if (!currentId || chatBtn.disabled) {
    return;
  }
  const question = chatInput.value.trim();
  if (!question) return;

  chatBtn.disabled = true;
  chatInput.value = '';

  outputVideo.pause();
  slidesVideo.pause();

  const t = outputVideo.currentTime;
  let idx = timestamps.findIndex((_, i) => t < (timestamps[i + 1] || Infinity));
  if (idx === -1) idx = timestamps.length - 1;
  const slideText = (timestamps[idx] && timestamps[idx].text) ? timestamps[idx].text : '';

  const payload = {
    uid: currentId,
    question: question,
    slide_index: idx + 1,
    slide_text: slideText
  };

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Error');
    chatAnswer.textContent = data.answer;
    outputVideo.style.display = 'none';
    chatVideo.src = `/outputs/${data.video}`;
    chatVideo.style.display = 'block';
    chatVideo.play();
    chatVideo.onended = () => {
      chatVideo.style.display = 'none';
      outputVideo.style.display = 'block';
      outputVideo.play();
      chatBtn.disabled = false;
    };
  } catch (err) {
    alert('Chat failed: ' + err.message);
    outputVideo.style.display = 'block';
    outputVideo.play();
    chatBtn.disabled = false;
  }
};

uploadBtn.onclick = () => {
  window.location.href = '/upload';
};


