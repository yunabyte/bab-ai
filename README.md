lcc.py : LangChainCustom (커스텀 체인)

### 초기 실행 방법
1. 벡터DB로 Chroma를 사용하므로 관련 패키지를 설치해주세요.
2. python3 lcc.py --build
   빌드하면 json 파일 내용이 벡터DB에 적재됩니다.
3. python3 lcc.py
   test_query에 있는 쿼리를 이용해서 랭체인 진행됩니다.

### 협업 시
- 개발 시작할 때마다 깃헙 레포 pull 해와서 충돌 관리하고 시작해주세요.
- 챗봇 성능 향상된 코드 push하시면 ai 팀원들에게 한 번씩 dm 남겨서 업데이트된 버전으로 진행하도록 해주세요.
