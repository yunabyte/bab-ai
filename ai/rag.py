from langchain.embeddings import OpenAIEmbeddings
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv(os.path.join(os.path.dirname(__file__), "../config/.env"))

# 임베딩 모델 생성
embedding_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
