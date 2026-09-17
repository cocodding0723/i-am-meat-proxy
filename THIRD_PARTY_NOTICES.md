# 출처와 수정 범위

이 저장소는 개인 비공개 패키지. 구성 요소에 일괄 라이선스를 덧씌우지 않는다.

## 고정한 원본

- `writing-skills`: 서브모듈의 [라이선스 안내](modules/writing-skills/THIRD_PARTY_NOTICES.md)를 따른다. doc-coauthoring·간결한 문장 편집·humanizer·prose-lint의 한국어 진입 문서와 UI 표시를 이 패키지에서 재작성했다. 참고 문서·Vale 스크립트·규칙·개별 라이선스는 보존한다.
- `i-have-adhd-compression`: [MIT License](modules/i-have-adhd-compression/LICENSE). 원본의 10개 규칙과 한국어 압축 기준을 한국어로 정리했다. 명시 호출 정책 유지. 임의 진단·시간 단정·불필요한 다음 과제 유도를 피하도록 문구를 조정했다. 설치본에 원본 SKILL.md와 LICENSE를 보존한다.
- `global-config`: 사용자 환경에서 추출한 비밀값 없는 설정 템플릿과 공통 작업 규칙. 실행 파일·서비스 자격증명은 포함하지 않는다.

각 정확한 커밋은 [modules.lock.json](modules.lock.json) 참고. upstream 문서의 영문 참고서·원문은 번역본과 구분한다.

## 새 스킬의 참고 자료

아래 공개 자료에서 절차를 검토했으며, 스크립트나 스킬 원문을 그대로 복사하지 않았다. 세 새 스킬과 설치·검증 도구는 이 패키지용 한국어 작성본이다.

- [GitHuman review workflow](https://github.com/mcollina/githuman-skills/blob/main/skills/githuman/rules/review-workflow.md): 변경 검수·피드백·커밋 흐름. UI 실행은 필수로 두지 않음.
- [githuman-review](https://gist.github.com/alemagio/1f29b641f9820af9d4ca68c9cf6c205e): 승인 대기 흐름 참고. 실제 UI 승인 확인이 생략된 스크립트는 채택하지 않음.
- [tomzx/agents SDLC](https://github.com/tomzx/agents/blob/main/skills/sdlc/SKILL.md): 작업 완료 후 명시적 Git 게시 승인 규칙 참고. 전체 SDLC 의존성은 가져오지 않음.
- [Cline create-pull-request](https://github.com/cline/cline/blob/main/.agents/skills/create-pull-request/SKILL.md): diff·템플릿·본문 파일 기반 PR 등록 참고. 자동 rebase·stash·강제 push 절차 제외.
- [GitHub github-issues](https://github.com/github/awesome-copilot/blob/main/skills/github-issues/SKILL.md): Issue 유형·재현·완료 기준·기존 필드 보존 참고. 특정 MCP 이름이나 미검증 CLI 옵션을 고정하지 않음.

확인일: 2026-09-17. 참고 링크의 최신 내용과 고정 서브모듈 버전은 별개다.
