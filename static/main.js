const outputVideo = document.getElementById("outputVideo");
const slidesVideo = document.getElementById("slidesVideo");
const slideInfo = document.getElementById("slideInfo");

let timestamps = [];

// Handle file upload
document.getElementById("uploadBtn").onclick = async () => {
  const videoFile = document.getElementById("videoFile").files[0];
  const audioFile = document.getElementById("audioFile").files[0];
  const timeFile = document.getElementById("timeFile").files[0];
  const faceFile = document.getElementById("faceFile").files[0];

  if (!videoFile || !audioFile || !timeFile || !faceFile) {
    alert("Please upload all files: video, audio, timestamps, and face image.");
    return;
  }

  const formData = new FormData();
  formData.append("video", videoFile);         // ✅ matches FastAPI
  formData.append("audio", audioFile);         // ✅ matches FastAPI
  formData.append("timestamps", timeFile);     // ✅ FIXED: matches FastAPI
  formData.append("face", faceFile);           // avatar image

  try {
    const res = await fetch("/upload", {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`Upload failed: ${res.status} - ${errorText}`);
    }

    const data = await res.json();

    if (!data.output_video || !data.slides_video) {
      throw new Error("Server did not return expected file paths");
    }

    outputVideo.src = `/outputs/${data.output_video}`;
    slidesVideo.src = `/uploads/${data.slides_video}`;
    outputVideo.load();
    slidesVideo.load();

    const jsonText = await timeFile.text();
    timestamps = JSON.parse(jsonText);
  } catch (err) {
    console.error("Upload error:", err);
    alert("Failed to generate avatar. Check server logs.");
  }
};

// keep slides video in sync with avatar
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
