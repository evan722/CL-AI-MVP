const outputVideo = document.getElementById('outputVideo');
const slidesVideo = document.getElementById('slidesVideo');
const slideInfo = document.getElementById('slideInfo');
const avatarFrame = document.getElementById('avatarFrame');

let timestamps = [];
let currentId = null;

document.getElementById('uploadBtn').onclick = async () => {
  const videoFile = document.getElementById('videoFile').files[0];
  const audioFile = document.getElementById('audioFile').files[0];
  const timeFile = document.getElementById('timeFile').files[0];
  const avatarFile = document.getElementById('avatarFile').files[0];

  if (!videoFile || !audioFile || !timeFile || !avatarFile) {
    alert('Please select slides, audio, timestamps and avatar files.');
    return;
  }

  const formData = new FormData();
  formData.append('video', videoFile);
  formData.append('audio', audioFile);
  formData.append('timestamps', timeFile);
  formData.append('avatar', avatarFile);

  try {
    const res = await fetch('/upload', { method: 'POST', body: formData });
    if (!res.ok) {
      const t = await res.text();
      throw new Error(`Upload failed: ${res.status} - ${t}`);
    }
    const data = await res.json();
    if (!data.output_video || !data.slides_video) {
      throw new Error('Server did not return expected file paths');
    }

    currentId = data.id;
    outputVideo.src = `/outputs/${data.output_video}`;
    slidesVideo.src = `/uploads/${data.slides_video}`;
    const jsonText = await timeFile.text();
    timestamps = JSON.parse(jsonText);
    outputVideo.style.display = 'block';
    avatarFrame.style.display = 'none';
    outputVideo.load();
    slidesVideo.load();
  } catch (err) {
    console.error('Upload error:', err);
    alert('Failed to generate video. Check server logs.');
  }
};

outputVideo.onplay = () => {
  slidesVideo.currentTime = outputVideo.currentTime;
  slidesVideo.play();
};

outputVideo.onpause = () => {
  slidesVideo.pause();
};

outputVideo.ontimeupdate = () => {
  const t = outputVideo.currentTime;
  slidesVideo.currentTime = t;
  if (!timestamps.length) return;
  let idx = timestamps.findIndex((_, i) => t < (timestamps[i + 1] || Infinity));
  if (idx === -1) idx = timestamps.length - 1;
  slideInfo.textContent = `Slide ${idx + 1}`;
};

document.getElementById('streamBtn').onclick = () => {
  if (!currentId) {
    alert('Upload files first.');
    return;
  }
  const ws = new WebSocket(`ws://${location.host}/ws/avatar/${currentId}`);
  avatarFrame.style.display = 'block';
  outputVideo.style.display = 'none';

  ws.onmessage = ev => {
    if (ev.data.startsWith('RESULT::')) {
      outputVideo.src = `/outputs/${ev.data.substring(8)}`;
      outputVideo.style.display = 'block';
      avatarFrame.style.display = 'none';
      outputVideo.play();
    } else {
      avatarFrame.src = 'data:image/jpeg;base64,' + ev.data;
    }
  };
  ws.onclose = () => console.log('stream closed');
};
