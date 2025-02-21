lcc.py : LangChainCustom (커스텀 체인)

### 초기 실행 방법
1. 벡터DB로 Chroma를 사용하므로 관련 패키지를 설치해주세요.
2. python3 lcc.py --build
   빌드하면 json 파일 내용이 벡터DB에 적재됩니다.
3. python3 lcc.py
   test_query에 있는 쿼리를 이용해서 랭체인 진행됩니다.

### 협업 시
- 개발 시작 전 GitHub 최신 코드로 업데이트하여 충돌을 방지해주세요.
- 챗봇 성능이 향상된 코드를 push한 경우, AI 팀원들에게 DM을 보내 최신 버전으로 업데이트하도록 안내해주세요.
  - git pull origin main
  - git push origin main
  - 현재 서비스 진행 중이 아니므로 별도의 브랜치 없이 main에서 개발을 진행합니다.
