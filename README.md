# i-am-meat-proxy

![버전](https://img.shields.io/badge/version-0.1.0-2563eb)
![도구](https://img.shields.io/badge/agents-Codex%20%C2%B7%20Claude%20%C2%B7%20Hermes-334155)
![한국어](https://img.shields.io/badge/skills-한국어_9종-16a34a)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776ab)
![접근](https://img.shields.io/badge/repository-private-6b7280)

**AI가 작업하고, 사람이 검수하고, 승인한 범위만 전달한다.**

Codex·Claude Code·Hermes에서 함께 쓰는 한국어 스킬과 전역 설정 패키지. 문서 작성, 간결한 답변, 커밋 전 사용자 검수, PR·Issue 등록을 같은 규칙으로 연결한다.

공통 규칙은 [전역 설정 저장소](https://github.com/cocodding0723/i-am-meat-proxy-config) 한 곳에서 관리한다. 모델·MCP·Hermes 운영 설정은 재설치용 템플릿으로 보관하고, 설치기는 필요한 스킬과 작업 규칙만 현재 환경에 적용한다.

## 빠른 시작

스킬 설치에는 Python 3.9 이상과 Git 필요. 설정 템플릿 변환에는 Python 3.11 이상과 PyYAML을 사용한다. 세 도구의 사용자 스킬 폴더는 없어도 생성한다. 비공개 저장소 두 개에 접근 가능한 GitHub SSH 인증이 필요하다.

```sh
git clone --recurse-submodules git@github.com:cocodding0723/i-am-meat-proxy.git
cd i-am-meat-proxy
python3 scripts/meat_proxy.py install --dry-run --replace
python3 scripts/meat_proxy.py install --replace
python3 scripts/meat_proxy.py doctor
```

`--replace`는 다른 내용의 기존 스킬·관리 파일을 **백업 후 교체**한다. 사용자가 쓴 지침은 관리 블록 밖에 보존한다. 알려진 예전 자동 커밋 규칙만 승인 우선 규칙으로 대체하며, 사용자가 수정한 다른 규칙이면 중단한다.

이미 설치돼 있으면 같은 명령을 다시 실행해도 변경하지 않는다. 새 스킬은 다음 턴이나 새 세션에서 확인한다. 이미 열린 Claude·Hermes 세션에 목록이 남아 있으면 새 세션을 시작한다.

## 포함 스킬

| 스킬 | 역할 | 적용 시점 |
| --- | --- | --- |
| [review-before-commit](skills/review-before-commit/SKILL.md) | 변경·검증 자료 제시, 사용자 승인, 범위를 지킨 커밋 | 코드 변경 마무리·커밋 준비 |
| [create-pr](skills/create-pr/SKILL.md) | 변경 분석, 저장소 템플릿, 한국어 PR 작성·등록 | PR 생성·수정 요청 |
| [manage-issues](skills/manage-issues/SKILL.md) | 버그·기능·작업 Issue 작성·등록 | Issue 생성·수정 요청 |
| [qa-checklist](skills/qa-checklist/SKILL.md) | 바뀐 기능 요약 + QA용 한 장 체크리스트 작성·점검 | QA 문서·테스트 체크리스트 요청 |
| [doc-coauthoring](overlays/doc-coauthoring/SKILL.md) | 문서 구조·근거·독자 관점 검토 | 기술 문서·QA·README 작성 |
| [writing-clearly-and-concisely](overlays/writing-clearly-and-concisely/SKILL.md) | 군더더기와 모호한 표현 축소 | 문장 편집·축약 |
| [writing-humanizer](overlays/writing-humanizer/SKILL.md) | 과장·상투어·기계적인 문체 정리 | 문체 재작성 |
| [prose-lint](overlays/prose-lint/SKILL.md) | Vale로 모호한 환경·검증 표현 검사 | 표현 린트 요청 |
| [i-have-adhd](overlays/i-have-adhd/SKILL.md) | 답부터 제시, 단계 정리, 한국어 표현 압축 | 명시적 호출만 |

스킬 식별자는 세 도구에서 같은 영문 이름을 유지하고, 설명·본문·표시 이름은 한국어로 제공한다. 기존 영문 참고서와 라이선스는 출처 보존을 위해 유지한다. 매번 스킬 9개를 전부 읽지 않는다.

사용 예시:

```text
review-before-commit으로 이번 변경을 검수할 수 있게 정리해줘. 승인 전에는 커밋하지 마.
create-pr로 현재 변경의 PR 초안만 작성해줘.
manage-issues로 이 버그를 현재 저장소에 등록해줘.
qa-checklist로 이번 브랜치 QA 체크리스트 만들어줘.
doc-coauthoring으로 이 QA 문서를 처음 보는 사람이 실행할 수 있게 다듬어줘.
```

Codex에서는 `$스킬명`, Claude Code·Hermes에서는 `/스킬명`으로 명시 호출할 수 있다. 자연어로 스킬 이름을 지정해도 된다. `i-have-adhd`는 자동 호출을 끈 상태로 유지하며, 호출 뒤 `stop adhd mode` 또는 `normal mode`로 종료한다.

## 검수와 게시

`구현·검증 → 변경 내용 제시 → 사용자 승인 → 선택 stage·commit·push → 원격 SHA 확인`

구현 요청은 커밋·push 승인이 아니다. 이번 범위의 업로드를 사용자가 이미 명시했다면 그 승인을 재사용한다. 승인 뒤 작업 범위가 달라지면 변경분을 다시 보여준다. PR·Issue 초안 요청은 게시하지 않는다.

이 절차는 에이전트가 읽는 **작업 지침**이다. 모든 shell 실행을 강제로 막는 Git 보안 장치는 아니다. GitHuman 서버나 별도의 승인 UI는 설치하지 않는다.

## 충돌을 줄이는 구성

- 공통 원본은 `modules/global-config/policy/WORKFLOW.md` 한 파일. 각 도구에는 짧은 관리 블록과 해당 파일을 배포한다.
- 기존 글쓰기 스킬을 같은 이름의 한국어판으로 갱신한다. 이름만 다른 중복 복사본을 만들지 않는다.
- Claude의 `i-have-adhd@i-have-adhd` 플러그인 활성화만 해제해 전역 스킬과 중복 노출되지 않게 한다. 다른 플러그인·권한·모델 설정은 보존한다.
- Hermes 기본 `humanizer`는 유지하고, 원고 편집용 `writing-humanizer`와 역할을 구분한다.
- 기존 자동 커밋 안내는 사용자 승인 우선으로 바꾼다. 동기화 훅 파일의 안내도 맞추되, 비활성 훅을 자동으로 활성화하지 않는다.

설치 전 전체 대상 검사 → 로컬 백업 → 적용 → 내용 비교 순서. 기존 동명 스킬 충돌, 손상된 관리 블록, 심볼릭 링크 대상, 다른 세션의 변경을 발견하면 중단한다. 쓰기 실패 시 이번 설치에서 변경한 대상을 백업으로 복원한다. 복원 도중 다른 세션의 추가 변경이 발견되면 해당 파일을 보존하고 백업 위치를 보고한다.

## 설치 경로와 Hermes 프로필

| 도구 | 경로 | 공통 규칙 연결 |
| --- | --- | --- |
| Codex | `CODEX_HOME/skills`, 기본 `~/.codex/skills` | `AGENTS.md` 관리 블록 |
| Claude Code | `CLAUDE_CONFIG_DIR/skills`, 기본 `~/.claude/skills` | `CLAUDE.md` 관리 블록 |
| Hermes | `HERMES_HOME/skills`, 기본 `~/.hermes/skills` | `SOUL.md` 관리 블록 |

각 도구 루트의 `meat-proxy/WORKFLOW.md`에 공통 규칙을 설치한다. 기존 Hermes 성격 설정은 보존한다.

```sh
# 특정 도구만
python3 scripts/meat_proxy.py install --agent claude --replace

# 기존 Hermes 프로필에도 같은 스킬·규칙 적용
python3 scripts/meat_proxy.py install --replace --hermes-profiles
python3 scripts/meat_proxy.py doctor --hermes-profiles

# 실제 전역 폴더를 건드리지 않는 시험 설치
python3 scripts/meat_proxy.py install --home /tmp/meat-proxy-example
```

`--home`을 지정하면 호스트의 경로 환경변수를 무시한다. `--hermes-profiles`는 `config.yaml`이 있는 기존 프로필만 선택한다. 프로필 모델·토큰·gateway 상태는 바꾸지 않는다.

## 서브모듈과 한국어 조립

| 경로 | 저장소 | 역할 |
| --- | --- | --- |
| `modules/writing-skills` | [writing-skills](https://github.com/cocodding0723/writing-skills) · 비공개 | 글쓰기 원본·참고 문서·Vale 규칙 |
| `modules/i-have-adhd-compression` | [i-have-adhd-compression](https://github.com/cocodding0723/i-have-adhd-compression) | 응답 압축 원본 |
| `modules/global-config` | [i-am-meat-proxy-config](https://github.com/cocodding0723/i-am-meat-proxy-config) · 비공개 | 공통 규칙·모델·MCP·Hermes 설정 템플릿 |

[modules.lock.json](modules.lock.json)에 저장소와 SHA를 기록한다. Git 서브모듈 포인터와 함께 검토하며 설치기가 최신 원격 버전으로 자동 변경하지 않는다.

`overlays/`는 이 패키지의 한국어 진입 문서다. 설치기는 고정한 원본의 보조 파일에 한국어 문서·표시 정보를 덧씌워 조립한다. 원본 서브모듈은 수정하지 않는다. 새 검수·PR·Issue·QA 스킬은 `skills/`에 있다.

```sh
# 고정된 버전 복원
git submodule update --init --recursive

# 조립된 스킬을 별도 폴더에서 확인
python3 scripts/meat_proxy.py build --output dist/skills
```

서브모듈 갱신은 하위 저장소를 먼저 검증·push하고, 상위 포인터와 `modules.lock.json`을 함께 변경한다. 한국어판의 의미 변화와 라이선스도 확인한다.

## 모델·MCP·운영 설정 복원

[설정 저장소 README](modules/global-config/README.md)의 절차를 따른다. Codex·Claude·Hermes 및 Hermes 프로필 설정 총 11개를 JSON 템플릿으로 보관하며 원래 TOML·JSON·YAML로 렌더링한다.

API 키·토큰·MCP 환경값은 `${MEAT_...}`로 치환한다. 재설치 시 비공개 `values.local.json`에 입력하고 별도 폴더로 렌더링한 뒤 현재 설정과 비교한다. 인증 파일·`.env`·대화·메모리·DB·로그·예약 작업 본문은 포함하지 않는다. 기존 서비스 로그인·플러그인 설치·MCP 실행 파일은 새 환경에서 별도 준비한다.

## 검증과 복구

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate.py
python3 scripts/meat_proxy.py doctor --hermes-profiles

# 설정 템플릿 검증에는 PyYAML 필요
python3.11 -m venv .venv
.venv/bin/python -m pip install -r modules/global-config/requirements.txt
.venv/bin/python -m unittest discover -s modules/global-config/tests -v
```

검증 기록은 [VERIFICATION.md](VERIFICATION.md). `doctor`는 설치 내용·중복·공통 규칙 충돌을 점검한다. 실제 모델이 스킬을 올바르게 선택하거나 결과 품질이 좋은지는 별도 사용 평가가 필요하다. Vale 실행 파일은 패키지에 포함하지 않는다.

백업은 `~/.local/share/i-am-meat-proxy/backups/<UTC 시각>/`에 저장된다. `receipt.json`에 변경 경로와 백업의 대응이 있다. 복구는 현재 파일과 백업을 비교한 뒤 해당 항목만 되돌린다. 이후 사용자 변경을 지울 수 있어 자동 전체 제거·전체 복원 명령은 제공하지 않는다. 백업은 Git에 올리지 않는다.

## 출처

[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)에 원본, 한국어 수정 범위, 라이선스를 기록한다. 배지는 구성·버전 표시이며 CI·서비스 연결·모델 품질 검증 배지가 아니다.
