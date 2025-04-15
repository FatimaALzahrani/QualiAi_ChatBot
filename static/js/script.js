const socket = io();

const chatMessages = document.getElementById("chat-messages");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const criteriaItems = document.querySelectorAll(".criterion-group li");

criteriaItems.forEach((item) => {
  item.addEventListener("click", function () {
    const criterionId = this.getAttribute("data-id");
    const criterionText = this.textContent;
    sendMessage(criterionId);
  });
});

sendButton.addEventListener("click", function () {
  sendUserMessage();
});

messageInput.addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    sendUserMessage();
  }
});

function sendUserMessage() {
  const message = messageInput.value.trim();
  if (message) {
    addMessage("user", message);

    socket.emit("message", { message: message });

    messageInput.value = "";
  }
}

function sendMessage(message) {
  addMessage("user", message);

  socket.emit("message", { message: message });
}

function addMessage(sender, text) {
  const messageElement = document.createElement("div");
  messageElement.classList.add("message", sender);

  text = formatText(text);

  messageElement.innerHTML = text;
  chatMessages.appendChild(messageElement);

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatText(text) {
  text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  text = text.replace(/\*(.*?)\*/g, "<em>$1</em>");

  text = text.replace(/^- (.*?)$/gm, "<li>$1</li>");
  if (text.includes("<li>")) {
    text = "<ul>" + text + "</ul>";
  }

  text = text.replace(
    /(https?:\/\/[^\s]+)/g,
    '<a href="$1" target="_blank">$1</a>'
  );

  return text;
}

socket.on("message", function (data) {
  addMessage(data.sender, data.text);
});

socket.on("connect", function () {
  console.log("تم الاتصال بالخادم");
});

socket.on("disconnect", function () {
  console.log("تم قطع الاتصال بالخادم");
  addMessage(
    "bot",
    "تم قطع الاتصال بالخادم. يرجى تحديث الصفحة للمحاولة مرة أخرى."
  );
});
