# 보안 정책

> **문서 언어:** 보안·지원 정책 문서는 **한국어**로 작성합니다. (취약점 본문은 영어로 보내 주셔도 됩니다.)

## 지원 버전

| 버전 | 지원 |
|------|------|
| **0.15.x** (현재 PyPI) | ✅ 적극 개발 |
| **0.14.x** | ✅ 보안 수정 요청 시 |
| **0.14.0 미만** | ❌ 미지원 — 업그레이드 권장 |

## 취약점 신고

`maru-deep-pro-search`에서 보안 취약점을 찾으면 **책임 있게** 알려 주세요.

1. **공개 이슈를 열지 마세요.**
2. [GitHub Security Advisory](https://github.com/claudianus/maru-deep-pro-search/security/advisories/new)를 열거나 **security@maru.dev**로 메일을 보내 주세요. 포함할 내용:
   - 취약점에 대한 명확한 설명
   - 재현 단계
   - 영향 평가
   - (가능하면) 수정 제안

처리 기준(목표):
- 48시간 이내 접수 확인
- 7일 이내 상세 회신
- 해결 시 변경 이력에 기록(익명 원하면 익명 처리)

## 보안 관련 기능

다층 방어를 사용합니다.

### 리서치 강제 (3계층)

> **프롬프트 인젝션이 아닙니다.** LLM은 텍스트를 무시할 수 있습니다. 아래는 **기술적 게이트**입니다.

- **1층 — 서버 쪽 게이트:** `SessionEnforcer`가 MCP 세션을 추적합니다. `fetch_page`, `web_search`, `answer`, `parallel_search` 등 **연구 의존 툴**은 같은 세션에서 `deep_research`가 끝나지 않았거나 리서치가 만료되면(30분) 하드 오류를 냅니다. **면제** 툴: `version`, `list_engines`, `engine_health`, `session_state`, `drift_status`, `query_knowledge`, `cache_stats`, `clear_caches`.
- **2층 — 클라이언트 훅:** 에이전트가 행동하기 전 물리적 차단:
  - **Claude Code:** `PreToolUse` 훅(exit code 2)으로 `Write`/`Edit` 차단
  - **Aider:** `lint-cmd` 게이트 스크립트가 리서치 미완료 시 실패
  - **Cursor:** `/research`, `/verify` 슬래시 커맨드 + `.cursorrules`
  - **Hermes:** `pre_tool_call` 플러그인 훅으로 미리서치 툴 차단, `post_tool_call` 감사, `on_session_start`로 게이트 리셋
- **3층 — 툴 의존:** `generate_code`가 세션의 `research_id`와 일치하는지, `proposed_code`에 리서치 산출의 인용 `[N]`이 있는지 검증합니다. MCP를 우회해 파일을 직접 쓰면 이 층은 적용되지 않습니다.

### 입력 방어

- **72개** 프롬프트 인젝션 시그니처(10개 이상 언어)
- **MCP 특화 탐지:** 툴 포이즈닝, 럭 풀, 섀도잉, MPMA 등
- **콘텐츠 정제:** 제로폭 문자 제거, 토큰 중화
- **감사 로깅:** 툴 호출 이상 징후 탐지
- **Docker 샌드박스:** 격리 실행 환경

## 알려진 한계

- 검색 결과는 스크래핑 대상 사이트의 보안·정책에 좌우됩니다.
- 시맨틱 임베딩은 로컬(CPU)만 사용하며 외부 API를 호출하지 않습니다.
- 감사 로그는 로컬 SQLite(`.maru/audit.db`)에 저장됩니다. 주기적으로 로테이션하세요.