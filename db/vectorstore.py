import os
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI

load_dotenv(dotenv_path="config/.env")



# 환경변수에서 Supabase URL, Anon Key, OpenAI API 키 가져오기
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# Supabase 클라이언트 생성
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# OpenAI API 키 설정

def get_embedding(text: str) -> list:
    """
    OpenAI의 임베딩 API를 호출하여 text의 임베딩 벡터를 반환합니다.
    """
    response = client.embeddings.create(model="text-embedding-ada-002",
    input=text)
    embedding = response.data[0].embedding
    return embedding

def update_keyword_embeddings():
    """
    키워드 테이블의 각 레코드에 대해 description을 임베딩하고,
    결과를 embedding 컬럼에 업데이트합니다.
    """
    # 키워드 테이블에서 id와 description을 가져옵니다.
    response = supabase.table("keywords").select("id, description").execute()
    keywords_data = response.data

    for keyword in keywords_data:
        keyword_id = keyword["id"]
        description = keyword["description"]

        # OpenAI 임베딩 API를 통해 description을 임베딩
        embedding = get_embedding(description)

        # 임베딩 결과를 키워드 테이블에 업데이트
        update_response = supabase.table("keywords").update({"embedding": embedding}).eq("id", keyword_id).execute()

        print(f"Updated keyword ID {keyword_id} with embedding.")

if __name__ == "__main__":
    update_keyword_embeddings()