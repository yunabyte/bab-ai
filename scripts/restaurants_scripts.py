import os
import json
import psycopg2
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# Supabase PostgreSQL 연결 문자열
DB_URL = os.getenv("SUPABASE_DB_URL")

def get_connection():
    return psycopg2.connect(DB_URL)

def insert_data(record):
    conn = get_connection()
    cur = conn.cursor()
    
    # record는 하나의 식당 데이터 (dictionary)로 가정
    id_value = record.get("id")
    name = record.get("name")
    thumbnail = record.get("thumbnail")
    menu = json.dumps(record.get("menu"))  # JSONB 컬럼에 넣기 위해 문자열로 변환
    ctg1 = record.get("ctg1")  # TEXT 배열; JSON 파일에 배열 형태면 그대로 넣으면 됨
    ctg2 = record.get("ctg2")
    diet = record.get("diet", False)
    cheap = record.get("cheap", False)
    latitude = record.get("latitude")
    longitude = record.get("longitude")
    kakao_link = record.get("kakao_link")
    
    query = """
    INSERT INTO restaurants (name, thumbnail, menu, ctg1, ctg2, diet, cheap, latitude, longitude, kakao_link)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(query, (name, thumbnail, menu, ctg1, ctg2, diet, cheap, latitude, longitude, kakao_link))
    conn.commit()
    cur.close()
    conn.close()

def main():
    # JSON 파일 열기 (파일 경로는 실제 경로로 수정)
    with open("db/store_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for record in data:
        insert_data(record)
    print("데이터 삽입 완료!")

if __name__ == "__main__":
    main()