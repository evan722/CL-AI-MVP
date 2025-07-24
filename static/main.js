const outputVideo = document.getElementById("outputVideo");
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
  formData.append("video", videoFile);
  formData.append("audio", audioFile);
  formData.append("timestamps", timeFile);
  formData.append("face", faceFile);

  try {
    const res = await fetch("/upload", { method: "POST", body: formData });
    if (!res.ok) throw new Error("Upload failed");
    const data = await res.json();

    const videoUrl = `/outputs/${data.output_video}`;
    outputVideo.src = videoUrl;
    outputVideo.load();

    const jsonText = await timeFile.text();
    timestamps = JSON.parse(jsonText);
  } catch (err) {
    console.error("Upload error:", err);
    alert("Failed to generate avatar. Check server logs.");
  }
};

// Sync slide info
outputVideo.ontimeupdate = () => {
  if (!timestamps.length) return;
  const t = outputVideo.currentTime;
  let idx = timestamps.findIndex((_, i) => t < (timestamps[i + 1] || Infinity));
  if (idx === -1) idx = timestamps.length - 1;
  slideInfo.textContent = `Slide ${idx + 1}`;
};
