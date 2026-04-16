# AI 기반 개발 — dx-runtime 가이드

## 개요

dx-runtime은 DEEPX 소프트웨어 스택 전반에 걸쳐 에이전틱 개발을 조율하는
**통합 레이어**입니다. **dx_app**(독립형 추론)과 **dx_stream**(GStreamer
파이프라인)을 단일 지식 베이스, 검증 시스템, 피드백 루프 아래 통합합니다.

dx-runtime 레벨에서 에이전트를 호출하면 **통합 라우터** 역할을 합니다 —
요청이 어떤 서브 프로젝트에 속하는지 판단하고, 적절한 스킬을 로드하여
올바른 빌더에 위임합니다.

## 작동 방식 — CLAUDE.md와 `.deepx/` 지식 베이스

dx 스택의 모든 프로젝트는 2계층 아키텍처를 따릅니다:

1. **`CLAUDE.md` / `AGENTS.md`** — IDE 진입점. Claude Code는 `CLAUDE.md`를,
   OpenCode는 `AGENTS.md`(동일 복사본)를 먼저 읽습니다. 환경 설정, 임포트 규칙,
   컨텍스트 라우팅 테이블, `.deepx/`로의 포인터가 포함됩니다.
2. **`.deepx/`** — 실제 지식 베이스. 에이전트, 스킬, 툴셋, 지침, 메모리, 스크립트,
   구조화된 지식(YAML)이 들어 있습니다. 에이전트는 소스 코드가 아닌 `.deepx/`
   파일을 컨텍스트로 읽습니다.

`CLAUDE.md`는 작고 안정적입니다. `.deepx/`는 프로젝트 성장에 따라 진화합니다.
에이전트는 컨텍스트 라우팅 테이블을 통해 필요한 파일만 로드하여 토큰 사용량을
최소화합니다.

## 지원 AI 도구

4가지 AI 코딩 도구가 지원됩니다. 각 도구는 자체 설정 파일을 통해
`.deepx/` 지식 베이스를 자동으로 로드합니다.

| 도구 | 유형 | 설정 파일 | 에이전트 호출 |
|---|---|---|---|
| **Claude Code** | CLI | `CLAUDE.md` | 자유 형식 대화; 라우팅 테이블이 자동 디스패치 |
| **GitHub Copilot** | VS Code | `.github/copilot-instructions.md`, `.github/agents/`, `.github/instructions/` | `@에이전트명 "프롬프트"` |
| **Cursor** | IDE | `.cursor/rules/*.mdc` | 자유 형식 대화; 규칙 자동 적용 |
| **OpenCode** | CLI | `AGENTS.md`, `opencode.json`, `.opencode/agents/`, `.opencode/skills/` | `@에이전트명` 또는 `/스킬명` |

### 자동 로드 상세

| 도구 | 항상 로드 | 파일별 로드 | 온디맨드 |
|---|---|---|---|
| Claude Code | `CLAUDE.md` | — | 라우팅 테이블 통한 `.deepx/skills/` |
| Copilot | `.github/copilot-instructions.md` | `.github/instructions/*.instructions.md` (`applyTo:` 글로브 매칭) | `.github/agents/*.agent.md` (`@이름`으로) |
| Cursor | `alwaysApply: true`인 `.cursor/rules/*.mdc` | `globs: [...]`인 `.cursor/rules/*.mdc` | — |
| OpenCode | `AGENTS.md` + `opencode.json` instructions | — | `.opencode/agents/*.md` (`@이름`), `.opencode/skills/*/SKILL.md` (`/이름`) |

### 설정

```bash
# Claude Code — 프로젝트 열고 코딩 시작
cd dx-runtime && claude

# OpenCode — 동일한 워크플로우
cd dx-runtime && opencode

# GitHub Copilot — VS Code에서 열기
code dx-runtime

# Cursor — Cursor에서 열기
cursor dx-runtime
```

### 플랫폼별 파일 참조

각 AI 코딩 에이전트는 dx-runtime 레벨에서 서로 다른 설정 파일을 자동 로딩합니다.

#### 자동 로딩 파일

| 파일 | Copilot Chat/CLI | OpenCode | Claude Code | Cursor | 로딩 |
|------|:---:|:---:|:---:|:---:|---------|
| `.github/copilot-instructions.md` | ✅ | — | — | — | 자동 |
| `CLAUDE.md` | — | — | ✅ | — | 자동 |
| `AGENTS.md` + `opencode.json` | — | ✅ | — | — | 자동 |
| `.cursor/rules/dx-runtime.mdc` | — | — | — | ✅ | 자동 |

#### 에이전트 파일 (수동 @mention)

| 에이전트 | Copilot (`@mention`) | OpenCode (`@mention`) |
|---------|------|---------|
| `dx-runtime-builder` | `.github/agents/dx-runtime-builder.agent.md` | `.opencode/agents/dx-runtime-builder.md` |
| `dx-validator` | `.github/agents/dx-validator.agent.md` | `.opencode/agents/dx-validator.md` |

#### 스킬 파일 (OpenCode 전용 — `/slash-command`)

| 스킬 | 파일 |
|-------|------|
| `/dx-brainstorm-and-plan` | `.opencode/skills/dx-brainstorm-and-plan/SKILL.md` |
| `/dx-validate-and-fix` | `.opencode/skills/dx-validate-and-fix/SKILL.md` |
| `/dx-verify-completion` | `.opencode/skills/dx-verify-completion/SKILL.md` |
| `/dx-tdd` | `.opencode/skills/dx-tdd/SKILL.md` |

#### 공유 지식 베이스 (`.deepx/`)

`.deepx/` 디렉토리는 모든 에이전트 플랫폼이 필요 시 참조하는 플랫폼 독립적 지식 베이스입니다. 자동 로딩되지 않으며, 에이전트와 스킬이 작업 실행 중 필요한 파일을 참조합니다.

| 디렉토리 | 파일 | 설명 |
|-----------|-------|-------------|
| `.deepx/agents/` | `dx-runtime-builder.md`, `dx-validator.md` | 권위 있는 에이전트 정의 (`.github/agents/` 및 `.opencode/agents/` 축약본의 원본) |
| `.deepx/skills/` | 4개 파일 (`dx-brainstorm-and-plan.md`, `dx-validate-and-fix.md`, `dx-verify-completion.md`, `dx-tdd.md`) | 상세 스킬 워크플로우 |

## 전체 에이전트 (총 12개)

### dx-runtime (에이전트 2개)

| 에이전트 | 역할 |
|---------|------|
| **dx-runtime-builder** | 통합 라우터 — 모든 요청을 수신하여 적절한 서브 프로젝트 빌더에 위임 |
| **dx-validator** | 통합 검증 — 모든 레벨의 검증 스크립트를 실행하고 피드백 수집 |

### dx_app (에이전트 6개)

| 에이전트 | 역할 |
|---------|------|
| **dx-app-builder** | 독립형 앱 마스터 라우터 — Python, C++, 또는 async 빌더 선택 |
| **dx-python-builder** | DxInfer와 InferenceEngine을 사용한 Python 추론 앱 빌드 |
| **dx-cpp-builder** | 네이티브 DxRT SDK를 사용한 C++ 추론 앱 빌드 |
| **dx-benchmark-builder** | .dxnn 모델 성능 벤치마킹 하니스 생성 |
| **dx-model-manager** | .dxnn 모델 경로 해석, 모델 다운로드, 설정 YAML 관리 |
| **dx-validator** | dx_app 출력 검증 — 임포트, 구조, 런타임 검사 |

### dx_stream (에이전트 4개)

| 에이전트 | 역할 |
|---------|------|
| **dx-stream-builder** | 파이프라인 앱 마스터 라우터 — 파이프라인 또는 메시징 빌더 선택 |
| **dx-pipeline-builder** | DX 가속기 엘리먼트를 사용한 GStreamer 파이프라인 앱 빌드 |
| **dx-model-manager** | 파이프라인용 .dxnn 모델 해석, 스트림 설정 관리 |
| **dx-validator** | dx_stream 출력 검증 — 파이프라인 문법, 엘리먼트 가용성 |

## 전체 스킬

| 프로젝트 | 스킬 | 용도 |
|---------|------|------|
| dx-runtime | `/dx-brainstorm-and-plan` | 프로세스: 코드 생성 전 협업 설계 세션 |
| dx-runtime | `/dx-tdd` | 프로세스: 테스트 주도 개발 — 검증 먼저, 구현 나중에 |
| dx-runtime | `/dx-verify-completion` | 프로세스: 완료 전 검증 — 증거 먼저, 주장 나중에 |
| dx-runtime | `dx-validate-and-fix` | 전체 피드백 루프 — 검증, 이슈 수집, 수정 적용 |
| dx_app | `dx-build-python-app` | Python 독립형 추론 앱 빌드 |
| dx_app | `dx-build-cpp-app` | C++ 독립형 추론 앱 빌드 |
| dx_app | `dx-build-async-app` | 비동기/배치 추론 앱 빌드 |
| dx_app | `dx-model-management` | .dxnn 모델 다운로드, 해석, 설정 |
| dx_app | `dx-validate` | dx_app 검증 스크립트 실행 |
| dx_stream | `dx-build-pipeline-app` | DX 엘리먼트를 사용한 GStreamer 파이프라인 앱 빌드 |
| dx_stream | `dx-build-mqtt-kafka-app` | MQTT/Kafka 메시지 출력 파이프라인 빌드 |
| dx_stream | `dx-model-management` | 스트리밍 파이프라인용 .dxnn 모델 관리 |
| dx_stream | `dx-validate` | dx_stream 검증 스크립트 실행 |

## 대화형 워크플로우 (5단계)

모든 에이전트는 동일한 5단계 워크플로우를 따릅니다:

### 1단계 — 이해
**2~3개의 핵심 질문**(앱 유형, 입력 소스, 특수 요구사항)을 합니다.
사용자 확인을 위한 빌드 계획을 제시합니다.

### 2단계 — 컨텍스트 로딩
컨텍스트 라우팅 테이블을 통해 관련 `.deepx/` 파일(스킬, 툴셋, 지침, 메모리)을
읽습니다. 소스 코드는 읽지 **않습니다** — 모든 API 참조와 패턴은 지식
베이스에 있습니다.

### 3단계 — 빌드
기본적으로 `dx-agentic-dev/<session_id>/`에 애플리케이션 파일을 생성합니다
(명시적 요청 시 `src/`에 직접 생성). `.deepx/instructions/`의 규칙을 따릅니다 —
절대 임포트, IFactory 패턴, 올바른 DxInfer 초기화.

### 4단계 — 검증
검증 스크립트 실행: 임포트 정확성, 구조 준수, 런타임 스모크 테스트
(문법 검사, 해당 시 드라이런).

### 5단계 — 보고
결과 제시: 생성된 파일(`dx-agentic-dev/` 또는 `src/` 내 전체 경로),
검증 상태, 실행 지침, 경고 사항.

## 빠른 시작 예제

다음 시나리오는 dx-runtime 레벨에서의 워크플로우를 보여줍니다. 시나리오 1은
dx-runtime 고유의 크로스 프로젝트 시나리오입니다. 시나리오 2와 3은 각각의
서브모듈(`dx_app/` 또는 `dx_stream/`)에서도 직접 실행할 수 있지만, dx-runtime에서
작업하면 통합 라우팅, 크로스 프로젝트 검증, 모든 레벨에 걸친
`dx-validate-and-fix` 피드백 루프를 활용할 수 있습니다.

### 시나리오 1: 독립형 앱과 스트리밍 파이프라인 동시 빌드

**프롬프트:**

```
"사람 감지 standalone 앱이랑 streaming 파이프라인 둘 다 만들어줘"
```

| 도구 | 사용 방법 |
|---|---|
| **Claude Code** | 프롬프트를 직접 입력. `CLAUDE.md`가 통합 컨텍스트 라우팅 테이블로 dx_app과 dx_stream 모두에 걸치는 작업임을 판단, 각각의 스킬 로드. |
| **GitHub Copilot** | `@dx-runtime-builder` 뒤에 프롬프트 입력. 요청을 분류 후 `handoffs:` 메커니즘으로 `dx-app-builder`와 `dx-stream-builder`에 핸드오프. |
| **Cursor** | 프롬프트를 직접 입력. `dx-runtime.mdc`(`alwaysApply: true`로 로드)가 전체 컨텍스트 라우팅 테이블 제공. |
| **OpenCode** | `@dx-runtime-builder` 뒤에 프롬프트 입력. `AGENTS.md`와 `opencode.json`이 세션 시작 시 자동 로드. |

### 시나리오 2: 독립형 감지 앱 빌드 (dx-runtime 라우팅 경유)

dx-runtime 레벨에서 이 요청을 하면 dx_app의 빌더로 라우팅됩니다.
`dx_app/`에서 직접 작업하는 것과 달리, dx-runtime은 두 서브 프로젝트에 걸친
통합 검증과 동일 세션에서 다른 작업과 연계할 수 있는 기능을 제공합니다.

**프롬프트:**

```
"yolo26n으로 사람 감지 앱 만들어줘"
```

| 도구 | 사용 방법 |
|---|---|
| **Claude Code** | 프롬프트를 직접 입력. `dx-build-python-app` 스킬로 라우팅. |
| **GitHub Copilot** | `@dx-app-builder` 뒤에 프롬프트 입력. |
| **Cursor** | 프롬프트를 직접 입력. |
| **OpenCode** | `@dx-app-builder` 뒤에 프롬프트 입력, 또는 `/dx-build-python-app` 스킬 사용. |

에이전트가 수행하는 작업:
1. 입력 소스와 출력 형식에 대해 질문
2. `dx-build-python-app` 스킬과 yolo26n 모델 설정 로드
3. `dx-agentic-dev/<session_id>/`에 파일 생성 (요청 시 `src/`에 직접)
4. 임포트와 구조 검증
5. 실행 명령과 함께 보고

> **팁:** 이 프롬프트는 `dx_app/`에서 직접 사용해도 동일하게 동작합니다.
> dx-runtime에서 작업하면 통합 라우팅과 다른 서브 프로젝트 작업과의 연계
> (예: 동일 세션에서 스트리밍 파이프라인도 함께 빌드)가 가능합니다.

### 시나리오 3: 스트리밍 파이프라인 빌드 (dx-runtime 라우팅 경유)

dx-runtime 레벨에서 이 요청을 하면 dx_stream의 빌더로 라우팅됩니다.
`dx_stream/`에서 직접 작업하는 것과 달리, dx-runtime은 통합 검증과
크로스 프로젝트 조율을 제공합니다.

**프롬프트:**

```
"RTSP 카메라에서 트래킹 포함 감지 파이프라인 만들어줘"
```

| 도구 | 사용 방법 |
|---|---|
| **Claude Code** | 프롬프트를 직접 입력. `dx-build-pipeline-app` 스킬로 라우팅. |
| **GitHub Copilot** | `@dx-stream-builder` 뒤에 프롬프트 입력. |
| **Cursor** | 프롬프트를 직접 입력. |
| **OpenCode** | `@dx-stream-builder` 뒤에 프롬프트 입력, 또는 `/dx-build-pipeline-app` 스킬 사용. |

에이전트가 수행하는 작업:
1. RTSP URL, 디스플레이 설정, 트래커 유형에 대해 질문
2. `dx-build-pipeline-app` 스킬과 트래커 툴셋 로드
3. `dx-agentic-dev/<session_id>/`에 파이프라인 생성 (요청 시 표준 경로에 직접)
4. 엘리먼트 가용성과 파이프라인 문법 검증
5. 실행 명령과 함께 보고

> **팁:** 이 프롬프트는 `dx_stream/`에서 직접 사용해도 동일하게 동작합니다.
> dx-runtime에서 작업하면 통합 라우팅과 모든 서브 프로젝트에 걸친
> `dx-validate-and-fix` 피드백 루프를 활용할 수 있습니다.

## 검증과 피드백 루프

dx-runtime 루트에서 다음 명령을 실행하세요:

```bash
# 모든 레벨 검증
python .deepx/scripts/validate_framework.py
python dx_app/.deepx/scripts/validate_framework.py
python dx_stream/.deepx/scripts/validate_framework.py

# 모든 검증기에서 피드백을 수집하여 단일 리포트로 생성
python .deepx/scripts/feedback_collector.py --all --output report.json

# 특정 서브 프로젝트로 범위 지정
python .deepx/scripts/feedback_collector.py --app-dirs dx_app --output report.json

# 적용 없이 제안된 수정 사항 미리보기
python .deepx/scripts/apply_feedback.py --report report.json --dry-run

# 모든 승인된 수정 적용
python .deepx/scripts/apply_feedback.py --report report.json --approve-all

# 특정 제안만 선택적으로 승인
python .deepx/scripts/apply_feedback.py --report report.json --approve FB-001,FB-003
```

검증 → 리뷰 → 수정 → 반복의 순환을 따릅니다.

## 스크립트 참조

| 스크립트 | 레벨 | 용도 |
|---------|------|------|
| `validate_framework.py` | dx-runtime | 통합 지식 베이스 구조 검증 |
| `validate_framework.py` | dx_app | dx_app 지식 베이스 및 생성된 앱 검증 |
| `validate_framework.py` | dx_stream | dx_stream 지식 베이스 및 파이프라인 검증 |
| `validate_app.py` | dx_app | 특정 생성된 애플리케이션 검증 |
| `validate_app.py` | dx_stream | 특정 생성된 파이프라인 앱 검증 |
| `feedback_collector.py` | dx-runtime | 모든 레벨의 검증 결과 집계 |
| `apply_feedback.py` | dx-runtime | 피드백 리포트에서 수정 사항 적용 |

## 지식 베이스 구조

각 `.deepx/` 디렉토리는 다음 구조를 따릅니다:

| 디렉토리 | 내용 |
|---------|------|
| `agents/` | 에이전트 정의 — 역할, 기능, 위임 규칙 |
| `skills/` | 앱 유형별 빌드 스킬 — 단계별 생성 워크플로우 |
| `instructions/` | 코딩 표준, 아키텍처 가이드라인, 임포트 규칙 |
| `toolsets/` | SDK/API 참조 — DxInfer, InferenceEngine, IFactory, GStreamer 엘리먼트 |
| `memory/` | 지속적 패턴과 함정 — 과거 빌드에서 학습한 내용 |
| `scripts/` | 검증 및 생성 도구 — 자동화를 위한 Python 스크립트 |
| `knowledge/` | 구조화된 YAML 데이터 — 모델 설정, 엘리먼트 카탈로그, 에러 매핑 |

dx-runtime `.deepx/`는 **횡단적** 지식(공유 규칙, 통합 검증)을 보유합니다.
서브 프로젝트 `.deepx/` 디렉토리는 **도메인별** 지식을 보유합니다.

## 문제 해결

| 문제 | 원인 | 해결 방법 |
|------|------|----------|
| 에이전트가 "skill not found" 표시 | 스킬 이름 오타 또는 `.deepx/skills/`에 파일 누락 | `ls .deepx/skills/`로 사용 가능한 스킬 확인 후 정확한 파일명 검증 |
| 검증에서 임포트 실패 | 생성된 코드가 절대 임포트 대신 상대 임포트 사용 | 빌더를 다시 실행 — 모든 에이전트가 `dx_app.*` 또는 `dx_stream.*`의 절대 임포트를 강제 |
| 모델 파일 미발견 (.dxnn) | 모델 미다운로드 또는 설정을 통한 경로 미해석 | `@dx-model-manager`를 실행하여 모델을 다운로드하고 `knowledge/models.yaml`에 등록 |
| `feedback_collector.py`가 빈 리포트 반환 | 아직 검증 스크립트가 실행되지 않음 | 먼저 각 레벨에서 `validate_framework.py`를 실행한 후 피드백 수집 |
| 파이프라인 엘리먼트 사용 불가 | DX GStreamer 플러그인 미설치 또는 `GST_PLUGIN_PATH`에 미포함 | `setup_env.sh`를 소싱하여 환경 변수를 설정하고 `gst-inspect-1.0`으로 플러그인 확인 |
| 에이전트가 잘못된 서브 프로젝트에 코드 생성 | dx_app과 dx_stream 간 모호한 요청 | 명확히 지정: dx_app은 "standalone", dx_stream은 "pipeline" 또는 "stream" 언급 |

## Session Sentinels

사용자 프롬프트를 처리할 때, 에이전트는 테스트 하니스의 자동 세션 경계 감지를 위해
다음 마커를 출력합니다:

| 마커 | 출력 시점 |
|------|----------|
| `[DX-AGENTIC-DEV: START]` | 에이전트 응답의 첫 번째 줄 |
| `[DX-AGENTIC-DEV: DONE (output-dir: <relative_path>)]` | 모든 작업 완료 후 마지막 줄. `<relative_path>`는 프로젝트 루트 기준 세션 출력 디렉토리의 상대 경로. 생성된 파일이 없으면 `(output-dir: ...)` 부분을 생략. |

규칙:
1. **필수** — 첫 번째 응답의 절대적 첫 줄에 `[DX-AGENTIC-DEV: START]`를 출력합니다. 다른 텍스트, tool call, reasoning보다 반드시 먼저 출력해야 합니다. 사용자가 "알아서 진행해"라고 해도 생략 불가 — 자동 테스트가 실패합니다.
2. 모든 작업, 검증, 파일 생성이 완료된 후 맨 마지막 줄에 DONE을 출력합니다.
3. handoff를 통해 호출된 sub-agent는 sentinel을 출력하지 않습니다 — 최상위 에이전트만 출력합니다.
4. 사용자가 한 세션에서 여러 프롬프트를 보내면, 각 프롬프트마다 START/DONE을 출력합니다.
5. DONE의 `output-dir`은 프로젝트 루트에서 세션 출력 디렉토리까지의 상대 경로여야 합니다.
6. **기획 산출물(spec, plan, 설계 문서)만 작성한 상태에서는 절대 DONE을 출력하지 마세요.** DONE은 모든 산출물(구현 코드, 스크립트, 설정 파일, 검증 결과)이 생성된 후에만 출력합니다.
