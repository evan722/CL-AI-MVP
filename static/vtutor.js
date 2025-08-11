const unityIframe = document.getElementById('unity-iframe');
const questionInput = document.getElementById('question');
const askBtn = document.getElementById('askBtn');
const answerDiv = document.getElementById('answer');

askBtn.onclick = async () => {
  const question = questionInput.value.trim();
  if (!question) return;

  try {
    const res = await fetch('/vtutor_chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Error');
    answerDiv.textContent = data.answer;
    unityIframe.contentWindow.postMessage({ action: 'unitySpeak', message: data.answer }, '*');
  } catch (err) {
    alert('Chat failed: ' + err.message);
  }
};
