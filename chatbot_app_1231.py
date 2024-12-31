import os
import pandas as pd
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter

# .env 파일 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)  # CORS 활성화

# OpenAI API Key 설정
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OpenAI API Key가 설정되지 않았습니다.")

# LangChain 초기화
def initialize_rag_pipeline():
    """LangChain RAG 파이프라인 초기화"""
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

    # 데이터 로드 및 전처리
    file_path = "db/Infoitems.xlsx"  # 교체된 파일 경로
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"데이터 파일이 존재하지 않습니다: {file_path}")

    # 엑셀 데이터를 읽기
    data = pd.read_excel(file_path)
    if data.empty:
        raise ValueError("엑셀 파일이 비어 있습니다. 데이터를 확인하세요.")

    # 컬럼 이름 전처리
    data.columns = data.columns.str.strip()

    # 데이터프레임을 LangChain 문서로 변환
    documents = [
        Document(
            page_content=f"Title: {row['Title']}, Brand: {row['Brand']}, Price: {row['Price']}, "
                         f"Option: {row['Option']}, Option 1: {row['Option 1']}, URL: {row['URL']}",
            metadata={"price": row['Price'], "url": row['URL'], "id": row['ID']}
        )
        for _, row in data.iterrows()
    ]

    # 텍스트 분리
    text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    split_documents = text_splitter.split_documents(documents)

    # FAISS 벡터스토어 초기화
    vectorstore = FAISS.from_documents(split_documents, embeddings)

    # OpenAI LLM 초기화
    llm = OpenAI(openai_api_key=openai_api_key)

    # RetrievalQA 체인 초기화
    retriever = vectorstore.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    return qa_chain

# RAG 파이프라인 초기화
try:
    qa_chain = initialize_rag_pipeline()
except Exception as e:
    print(f"RAG 파이프라인 초기화 오류: {e}")
    qa_chain = None

# 라우트 설정
@app.route("/")
def home():
    return render_template("bot.html")

@app.route("/chat", methods=["POST"])
def chat():
    if qa_chain is None:
        return jsonify({"error": "RAG 파이프라인 초기화 실패. 서버 로그를 확인하세요."}), 500

    data = request.json
    input_text = data.get("message", "")  # 수정: message -> input_text

    try:
        # LangChain RAG 파이프라인으로 응답 생성
        response = qa_chain.run(input_text)  # 수정: invoke() -> run()

        # 예시 응답 구조 수정
        return jsonify({
            "input_text": input_text,
            "response": response,
            "status": "success",  # 상태 추가
            "products": [{"name": "Product1", "category": "Category1"}],  # 예시 상품 데이터
            "gpt_response": response,  # 예시 GPT 응답
            "extracted_keywords": ["keyword1", "keyword2"]  # 예시 추출된 키워드
        })
    except Exception as e:
        print(f"Error during chat processing: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다. 다시 시도해주세요."}), 500


# Flask 실행
if __name__ == "__main__":
    app.run(host="localhost", port=5500, debug=True)
