# 검증 기록

검증 대상: 0.1.0, 2026-09-17 macOS 로컬.

도구: Python 3.9.6(설치기), Python 3.11(Hermes 가상환경·설정 변환), Codex CLI 0.154.0, Claude Code 2.1.258.

| 확인 항목 | 결과 |
| --- | --- |
| 패키지 설치·충돌·백업·복원·동시 변경 보존·재실행·프로필 격리 | 11개 테스트 통과 |
| 설정의 비밀값 치환·경로 이식·누락값 중단·TOML·전체 11개 템플릿 왕복 변환 | 5개 테스트 통과 |
| 한국어 스킬 메타데이터·본문·참조·README 로컬 링크 | 8개 스킬 통과 |
| Codex skill-creator `quick_validate.py` | 7개 통과. `disable-model-invocation` 필드를 쓰는 i-have-adhd는 실제 도구 인식으로 확인 |
| Codex app-server `skills/list` | 8개 인식·활성, 중복 없음 |
| Claude Code 초기화 응답의 명령 목록 | 8개 인식, 중복 없음 |
| Hermes `skills_list` / `skill_view` | 기본 환경 및 기존 프로필 7개에서 각각 8개 목록·본문 읽기 성공 |
| 전역 설치본과 조립 원본 비교 | 10개 설치 루트 × 8개 스킬 일치 |
| `doctor --hermes-profiles` | 충돌 0건 |
| 설치 명령 재실행 계획 | 변경 0건 |
| 모델·MCP·Hermes 운영 설정 | 설치 전후 파일 해시 일치 |
| Claude settings.json | i-have-adhd 중복 플러그인 활성화 값만 변경. 나머지 구조·값 일치 |

Claude 인식 확인은 hooks·MCP를 끈 초기화 요청으로 수행했다. 모델 프롬프트를 보내지 않았다. Codex도 세션 생성이나 모델 호출 없이 스킬 목록만 확인했다.

백업: 각 설치 경로와 이전 파일은 로컬 `~/.local/share/i-am-meat-proxy/backups/`의 영수증으로 추적한다. 해당 백업·절대 사용자 경로·인증값은 이 문서에 포함하지 않는다.

모델 호출을 통한 자동 스킬 선택·문서 편집 품질, 실제 모델/API 인증, MCP 서비스 연결, Hermes gateway 재기동은 이 검증 범위에 포함하지 않는다.
