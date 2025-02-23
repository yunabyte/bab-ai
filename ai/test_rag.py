import os
from dotenv import load_dotenv
import openai
from langchain import OpenAI, PromptTemplate, LLMChain
from supabase import create_client, Client

# .env 파일에서 환경변수 로드 (config 폴더 내 .env 파일 경로 지정)
load_dotenv(dotenv_path="config/.env")

# 환경변수 가져오기
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI 및 Supabase 클라이언트 설정
openai.api_key = OPENAI_API_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def get_embedding(text: str) -> list:
    """
    OpenAI 임베딩 API를 호출해 주어진 텍스트의 임베딩 벡터를 반환합니다.
    """
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response["data"][0]["embedding"]

def search_restaurants(query_embedding: list, top_n: int = 5) -> list:
    """
    쿼리 임베딩 벡터와 키워드 임베딩 벡터 간 유사도 계산을 통해 관련 식당 정보를 조회합니다.
    실제 Supabase의 pgvector를 사용한 유사도 검색 쿼리를 호출합니다.
    
    예시로, 키워드 테이블에서 유사한 태그를 가진 식당(매핑 테이블 조인)을 조회합니다.
    """
    # 실제 운영에서는 아래와 같은 SQL 쿼리를 Supabase RPC 또는 테이블 쿼리로 실행합니다.
    # 예시 쿼리:
    # SELECT r.name, r.ctg2
    # FROM keywords k
    # JOIN restaurant_keywords rk ON k.id = rk.keyword_id
    # JOIN restaurants r ON rk.restaurant_id = r.id
    # WHERE ... (k.embedding와 쿼리 벡터 간 유사도 순 정렬)
    #
    # 여기서는 예시 결과를 반환하도록 합니다.
    results = [
        {"name": "해장국집", "ctg2": ["칼국수", "해장국", "국밥"]},
        {"name": "국밥의 정석", "ctg2": ["국밥", "칼국수"]},
        {"name": "따끈한 아침", "ctg2": ["해장", "찌개"]},
    ]
    return results[:top_n]

# 쿼리 시나리오
user_query = "오늘은 해장을 해야겠는걸"

# 1. 사용자 쿼리 임베딩 생성
query_embedding = get_embedding(user_query)

# 2. Supabase를 통해 유사도 검색으로 관련 식당 정보 조회 (매핑 테이블 이용)
restaurant_results = search_restaurants(query_embedding)

# 3. 조회된 식당 정보를 기반으로 자연스러운 추천 메시지 생성을 위한 프롬프트 준비
restaurant_info_str = "\n".join(
    [f"{r['name']} - Categories: {', '.join(r['ctg2'])}" for r in restaurant_results]
)

prompt_template = PromptTemplate(
    input_variables=["query", "restaurant_info"],
    template="""
You are a friendly food recommendation assistant.
The user query is: "{query}"

Based on the query, the following restaurants were identified:
{restaurant_info}

Provide a natural and engaging recommendation message for the user.
"""
)

# 4. LangChain LLMChain을 사용해 추천 메시지 생성
llm = OpenAI(temperature=0.7)
chain = LLMChain(llm=llm, prompt=prompt_template)

result_text = chain.run({"query": user_query, "restaurant_info": restaurant_info_str})

print("Recommendation:")
print(result_text)