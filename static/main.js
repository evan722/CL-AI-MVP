const outputVideo = document.getElementById('outputVideo');
const slideImg = document.getElementById('slideImg');
const slideInfo = document.getElementById('slideInfo');
const avatarFrame = document.getElementById('avatarFrame');
const playPauseBtn = document.getElementById('playPauseBtn');
const prevSlideBtn = document.getElementById('prevSlide');
const nextSlideBtn = document.getElementById('nextSlide');
const chatInput = document.getElementById('chatInput');
const chatBtn = document.getElementById('chatBtn');
const chatAnswer = document.getElementById('chatAnswer');
const chatVideo = document.getElementById('chatVideo');
const uploadBtn = document.getElementById('uploadBtn');

let timestamps = [];
let slides = [];
let slideIndex = 0;
let segmentEnd = null;
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

async function loadSlides(presentationId) {
  try {
    const apiKey = window.GOOGLE_API_KEY || '';
    const presResp = await fetch(`https://slides.googleapis.com/v1/presentations/${presentationId}?key=${apiKey}`);
    const pres = await presResp.json();
    const pages = pres.slides || [];
    slides = await Promise.all(pages.map(async s => {
      let thumb = '';
      try {
        const tResp = await fetch(`https://slides.googleapis.com/v1/presentations/${presentationId}/pages/${s.objectId}/thumbnail?key=${apiKey}&thumbnailProperties.thumbnailSize=LARGE`);
        const tData = await tResp.json();
        thumb = tData.contentUrl;
      } catch {}
      let text = '';
      if (s.pageElements) {
        text = s.pageElements.map(pe => {
          try {
            return pe.shape && pe.shape.text && pe.shape.text.textElements
              .map(te => te.textRun ? te.textRun.content : '')
              .join('');
          } catch { return ''; }
        }).join(' ');
      }
      return {thumb, text};
    }));
  } catch (err) {
    console.error('Failed to load slides', err);
    slides = [];
  }
  return slides.length > 0;
}

async function loadLocalSlides(id) {
  slides = [];
  for (let i = 1; i < 100; i++) {
    const url = `/uploads/${id}_slide_${i}.png`;
    try {
      const resp = await fetch(url);
      if (!resp.ok) break;
      slides.push({thumb: url, text: ''});
    } catch {
      break;
    }
  }
  return slides.length > 0;
}

function showSlide(idx) {
  if (!slides.length) return;
  slideIndex = idx;
  slideImg.src = slides[idx].thumb;
  slideInfo.textContent = `Slide ${idx + 1}`;
  const start = timestamps[idx] || 0;
  const end = timestamps[idx + 1] || outputVideo.duration || Infinity;
  segmentEnd = end;
  outputVideo.currentTime = start;
  outputVideo.play().catch(()=>{});
  playPauseBtn.textContent = 'Pause';
}

async function loadInitial() {
  const params = new URLSearchParams(window.location.search);
  currentId = params.get('id') || 'default';

  outputVideo.src = `/outputs/${currentId}.mp4`;
  try {
    const res = await fetch(`/uploads/${currentId}_timestamps.json`);
    timestamps = await res.json();
  } catch {
    timestamps = [];
  }
  let slidesId = '';
  try {
    slidesId = await (await fetch(`/uploads/${currentId}_slides_id.txt`)).text();
    slidesId = slidesId.trim();
  } catch {}
  let loaded = false;
  if (slidesId && slidesId !== 'presentation-id-placeholder') {
    loaded = await loadSlides(slidesId);
  }
  if (!loaded) {
    await loadLocalSlides(currentId);

  }
  outputVideo.style.display = 'block';
  avatarFrame.style.display = 'none';
  outputVideo.load();
  outputVideo.onloadedmetadata = () => {
    if (slides.length) {
      showSlide(0);
    }
  };
  startStreaming();
}

window.addEventListener('load', loadInitial);


playPauseBtn.onclick = () => {
  if (outputVideo.paused) {
    const end = timestamps[slideIndex + 1] || outputVideo.duration || Infinity;
    segmentEnd = end;
    outputVideo.play();
    playPauseBtn.textContent = 'Pause';
  } else {
    outputVideo.pause();
    playPauseBtn.textContent = 'Play';
  }
};

prevSlideBtn.onclick = () => {
  if (slideIndex > 0) {
    showSlide(slideIndex - 1);
  }
};

nextSlideBtn.onclick = () => {
  if (slideIndex < slides.length - 1) {
    showSlide(slideIndex + 1);
  }
};


outputVideo.ontimeupdate = () => {
  if (segmentEnd !== null && outputVideo.currentTime >= segmentEnd) {
    outputVideo.pause();
    playPauseBtn.textContent = 'Play';
    segmentEnd = null;
  }

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

  const slideText = slides[slideIndex] ? slides[slideIndex].text : '';
  const payload = {
    uid: currentId,
    question: question,
    slide_index: slideIndex + 1,
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
      showSlide(slideIndex); // resume current slide
      chatBtn.disabled = false;
    };
  } catch (err) {
    alert('Chat failed: ' + err.message);
    outputVideo.style.display = 'block';
    showSlide(slideIndex);
    chatBtn.disabled = false;
  }
};

uploadBtn.onclick = () => {
  window.location.href = '/upload';
};

