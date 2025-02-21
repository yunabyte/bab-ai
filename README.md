lcc.py : LangChainCustom 커스텀한 체인을 만들었습니다.

### 초기 실행 방법
1. 벡터DB로 Chroma를 사용했습니다. Chroma와 관련된 설치해주세요.
2. python3 lcc.py --build
   빌드하면 json 파일 내용이 벡터DB에 적재됩니다.
3. python3 lcc.py
   test_query에 있는 쿼리를 이용해서 랭체인 진행됩니다.
