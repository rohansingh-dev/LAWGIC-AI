const chatForm = document.getElementById("chat-form")
const chatInput = document.getElementById("chat-input")
const chatLog = document.getElementById("chat-log")
const languageSelect = document.getElementById("language-select")
let chatMessages = []
let isTyping = false
function appendMessage(sender, text, timestamp = new Date()) {
  const messageId = Date.now().toString()
  const message = {
    id: messageId,
    sender,
    text,
    timestamp,
  }
  chatMessages.push(message)
  renderMessage(message)
  scrollToBottom()
}
function renderMessage(message) {
  if (!chatLog) return;
  if (message.sender === "user") {
    const div = document.createElement("div")
    div.className = "chat-message-user mb-4 text-right"
    div.innerHTML = `<span class="font-semibold text-blue-400"><i class='fas fa-user-circle mr-2'></i></span> <span class='bg-transparent text-white text-base'>${escapeHtml(message.text)}</span>`
    chatLog.appendChild(div)
  } else {
    const div = document.createElement("div")
    div.className = "chat-message-bot mb-8 flex items-start gap-4"
    div.innerHTML = `
      <div class="w-10 h-10 rounded-full flex items-center justify-center bg-gradient-to-r from-blue-500 to-purple-600 text-white text-xl flex-shrink-0 mt-1">
        <i class="fas fa-robot"></i>
      </div>
      <div class="p-4 rounded-2xl max-w-2xl bg-slate-800 text-slate-100 border border-slate-700 rich-ai-answer">
        ${formatMessageContent(message.text)}
      </div>
    `
    chatLog.appendChild(div)
  }
}
function formatMessageContent(content) {
  let html = escapeHtml(content);
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
             .replace(/\*(.*?)\*/g, "<em>$1</em>");
  const lines = html.split(/\r?\n/);
  let result = '';
  let inList = false;
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i].trim();
    if (/^- .+:$/.test(line)) {
      if (inList) { result += '</ul>'; inList = false; }
      result += `<strong class="block mt-4 mb-1">${line.replace(/^- (.+):$/, '$1:')}</strong>`;
    }
    else if (/^- /.test(line)) {
      if (!inList) {
        result += "<ul class='list-disc ml-6 my-2'>";
        inList = true;
      }
      result += `<li>${line.replace(/^- /, '')}</li>`;
    }
    else if (line === '') {
      if (inList) {
        result += '</ul>';
        inList = false;
      }
      result += '<br>';
    }
    else {
      if (inList) {
        result += '</ul>';
        inList = false;
      }
      result += `<p>${line}</p>`;
    }
  }
  if (inList) result += '</ul>';
  return result;
}
function escapeHtml(text) {
  return text.replace(/[&<>"']/g, function (c) {
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c];
  });
}
function showTypingIndicator() {
  isTyping = true
  const typingDiv = document.createElement("div")
  typingDiv.className = "typing-indicator chat-message-bot mb-8 flex items-start gap-4"
  typingDiv.innerHTML = `
    <div class="w-10 h-10 rounded-full flex items-center justify-center bg-gradient-to-r from-blue-500 to-purple-600 text-white text-xl flex-shrink-0 mt-1">
      <i class="fas fa-robot"></i>
    </div>
    <div class="p-4 rounded-2xl bg-slate-800 text-slate-100 border border-slate-700">
      <div class="loading-dots">
        <div></div>
        <div></div>
        <div></div>
      </div>
    </div>
  `
  chatLog.appendChild(typingDiv)
  scrollToBottom()
}
function hideTypingIndicator() {
  isTyping = false
  const typingIndicator = chatLog.querySelector(".typing-indicator")
  if (typingIndicator) {
    typingIndicator.remove()
  }
}
function scrollToBottom() {
  if (chatLog) {
    chatLog.scrollTop = chatLog.scrollHeight
  }
}
async function getAIResponse(message, language) {
  try {
    const response = await fetch("/chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ message, language }),
    })
    if (!response.ok) {
      throw new Error("Network response was not ok")
    }
    const data = await response.json()
    return data.reply
  } catch (error) {
    console.error("Chat error:", error)
    return '<span style="color:#ef4444;">[Error] Could not connect to server. Please try again later.</span>'
  }
}
function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}
document.addEventListener("DOMContentLoaded", () => {
  const mobileMenuBtn = document.getElementById("mobile-menu-btn")
  const mobileMenu = document.getElementById("mobile-menu")
  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener("click", () => {
      mobileMenu.classList.toggle("hidden")
    })
  }
  const contactForm = document.getElementById("contact-form")
  if (contactForm) {
    contactForm.addEventListener("submit", function (e) {
      e.preventDefault()

      const submitBtn = this.querySelector('button[type="submit"]')
      const originalText = submitBtn.innerHTML
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Sending...'
      submitBtn.disabled = true

      setTimeout(() => {
        showNotification("Thank you for your message! We'll get back to you soon.", "success")
        this.reset()
        submitBtn.innerHTML = originalText
        submitBtn.disabled = false
      }, 2000)
    })
  }
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault()
      const target = document.querySelector(this.getAttribute("href"))
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        })
      }
    })
  })
  window.addEventListener("scroll", () => {
    const nav = document.querySelector("nav")
    if (nav) {
      if (window.scrollY > 100) {
        nav.classList.add("backdrop-blur-md")
      } else {
        nav.classList.remove("backdrop-blur-md")
      }
    }
  })
})
function showNotification(message, type = "info") {
  const notification = document.createElement("div")
  notification.className = `fixed top-4 right-4 p-4 rounded-lg text-white z-50 ${
    type === "success" ? "bg-green-500" : type === "error" ? "bg-red-500" : "bg-blue-500"
  }`
  notification.textContent = message
  document.body.appendChild(notification)
  setTimeout(() => {
    notification.remove()
  }, 3000)
}
function askSampleQuestion(question) {
  if (chatInput) {
    chatInput.value = question
    chatInput.focus()
  }
}
window.LawgicAI = {
  showNotification,
  askSampleQuestion,
  appendMessage,
}
