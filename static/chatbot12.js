async function sendMessage(message) {
    const userMessageElement = document.createElement("div");
    userMessageElement.className = "message";
    userMessageElement.textContent = `You: ${message}`;
    chatMessages.prepend(userMessageElement);

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ input_text: message })  // 수정: message -> input_text
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
        botResponse += `\n\nAI Assistant: ${data.gpt_response}`;
        botResponse += `\n\n추출된 키워드: ${data.extracted_keywords.join(", ")}`;

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
