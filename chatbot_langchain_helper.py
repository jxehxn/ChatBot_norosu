import os
import pandas as pd
from dotenv import load_dotenv  # 추가
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage
from sklearn.feature_extraction.text import TfidfVectorizer

# .env 파일 로드
load_dotenv()  # .env 파일에서 환경 변수 읽기

# OpenAI API 키 설정
api_key = os.getenv("OPENAI_API_KEY")  # 환경 변수에서 API 키 로드
if not api_key:
    raise ValueError("OpenAI API Key가 설정되지 않았습니다. .env 파일을 확인하세요.")
os.environ["OPENAI_API_KEY"] = api_key

def load_excel_database(file_path):
    """엑셀 파일 로드 및 데이터프레임 반환."""
    return pd.read_excel(file_path)

def extract_keywords(query, num_keywords=10):
    """사용자 질문에서 주요 키워드를 추출 (TF-IDF 사용)."""
    try:
        if not query or query.strip() == "":
            return []

        vectorizer = TfidfVectorizer(stop_words='english', max_features=num_keywords)
        vectors = vectorizer.fit_transform([query])
        keywords = vectorizer.get_feature_names_out()

        return list(keywords)
    except Exception as e:
        print(f"키워드 추출 중 오류 발생: {str(e)}")
        return []

def search_products(df, query):
    """키워드와 일치하는 상위 5개 상품을 반환."""
    keywords = extract_keywords(query, num_keywords=10)
    if not keywords:
        return pd.DataFrame(), "키워드를 추출하지 못했습니다."

    print(f"추출된 키워드: {keywords}")

    def match_score(row):
        row_text = " ".join(str(row[col]).lower() for col in df.columns if col != "match_score")
        return sum(keyword.lower() in row_text for keyword in keywords)

    if 'match_score' in df.columns:
        df = df.drop(columns=['match_score'])

    df['match_score'] = df.apply(match_score, axis=1)
    sorted_results = df.sort_values(by='match_score', ascending=False)

    top_results = sorted_results[sorted_results['match_score'] > 0].head(5)
    unmatched_reason = "키워드와 일치하는 항목이 없습니다." if top_results.empty else ""
    return top_results, unmatched_reason

def generate_gpt_response(keywords, role="쇼핑몰 CS 전문가"):
    """LangChain을 사용하여 역할 기반 응답 생성"""
    try:
        if not keywords:
            return "키워드를 추출하지 못했습니다. 다시 시도해주세요."

        # LangChain ChatOpenAI 객체 생성
        chat = ChatOpenAI(model="gpt-4", temperature=0)

        # 역할 및 키워드를 기반으로 프롬프트 생성
        prompt_template = (
            f"당신은 {role}입니다. 다음 키워드를 기반으로 사용자에게 도움이 되는 답변을 제공하세요: {', '.join(keywords)}"
        )

        # LangChain의 HumanMessage 객체를 사용해 메시지 구성
        messages = [HumanMessage(content=prompt_template)]

        # 모델 호출
        response = chat(messages)

        # 응답 텍스트 반환
        return response.content.strip()

    except Exception as e:
        return f"LangChain을 통해 답변 생성 중 오류가 발생했습니다: {str(e)}"
