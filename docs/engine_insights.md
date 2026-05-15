# 검색 엔진 인사이트·최적화 가이드

> scrapling 0.2.99로 광범위하게 스크래핑 실험하며 얻은 교훈입니다.

---

## 1. TextHandler 함정

scrapling의 `TextHandler`(`.text`로 접근)는 **`__len__`가 깨져 있음** — 텍스트가 있어도 `len(el.text)`가 `0`인 경우가 많습니다.

**항상 이렇게:**
```python
str(el.text)          # el.text가 None이 아닐 때
el.get_all_text()     # 중첩 요소 대비 폴백
```

`base.py`의 `_text(el)` 헬퍼가 이를 안전하게 캡슐화합니다.

---

## 2. 네이버 — 난독화 DOM 복구

네이버 SERP는 해시된 CSS 클래스(`sds-comps-*`, `fender-ui_*`)로 재설계되었습니다. 전통 셀렉터(`.total_wrap`, `.lst_total`)는 매칭이 0개입니다.

**대응:**
- 컨테이너: `.fds-web-doc-root` — organic 웹 결과마다 안정적으로 감쌈
- URL: `a[nocr="1"]` — **직접 외부 링크**, 리다이렉트 디코딩 불필요
- 제목/스니펫: `get_all_text()` 파싱 + UI 노이즈 필터

핵심: 네이버는 여전히 핵심 구조를 SSR하므로 `AsyncFetcher`(JS 없음)로 충분합니다.

---

## 3. 바이두 — 노이즈 필터링

바이두는 organic 결과에 AI 답변, 광고, 추천 위젯을 섞습니다.

**필수 필터:** 클래스 `result-op`(운영·프로모션 콘텐츠) 컨테이너는 건너뜀.

내부 URL도 필터:
- `nourl.ubs.baidu.com`
- `recommend_list.baidu.com`
- `baidu.php` 리다이렉트

---

## 4. 구글 — 세션 재사용이 전부

구글 레이트 리밋은 **IP만이 아니라** 다음을 크게 봅니다.
- 브라우저 핑거프린트 일관성
- 쿠키/세션 연속성
- 로그인 상태

**발견:** `StealthyFetcher.async_fetch()`는 **호출마다 새 브라우저**를 띄워 쿠키를 날립니다. `real_chrome=True`여도 엄격한 한도에 걸립니다.

**대안:** `AsyncStealthySession`은 요청 간 브라우저 인스턴스를 재사용합니다. 쿠키가 유지되어 연속 검색 시 429 없이 성공하기 쉽습니다.

추가 하드닝:
- `real_chrome=True` — 번들 Chromium 대신 시스템 Chrome
- `network_idle=True` — 페이지 로드 완료까지 대기
- `block_webrtc=True`, `hide_canvas=True` — IP/핑거프린트 유출 완화
- `locale="en-US"`, `timezone_id="America/New_York"` — US 로캘 스푸핑
- `adaptive=True` — 구글이 컨테이너 셀렉터를 바꿀 때 복구

---

## 5. 빙 — 로캘 파라미터

빙은 기본적으로 IP 지리위치를 따릅니다. 한국 IP에서 "machine learning tutorial"을 치면 "machine"에 대한 국어 사전 결과가 나올 수 있습니다.

**수정:** `setmkt=en-US&setlang=en`을 붙여 영어 결과를 강제합니다.

---

## 6. DuckDuckGo — 지역 고정

DuckDuckGo도 지리에 민감합니다. `kl=us-en`을 붙여 미국 영어 결과를 우선합니다.

---

## 7. Startpage — JS 렌더링 필수

Startpage는 구글 결과를 프록시하지만 클라이언트 JS로 렌더합니다. `AsyncFetcher`는 빈 결과; `StealthyFetcher`(또는 `AsyncStealthySession`)가 필수입니다.

---

## 8. 특수 쿼리 연산자 — 주의

`site:`, `filetype:` 등을 **자동 주입**하는 것은 **위험**합니다.

| 연산자 | DuckDuckGo | Bing | Google | 판단 |
|----------|-----------|------|--------|------|
| `site:` | 동작 | **0건** | 봇 탐지 | **자동 주입 금지** |
| `filetype:` | 미검증 | 미검증 | 미검증 | 일반 검색에는 리스크 |

**더 안전:** 쿼리 연산자 대신 엔진 URL 파라미터(`hl=`, `setmkt=`, `kl=`)를 튜닝합니다.

---

## 9. URL 필터링 — 전역 개선

`utils/url.py`에 추가된 것들:
- `ubs.baidu.com` — 바이두 내부 트래킹
- `recommend_list.baidu.com` — 바이두 추천 위젯
- `baidu.php` — 바이두 리다이렉트 프록시
- `nourl.` — 바이두 플레이스홀더 URL

---

## 10. 엔진 아키텍처 결정

### API 전용 엔진은 피할 것
Brave(`BRAVE_API_KEY` 필요), Academic(ArXiv + Semantic Scholar API) 등은 제거했습니다. 프로젝트는 **직접 HTML 스크래핑**과 외부 API 비의존에 집중합니다.

### 세션 vs Fetcher
| 패턴 | 호출마다 브라우저 | 쿠키 유지 | 레이트 리스크 |
|---------|-----------------|-----------------|-----------------|
| `AsyncFetcher.get()` | 해당 없음(HTTP만) | 해당 없음 | 낮음 |
| `StealthyFetcher.async_fetch()` | 매번 새로 | 없음 | **높음** |
| `AsyncStealthySession` | 재사용 | 있음 | **낮음** |

JS 렌더가 필요한 엔진(구글, Startpage)은 `AsyncStealthySession`을 우선하세요.
