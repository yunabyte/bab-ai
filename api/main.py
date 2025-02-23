# api/main.py

import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain.llms import OpenAI as LLMOpenAI
from langchain import PromptTemplate, LLMChain
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2

# .env 파일 로드 (config 폴더 내 .env 파일 경로 지정)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../config/.env"))

# 환경변수 가져오기
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not SUPABASE_DB_URL or not OPENAI_API_KEY:
    raise Exception("필수 환경 변수가 없습니다.")

# OpenAI API 설정
client = OpenAI(api_key=OPENAI_API_KEY)

def get_connection():
    """psycopg2를 사용해 데이터베이스 연결을 생성합니다."""
    return psycopg2.connect(SUPABASE_DB_URL)

def get_embedding(text: str) -> list:
    """
    OpenAI 임베딩 API를 호출해 주어진 텍스트의 임베딩 벡터를 반환합니다.
    """
    response = client.embeddings.create(model="text-embedding-ada-002",
    input=text)
    return response.data[0].embedding

def search_restaurants(query_embedding: list, top_n: int = 5) -> list:
    """
    쿼리 임베딩 벡터와 데이터베이스에 저장된 키워드 임베딩 벡터 간 유사도 연산을 통해
    관련 식당 정보를 조회합니다.
    """
    conn = get_connection()
    cur = conn.cursor()

    # query_embedding을 pgvector가 인식할 수 있도록 문자열로 변환 (공백 없이)
    embedding_str = str(query_embedding).replace(" ", "")

    sql = f"""
    SELECT r.name, r.ctg2
    FROM keywords k
    JOIN restaurant_keywords rk ON k.id = rk.keyword_id
    JOIN restaurants r ON rk.restaurant_id = r.id
    ORDER BY k.embedding <-> '{embedding_str}'::vector
    LIMIT {top_n};
    """
    try:
        cur.execute(sql)
        rows = cur.fetchall()
    except Exception as e:
        cur.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"데이터베이스 쿼리 에러: {e}")

    cur.close()
    conn.close()

    results = [{"name": row[0], "ctg2": row[1]} for row in rows]
    return results

# LangChain 프롬프트 템플릿 및 LLMChain 설정 (프롬프트 한국어)
prompt_template = PromptTemplate(
    input_variables=["query", "restaurant_info"],
    template="""
당신은 친절한 식당 추천 도우미입니다.
사용자 질문: "{query}"

데이터베이스에 저장된 다음 식당 정보를 참고하여,
사용자에게 적절한 식당을 추천해 주세요.
식당 이름, 메뉴, 가격 등을 포함하여 자연스럽게 설명해 주세요.

식당 정보:
{restaurant_info}
    """
)
llm = LLMOpenAI(temperature=0.7, openai_api_key=OPENAI_API_KEY)
chain = LLMChain(llm=llm, prompt=prompt_template)

# FastAPI 애플리케이션 생성
app = FastAPI()

# 요청 및 응답 모델 정의
class RecommendRequest(BaseModel):
    query: str

class RecommendResponse(BaseModel):
    recommendation: str

@app.post("/recommend", response_model=RecommendResponse)
def recommend_endpoint(req: RecommendRequest):
    user_query = req.query

    # 1. 사용자 쿼리 임베딩 생성
    query_embedding = get_embedding(user_query)

    # 2. 데이터베이스에서 벡터 연산을 통해 관련 식당 정보 조회
    restaurant_results = search_restaurants(query_embedding)

    # 3. 조회된 식당 정보를 문자열로 조합 (예: "식당명 - 카테고리: ...")
    restaurant_info_str = "\n".join(
        [f"{r['name']} - 카테고리: {', '.join(r['ctg2'])}" for r in restaurant_results]
    )

    # 4. LangChain을 사용해 추천 메시지 생성
    recommendation = chain.run({"query": user_query, "restaurant_info": restaurant_info_str})

    return RecommendResponse(recommendation=recommendation)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)