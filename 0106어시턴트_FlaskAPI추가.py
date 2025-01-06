from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import openai

app = Flask(__name__)
load_dotenv()
API_KEY = os.environ['OPENAI_API_KEY']

# OpenAI Assistants API 클라이언트 설정
client = openai.OpenAI(api_key=API_KEY)

# Flask 라우트: HTML 페이지 렌더링
@app.route('/')
def index():
    return render_template('index.html')

# Flask 라우트: 사용자가 질문을 보낼 때 호출 (API 엔드포인트)
@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        user_input = data.get("question")

        # OpenAI Assistants API 사용 (스레드 생성 및 메시지 전송)
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        # 실행 생성 및 결과 대기
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id="asst_np1urbXJqkahf2ve9Sh1eqnR"
        )

        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        # 응답 메시지 가져오기
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        bot_response = messages.data[-1].content[0].text.value

        return jsonify({"answer": bot_response})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
