# api/main.py

from fastapi import FastAPI, Query
import os
import psycopg2
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
import json

# 환경 변수 로드 (.env 파일)
load_dotenv(os.path.join(os.path.dirname(__file__), "../config/.env"))

app = FastAPI()

def get_connection():
    DB_URL = os.getenv("SUPABASE_DB_URL")
    return psycopg2.connect(DB_URL)

# LLM 설정 (OpenAI API 사용)
llm = ChatOpenAI(
    model_name="gpt-4", 
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# DB에서 식당 데이터를 가져와 텍스트로 변환하는 함수
def get_restaurants_text():
    conn = get_connection()
    cur = conn.cursor()
    # 필요한 컬럼 선택 (menu는 JSONB 타입이라 DB에서 가져올 때 이미 파이썬 객체로 반환될 수 있음)
    cur.execute("SELECT name, menu FROM restaurants;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    restaurants_info = []
    for row in rows:
        name, menu = row
        # 만약 menu가 문자열이면 파싱, 리스트면 그대로 사용
        if isinstance(menu, str):
            try:
                menu_list = json.loads(menu)
            except Exception as e:
                print("JSON 파싱 에러:", e)
                menu_list = []
        elif isinstance(menu, list):
            menu_list = menu
        else:
            menu_list = []
            
        # 메뉴 항목을 "메뉴명 (가격원)" 형태로 변환
        menu_str = ", ".join(
            [f"{item.get('name', 'N/A')} ({item.get('price', 'N/A')}원)" for item in menu_list]
        )
        info = f"식당 이름: {name}\n메뉴 및 가격: {menu_str}"
        restaurants_info.append(info)
    return "\n\n".join(restaurants_info)

@app.get("/")
def read_root():
    return {"message": "Restaurant Recommendation API is running!"}

@app.get("/recommend")
def recommend(query: str = Query(..., description="추천 받고 싶은 식당에 대한 자연어 질문을 입력하세요")):
    # Supabase에서 식당 정보 가져오기
    restaurants_text = get_restaurants_text()
    
    # 사용자 쿼리와 식당 정보를 포함하는 프롬프트 생성
    prompt = f"""
    당신은 식당 추천 챗봇입니다.
    사용자 질문: "{query}"
    
    다음은 데이터베이스에 저장된 식당 정보입니다:
    {restaurants_text}
    
    위 정보를 바탕으로 사용자에게 적절한 식당 추천을 한글로 해주세요.
    메뉴와 가격도 함께 제시해주세요.
    """
    response = llm.predict(prompt)
    return {"recommendation": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)