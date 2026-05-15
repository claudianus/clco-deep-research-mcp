# maru-deep-pro-search에 기여하기

> **문서 언어:** 개발·기여 가이드는 **한국어**가 기본입니다.

기여에 관심 가져 주셔서 감사합니다. 이 문서는 참여 시 지켜야 할 기준을 정리합니다.

## 개발 환경

```bash
git clone https://github.com/claudianus/maru-deep-pro-search.git
cd maru-deep-pro-search

# 개발 의존성 포함 설치 (CI와 동일: ruff, mypy 등)
uv sync --all-groups

# 또는 설치 스크립트
bash scripts/install.sh
```

## 품질 게이트

```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy src/
```

자동화된 테스트는 사용하지 않습니다. 검증은 정적 분석이 전부입니다.

## 코드 스타일

- Python 3.10+ 문법: `Optional` 대신 `| None`, `List[str]` 대신 `list[str]`
- PEP 8, 줄 길이 100
- 공개 함수·메서드에 타입 힌트
- 독스트링은 Google 스타일

## 새 검색 엔진 추가

1. `src/maru_deep_pro_search/engines/<이름>.py` 생성
2. `BaseEngine`을 상속하고 `search()`·`fetch()` 구현
3. `engines/registry.py`의 `_register_builtins()`에 등록
4. `README.md` 엔진 표·`docs/index.html` 갱신

## 새 에이전트 어댑터 추가

1. `src/maru_deep_pro_search/cli/agents/<이름>.py` 생성
2. `AgentAdapter`를 상속하고 `detect`, `install_mcp`, `inject_rules`, `backup`, `restore` 구현
3. `cli/setup.py`의 `ADAPTER_REGISTRY`에 등록
4. `README.md`·`docs/index.html`·`AGENT_COMPATIBILITY.md` 등 문서 동기화

## 보안 시그니처 추가

1. `utils/sanitize.py`의 `_compile_signatures()`에 정규식 패턴 추가
2. 필요 시 다국어 변형 포함
3. `README.md`의 시그니처 개수 갱신

## PR 절차

1. 포크 후 기능 브랜치 생성
2. 커밋 메시지를 명확히
3. 위 품질 게이트 통과 확인
4. 문서 갱신 (`README.md`, `docs/index.html`, `CHANGELOG.md` 등)
5. PR 템플릿에 맞춰 제출

## 릴리스

> ⚠️ **PyPI에 수동 업로드하지 마세요.** GitHub Actions가 자동 배포합니다.

1. `CHANGELOG.md`에 새 버전 반영
2. `pyproject.toml` 버전 수정 (`__init__.py`와 동기화)
3. `git tag v0.x.x && git push origin v0.x.x`
4. Actions가 PyPI 빌드·배포

## 문의

[GitHub Discussions](https://github.com/claudianus/maru-deep-pro-search/discussions) 또는 Issues로 연락 주세요.
