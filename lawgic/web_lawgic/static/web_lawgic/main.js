const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatLog = document.getElementById('chat-log');
const languageSelect = document.getElementById('language-select');

function appendMessage(sender, text) {
    const div = document.createElement('div');
    div.className = 'chat-message ' + sender;
    div.textContent = (sender === 'user' ? 'You: ' : 'LawgicAI: ') + text;
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
}

chatForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const message = chatInput.value.trim();
    const language = languageSelect.value;
    if (!message) return;
    appendMessage('user', message);
    chatInput.value = '';
    fetch('/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, language })
    })
    .then(res => res.json())
    .then(data => {
        appendMessage('bot', data.reply);
    })
    .catch(() => {
        appendMessage('bot', '[Error] Could not connect to server.');
    });
});
