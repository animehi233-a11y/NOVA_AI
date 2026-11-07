const form = document.getElementById("chat-form");
const input = document.getElementById("message");
const chat = document.getElementById("chat");
const welcome = document.getElementById("welcome");
const send = document.getElementById("send");
const messages = [];

function addMessage(role, text) {
  const bubble = document.createElement("div");
  bubble.className = `message ${role}`;
  bubble.textContent = text; // textContent prevents HTML injection
  chat.appendChild(bubble);
  bubble.scrollIntoView({ behavior: "smooth", block: "nearest" });
  return bubble;
}

async function sendMessage(text) {
  const clean = text.trim();
  if (!clean || send.disabled) return;

  welcome.hidden = true;
  messages.push({ role: "user", text: clean });
  addMessage("user", clean);
  input.value = "";
  send.disabled = true;
  const waiting = addMessage("assistant", "NOVA is thinking…");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: messages.slice(-12) })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Request failed");
    waiting.textContent = data.reply;
    messages.push({ role: "assistant", text: data.reply });
  } catch (error) {
    waiting.textContent = `Sorry, I couldn't answer. ${error.message}`;
    messages.pop(); // allow the user to retry the last message
  } finally {
    send.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", event => {
  event.preventDefault();
  sendMessage(input.value);
});

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 140) + "px";
});

document.querySelectorAll(".suggestion").forEach(button => {
  button.addEventListener("click", () => sendMessage(button.dataset.prompt));
});
