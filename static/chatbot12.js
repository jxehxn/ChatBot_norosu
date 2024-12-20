document.addEventListener("DOMContentLoaded", function () {
    const chatMessages = document.getElementById("chat-messages");
    const userInput = document.querySelector("#user-input input");
    const sendButton = document.querySelector("#user-input button");

    async function sendMessage(message) {
        const userMessageElement = document.createElement("div");
        userMessageElement.className = "message";
        userMessageElement.textContent = `You: ${message}`;
        chatMessages.prepend(userMessageElement);

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message })
            });

            if (!response.ok) {
                throw new Error(`서버 오류: ${response.status}`);
            }

            const data = await response.json();
            let botResponse = "";

            if (data.status === "success") {
                botResponse += `추천 상품:\n`;
                data.products.forEach(product => {
                    botResponse += `- ${product.name} (${product.category})\n`;
                });
            }
            botResponse += `\nAI Assistant: ${data.gpt_response}`;
            botResponse += `\n추출된 키워드: ${data.extracted_keywords.join(", ")}`;

            const botMessageElement = document.createElement("div");
            botMessageElement.className = "message";
            botMessageElement.textContent = botResponse;
            chatMessages.prepend(botMessageElement);

        } catch (error) {
            console.error("Error:", error);
            const errorMessageElement = document.createElement("div");
            errorMessageElement.className = "message";
            errorMessageElement.textContent = "Bot: 서버 오류가 발생했습니다. 다시 시도해주세요.";
            chatMessages.prepend(errorMessageElement);
        }
    }

    sendButton.addEventListener("click", () => {
        const message = userInput.value.trim();
        if (message) {
            sendMessage(message);
            userInput.value = "";
        }
    });

    userInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            const message = userInput.value.trim();
            if (message) {
                sendMessage(message);
                userInput.value = "";
            }
        }
    });
});
