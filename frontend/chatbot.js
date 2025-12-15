const icon = document.getElementById("chatbot-icon");
const box = document.getElementById("chatbot-box");
const closeBtn = document.getElementById("close-btn");
const messages = document.getElementById("chat-messages");
const input = document.getElementById("user-input");

icon.onclick = () => box.classList.remove("hidden");
closeBtn.onclick = () => box.classList.add("hidden");

function addMessage(text, className) {
    const div = document.createElement("div");
    div.className = className;
    div.innerText = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

async function sendMessage() {
    const question = input.value.trim();
    if (!question) return;

    addMessage("You: " + question, "user");
    input.value = "";

    try {
        const res = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question })
        });

        const data = await res.json();
        addMessage("Bot: " + data.answer, "bot");

    } catch (err) {
        addMessage("Bot: Backend not reachable", "bot");
    }
}
