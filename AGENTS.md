# i-am-meat-proxy 작업 규칙

한국어 스킬·공통 규칙의 원본을 관리한다. trunk 브랜치에 작업·push 가능.
변경 후 `python3 -m unittest discover -s tests -v`, `python3 scripts/validate.py`, `git diff --check` 실행.
서브모듈은 고정 커밋 유지. 하위 변경을 먼저 push하고 상위 포인터를 갱신한다.
기존 사용자 설정은 백업·관리 블록으로 보존한다. 모델·MCP·Hermes 운영 설정은 템플릿만 제공하며 설치기가 실제 서비스나 cron을 재시작하지 않는다.
자격증명·대화·메모리·실행 DB·로컬 백업은 저장소에 넣지 않는다.
