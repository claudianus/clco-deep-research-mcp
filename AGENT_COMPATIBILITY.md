# 3-계층 강제 아키텍처 — 에이전트별 호환성 매트릭스

## 요약

| 에이전트 | Layer 1 서버 게이트 | Layer 2 클라이언트 훅 | 물리적 차단 강도 | 한계 / 주의사항 |
|---|---|---|---|---|
| **Claude Code** | O 자동 적용 | PreToolUse (Bash 차단) + PostToolUse (Write/Edit 사후 검증) + SessionStart (컨텍스트 주입) | **중간~강함** | PreToolUse 버그(GH#13744)로 Write/Edit은 exit 2가 차단 불가. SessionStart + PostToolUse 이중 보호로 우회 |
| **Aider** | O 자동 적용 | lint-cmd + test-cmd 게이트 (14개 언어 자동 감지) | **강함** | 린트/테스트 실패 시 에디트 롤백. 가장 신뢰할 수 있는 물리적 차단 |
| **Cursor** | O 자동 적용 | onPreEdit 훅 (2026+) -- 편집 적용 전 veto + .cursorrules + /research /verify 커맨드 | **중간~강함** | onPreEdit는 Cursor 2026+ 버전 필요. 구버전은 .cursorrules + defaultInstructions만 |
| **Hermes** | O 자동 적용 | pre_tool_call 네이티브 플러그인 훅 + /research 슬래시 커맨드 | **강함** | 네이티브 훅이라 도구 호출 자체를 차단. 플러그인 설치 필요 |
| **Windsurf** | O 자동 적용 | defaultInstructions + autoEnableTools | **약함** | 프롬프트 주입만. Layer 1 하드 에러에 전적 의존 |
| **Zed** | O 자동 적용 | assistant.default_instructions | **약함** | 프롬프트 주입만. Layer 1 하드 에러에 전적 의존 |
| **Continue** | O 자동 적용 | /research + /verify 커스텀 커맨드 | **약함** | 커맨드는 편의성 제공. Layer 1 하드 에러에 전적 의존 |
| **JetBrains** | O 자동 적용 | mcp.autoEnableTools | **약함** | MCP 도구 자동 활성화. Layer 1 하드 에러에 전적 의존 |
| **Copilot** | O 자동 적용 | defaultInstructions (VS Code settings.json) | **약함** | 프롬프트 주입만. Layer 1 하드 에러에 전적 의존 |
| **Cline** | O 자동 적용 | defaultInstructions (VS Code settings.json) | **약함** | 프롬프트 주입만. Layer 1 하드 에러에 전적 의존 |
| **Devin** | O 자동 적용 | devin.json 설정 주입 | **약함** | 프롬프트 주입만. Layer 1 하드 에러에 전적 의존 |
| **Amazon Q** | O 자동 적용 | amazonq.json 설정 주입 | **약함** | 프롬프트 주입만. Layer 1 하드 에러에 전적 의존 |
| **Cody** | O 자동 적용 | cody.json 설정 주입 | **약함** | 프롬프트 주입만. Layer 1 하드 에러에 전적 의존 |
| **Codeium** | O 자동 적용 | codeium.json 설정 주입 | **약함** | 프롬프트 주입만. Layer 1 하드 에러에 전적 의존 |
| **Supermaven** | O 자동 적용 | supermaven.json 설정 주입 | **약함** | 프롬프트 주입만. Layer 1 하드 에러에 전적 의존 |
| **Tabnine** | O 자동 적용 | tabnine.json 설정 주입 | **약함** | 프롬프트 주입만. Layer 1 하드 에러에 전적 의존 |
| **OpenCode** | O 자동 적용 | opencode.json 설정 주입 | **약함** | 프롬프트 주입만. Layer 1 하드 에러에 전적 의존 |
| **Kimi** | O 자동 적용 | ~/.kimi/config 설정 주입 | **약함** | 프롬프트 주입만. Layer 1 하드 에러에 전적 의존 |
| **Kilo** | O 자동 적용 | kilo.json 설정 주입 | **약함** | 프롬프트 주입만. Layer 1 하드 에러에 전적 의존 |
| **AntiGravity** | O 자동 적용 | antigravity.json 설정 주입 | **약함** | 프롬프트 주입만. Layer 1 하드 에러에 전적 의존 |

---

## Layer 1: Server-Side Enforcement (SessionEnforcer)

**모든 에이전트에 자동 적용됩니다.** MCP 서버 수준에서 동작하므로 클라이언트와 무관합니다.

- `deep_research` 호출 시 세션에 마킹 + 30분 TTL
- 나머지 7개 툴(`web_search`, `fetch_page`, `answer` 등)은 세션 마킹 없이 호출 시 `ResearchRequiredError` 반환
- 에이전트가 MCP를 우회하고 직접 파일 시스템에 쓰거나 외부 API를 호출하면 막을 수 없음

---

## Layer 2: Client-Side Hooks

### 물리적 차단 가능 (4개)

| 에이전트 | 훅 메커니즘 | 차단 시점 | 회피 난이도 |
|---|---|---|---|
| **Aider** | lint-cmd / test-cmd | 에디트 적용 후 린트/테스트 실행 시 | 거의 불가. 린트 실패=에디트 롤백 |
| **Hermes** | pre_tool_call 플러그인 | 도구 호출 직전 | 불가. 네이티브 훅이라 도구 실행 자체가 차단됨 |
| **Claude Code** | PreToolUse (exit 2) + PostToolUse + SessionStart | Bash: 실행 전 / Write/Edit: 사후 검증 | 중간. PreToolUse 버그로 Write/Edit은 SessionStart+PostToolUse로 이중 보호 |
| **Cursor** | onPreEdit (2026+) | 편집 적용 전 | 중간. 구버전 Cursor는 적용 불가 |

### 프롬프트 주입만 (16개)

나머지 16개 에이전트는 설정 파일에 `RESEARCH_PROTOCOL`을 주입하는 것만 가능합니다. 이들은 **Layer 1의 하드 에러 반환**에 의존합니다.

```
에이전트가 deep_research 없이 web_search 호출
    -> Layer 1: ResearchRequiredError 반환
    -> 에이전트가 에러를 무시하고 계속 진행하면 차단 실패
```

---

## Layer 3: Tool Dependency (generate_code)

- **적용 대상**: 모든 에이전트 (MCP 표준 툴)
- **메커니즘**: `generate_code(research_id=..., proposed_code=...)` 호출 시 세션의 `research_id` 일치 여부 + 코드 내 인용 `[N]` 포함 여부 검증
- **효과**: 에이전트가 "올바른 MCP citizen"일 때만 유효
- **한계**: 에이전트가 툴을 호출하지 않고 직접 파일에 쓰면 무의미

**권장**: Layer 2 훅이 있는 에이전트(Claude, Aider, Cursor, Hermes)와 병행 사용 시 시너지

---

## 종합 평가

| 강도 등급 | 에이전트 | 특징 |
|---|---|---|
| **강함** | Aider, Hermes | 에디트/도구 호출 자체를 물리적으로 차단. 에이전트가 막혀도 못 넘어감 |
| **중간~강함** | Claude Code, Cursor | 다중 훅으로 우회 어렵지만, 버그나 버전 의존성 존재 |
| **약함** | 나머지 16개 | 프롬프트 주입 + Layer 1 서버 에러에 의존. 에이전트가 무시하면 차단 불가 |
