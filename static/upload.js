const status = document.getElementById('status');

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

