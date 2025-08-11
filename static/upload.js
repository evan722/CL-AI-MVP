const status = document.getElementById('status');

document.getElementById('uploadBtn').onclick = async () => {
  const slidesId = document.getElementById('slidesId').value.trim();
  const slidesFile = document.getElementById('slidesFile').files[0];
  const audioFile = document.getElementById('audioFile').files[0];
  const timeFile = document.getElementById('timeFile').files[0];
  const avatarFile = document.getElementById('avatarFile').files[0];

  if (!audioFile || !timeFile || !avatarFile || (!slidesId && !slidesFile)) {
    alert('Please provide audio, timestamps, avatar, and either a slides ID or PDF.');
    return;
  }

  const formData = new FormData();
  if (slidesFile) formData.append('slides', slidesFile);
  else formData.append('slides_id', slidesId);
  formData.append('audio', audioFile);
  formData.append('timestamps', timeFile);
  formData.append('avatar', avatarFile);

  status.textContent = 'Uploading...';

  try {
    const res = await fetch('/upload', { method: 'POST', body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Upload failed');
    status.textContent = 'Success! Redirecting...';
    window.location.href = `/?id=${data.id}`;
  } catch (err) {
    status.textContent = 'Error: ' + err.message;
  }
};

