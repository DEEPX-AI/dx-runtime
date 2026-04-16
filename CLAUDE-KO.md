# DEEPX dx-runtime — Claude Code 진입점

> 3계층 DEEPX 지식 베이스 아키텍처를 위한 통합 진입점.

## 응답 언어

응답 언어를 사용자의 프롬프트 언어에 맞추세요 — 질문하거나
응답할 때, 사용자가 사용하는 언어와 동일한 언어를 사용하세요.

**기술 용어 규칙**: 한국어로 응답할 때, 영어 기술 용어는
원래 영어 형태를 유지하세요. 영어 용어를 한글 음차 표기로 변환하지 마세요
(한글 음차 표기 금지). 정착된 한국어 외래어(모델, 서버, 파일, 데이터)는 허용됩니다.

## 권장 모델 (사전 점검)

DX Agentic Development는 강력한 instruction following과 지식 베이스
활용 능력이 필요합니다. 작업을 시작하기 전에 권장 모델 중 하나로
실행 중인지 확인하세요:

- **Claude Sonnet 4.6** 이상
- **Claude Opus 4.6** 이상

이 모델이 아닌 경우 (예: GPT-4.1, GPT-4o, Gemini 등),
첫 번째 응답 시작 부분에 다음 알림을 출력하세요:

```
══════════════════════════════════════════════════════════════
⚠  DX-AGENTIC-DEV: MODEL NOTICE

DX Agentic Development recommends Claude Sonnet 4.6+ or
Opus 4.6+. Your current model may produce lower quality
in instruction following, knowledge base utilization, and
API accuracy. Please switch to a recommended model.
══════════════════════════════════════════════════════════════
```

박스 알림 후 작업을 정상적으로 진행하세요. 이것은 정보 제공용
경고이며 차단 게이트가 아닙니다.

### 모델 알림 반복 (비권장 모델만 해당)

위의 MODEL NOTICE 박스를 출력한 경우 (즉, 권장 모델이 아닌 경우),
사용자가 답해야 하는 **실제 질문 행 바로 앞에** 이 단축 리마인더를
반드시 출력해야 합니다 — brainstorming 흐름의 시작 부분이 아닙니다.

**타이밍**: 모든 파일 읽기, 컨텍스트 분석, 서문 텍스트 이후,
`?` (실제 질문)가 포함된 행 바로 앞에 이 리마인더를 삽입하세요:

```
---
⚠ **Non-recommended model** — output quality may be degraded. Recommended: Claude Sonnet 4.6+ / Opus 4.6+
---
```

**예시 — 잘못됨** (반복이 박스와 함께 스크롤됨):
```
[DX-AGENTIC-DEV: START]
══ MODEL NOTICE ══
---  ⚠ Non-recommended model ---     ← 너무 일찍, 스크롤됨
... (파일 읽기, 컨텍스트 분석) ...
첫 번째 질문: ...?
```

**예시 — 올바름** (반복이 질문 바로 앞에 표시):
```
[DX-AGENTIC-DEV: START]
══ MODEL NOTICE ══
... (파일 읽기, 컨텍스트 분석) ...
---  ⚠ Non-recommended model ---     ← 질문 바로 앞
첫 번째 질문: ...?
```

이 리마인더는 한 번만 (첫 번째 질문 앞에) 출력하세요. 매 질문마다 출력하지 마세요.

## 지식 베이스 아키텍처

| 계층 | 경로 | 범위 |
|-------|------|-------|
| **dx_app** | `dx_app/.deepx/` | Standalone inference (Python/C++, IFactory, SyncRunner/AsyncRunner) |
| **dx_stream** | `dx_stream/.deepx/` | GStreamer pipeline (13개 element, 6개 pipeline 카테고리) |
| **dx-runtime** (현재) | `.deepx/` | Integration 계층 — 프로젝트 간 패턴, 통합 라우팅 |

각 서브 프로젝트는 **자체 완결적**입니다. 이 계층은 프로젝트 간 오케스트레이션만 추가합니다.

## 라우팅 로직

작업 범위에 맞는 진입점을 읽으세요:

| 작업 대상... | 먼저 읽기 |
|---|---|
| dx_app 코드 (Python/C++ inference, IFactory, runner) | `dx_app/CLAUDE.md` |
| dx_stream 코드 (GStreamer pipeline, DxInfer, DxOsd) | `dx_stream/CLAUDE.md` |
| 프로젝트 간 통합 (공유 모델, 빌드 순서, 통합 테스팅) | 이 파일 + `.deepx/instructions/integration.md` |
| 어떤 서브 프로젝트인지 불확실 | 이 파일 — 아래 통합 컨텍스트 라우팅 테이블 사용 |

## 대화형 워크플로우 (반드시 따를 것)

**빌드 전에 항상 사용자와 핵심 결정 사항을 검토하세요.** 이것은 **HARD GATE**입니다.

앱 유형, 기능, 입력 소스를 확인하기 위해 2-3개의 타겟 질문을 하세요. 이를 통해
협업 워크플로우를 만들고 오해를 초기에 잡을 수 있습니다. 사용자가 명시적으로
"just build it" 또는 "use defaults"라고 말한 경우에만 질문을 건너뛰되 — 그 경우에도
빌드 계획을 제시하고 코드 생성 전 확인을 기다리세요.

## 빠른 참조

```bash
# dx_app
dx_app/install.sh && dx_app/build.sh   # Build C++ and pybind11 bindings
dx_app/setup.sh                        # Download models and test media

# dx_stream
dx_stream/install.sh                   # Install GStreamer plugin bindings
dx_stream/setup.sh                     # Download sample models and videos

# Verification
dxrt-cli -s                            # Verify NPU availability
gst-inspect-1.0 dxinfer                # Verify DxInfer plugin is registered
```

## 모든 Skills (병합)

### dx_app Skills

| 커맨드 | 설명 |
|---------|-------------|
| /dx-build-python-app | Python inference 앱 빌드 (sync, async, cpp_postprocess, async_cpp_postprocess) |
| /dx-build-cpp-app | InferenceEngine을 사용한 C++ inference 앱 빌드 |
| /dx-build-async-app | async 고성능 inference 앱 빌드 |

### dx_stream Skills

| 커맨드 | 설명 |
|---------|-------------|
| /dx-build-pipeline-app | GStreamer pipeline 앱 빌드 (6개 카테고리: single-model, multi-model, cascaded, tiled, parallel, broker) |
| /dx-build-mqtt-kafka-app | MQTT/Kafka message broker pipeline 앱 빌드 |

### 공유 Skills

| 커맨드 | 설명 |
|---------|-------------|
| /dx-model-management | .dxnn 모델 다운로드, 등록, 설정 |
| /dx-validate | 모든 phase gate에서 검증 체크 실행 |
| /dx-validate-and-fix | 전체 피드백 루프: 검증, 수집, 승인, 적용, 확인 |

### Process Skills (모든 계층에서 사용 가능)

| 커맨드 | 설명 |
|---------|-------------|
| /dx-brainstorm-and-plan | 프로세스: 코드 생성 전 협업 설계 세션 |
| /dx-tdd | 프로세스: 테스트 주도 개발 — 파일 생성 직후 즉시 검증 |
| /dx-verify-completion | 프로세스: 완료 선언 전 검증 — 주장 전 증거 |

## 통합 컨텍스트 라우팅 테이블

작업 내용에 따라 일치하는 행**만** 읽으세요:

| 작업에서 언급하는 내용... | 서브 프로젝트 | 읽을 파일 |
|---|---|---|
| **Python app, inference, factory** | dx_app | `dx_app/CLAUDE.md`, `dx_app/.deepx/skills/dx-build-python-app.md`, `dx_app/.deepx/toolsets/common-framework-api.md` |
| **C++ app, native, InferenceEngine** | dx_app | `dx_app/CLAUDE.md`, `dx_app/.deepx/skills/dx-build-cpp-app.md`, `dx_app/.deepx/toolsets/dx-engine-api.md` |
| **Async, performance, throughput** | dx_app | `dx_app/CLAUDE.md`, `dx_app/.deepx/skills/dx-build-async-app.md`, `dx_app/.deepx/memory/performance_patterns.md` |
| **Pipeline, GStreamer, stream** | dx_stream | `dx_stream/CLAUDE.md`, `dx_stream/.deepx/skills/dx-build-pipeline-app.md`, `dx_stream/.deepx/toolsets/dx-stream-elements.md` |
| **Multi-model, cascaded, tiled** | dx_stream | `dx_stream/CLAUDE.md`, `dx_stream/.deepx/skills/dx-build-pipeline-app.md`, `dx_stream/.deepx/toolsets/dx-stream-metadata.md` |
| **MQTT, Kafka, message broker** | dx_stream | `dx_stream/CLAUDE.md`, `dx_stream/.deepx/skills/dx-build-mqtt-kafka-app.md`, `dx_stream/.deepx/toolsets/dx-stream-elements.md` |
| **Model, download, registry** | shared | `dx_app/.deepx/skills/dx-model-management.md`, `dx_app/.deepx/toolsets/model-registry.md` |
| **Validation, testing** | shared | `dx_app/.deepx/skills/dx-validate.md`, `dx_app/.deepx/instructions/testing-patterns.md` |
| **Validation, feedback, fix** | dx-runtime | `.deepx/skills/dx-validate-and-fix.md`, `.deepx/knowledge/feedback_rules.yaml` |
| **Cross-project, integration** | dx-runtime | `.deepx/instructions/integration.md`, `.deepx/instructions/agent-protocols.md` |
| **항상 읽기 (모든 작업)** | dx-runtime | `.deepx/memory/common_pitfalls.md` |
| **Brainstorm, plan, design** | 모든 계층 | `.deepx/skills/dx-brainstorm-and-plan.md` |
| **TDD, validation, incremental** | 모든 계층 | `.deepx/skills/dx-tdd.md` |
| **Completion, verify, evidence** | 모든 계층 | `.deepx/skills/dx-verify-completion.md` |

## Python 임포트 (dx_app)

```python
from dx_app.src.python_example.common.runner.args import parse_common_args
from dx_app.src.python_example.common.runner.factory_runner import FactoryRunner
from dx_app.src.python_example.common.utils.model_utils import load_model_config
import logging

logger = logging.getLogger(__name__)
```

## 핵심 규칙

### 공통

1. **절대 임포트**: `from dx_app.src.python_example.common.xyz import ...`
2. **로깅**: `logging.getLogger(__name__)` — 단독 `print()` 금지
3. **하드코딩된 모델 경로 금지**: 모든 모델 경로는 CLI args, model_registry.json, 또는 model_list.json에서 가져올 것
4. **Skill 문서로 충분**: 먼저 skill 문서를 읽을 것. skill이 불충분한 경우가 아니면 소스 코드를 읽지 말 것.
5. **NPU 체크**: 모든 inference 작업 전에 `dxrt-cli -s` 실행

### dx_app 전용

6. **Factory 패턴**: 모든 앱은 5개 메서드를 가진 IFactory를 구현 (`create_preprocessor`, `create_postprocessor`, `create_visualizer`, `get_model_name`, `get_task_type`)
7. **CLI args**: `common/runner/args.py`의 `parse_common_args()` 사용
8. **4가지 변형**: Python 앱은 sync, async, sync_cpp_postprocess, async_cpp_postprocess를 가짐

### dx_stream 전용

9. **preprocess-id 매칭**: 모든 `DxPreprocess` / `DxInfer` 쌍은 동일한 `preprocess-id`를 공유해야 함
10. **Queue element**: 모든 GStreamer 처리 단계 사이에 `queue`를 배치
11. **RTSP용 DxRate**: RTSP 소스 후 항상 `DxRate rate=<fps>` 삽입
12. **DxMsgBroker 전에 DxMsgConv**: 발행 전 항상 metadata를 직렬화

### 통합

13. **빌드 순서**: dx_app 먼저, 그다음 dx_stream (dx_stream은 dx_app 라이브러리에 링크)
14. **공유 .dxnn 모델**: 두 서브 프로젝트 모두 `dx_app/config/model_registry.json`을 단일 진실 소스로 공유
15. **임포트 경로**: dx_stream은 dx_app에서 임포트 가능 — 반대는 절대 불가
16. **PPU 모델 자동 감지**: 컴파일된 .dxnn 모델 작업 시, 모델 이름 접미사(`_ppu`), `model_registry.json`의 `csv_task: "PPU"`, 또는 사용자 컨텍스트를 확인하여 PPU를 자동 감지. PPU 모델은 간소화된 postprocessing 사용 — 별도 NMS 불필요.
17. **기존 예제 검색**: 새 예제 코드를 생성하기 전 항상 기존 예제를 검색. 발견되면 사용자에게 옵션 제시: (a) 기존 코드 설명만, 또는 (b) 기존 코드 기반으로 새로 생성. 무단 덮어쓰기 금지.

## 플레이스홀더 코드 금지 (필수)

스텁/플레이스홀더 코드를 절대 생성하지 마세요. 여기에 포함되는 것:
- 주석 처리된 임포트: `# from dxnn_sdk import InferenceEngine`
- 가짜 결과: `result = np.zeros(...)`
- TODO 마커: `# TODO: implement actual inference`
- 실제 async 구현 없이 "sync 버전과 유사"

모든 생성 코드는 지식 베이스의 실제 API를 사용하여 기능적이어야 합니다.
필요한 SDK/API를 모르는 경우 먼저 관련 skill 문서를 읽으세요.

## 실험적 기능 — 금지

실험적이거나 존재하지 않는 기능을 제안, 추천, 또는 구현하지 마세요. 여기에 포함되는 것:
- "웹 기반 비주얼 컴패니언" (web-based visual companion)
- 로컬 URL 기반 다이어그램 뷰어 또는 대시보드
- 사용자가 시각화를 위해 로컬 URL을 열어야 하는 모든 기능
- 현재 도구 세트에 존재하지 않는 모든 기능

**Superpowers brainstorming skill 오버라이드**: superpowers `brainstorming` skill에는
"Visual Companion" 단계 (체크리스트의 2단계)가 포함되어 있습니다. 이 단계는
DEEPX 프로젝트에서 반드시 건너뛰어야 합니다. visual companion은 우리 환경에 존재하지 않습니다.
brainstorming 체크리스트에서 "Offer visual companion"이라고 표시되면, 건너뛰고
"Ask clarifying questions" (3단계)로 직접 진행하세요.

기능이 존재하지 않으면 존재하는 척하지 마세요. 검증된 문서화된
기능만 사용하세요.

**Autopilot / autonomous 모드 오버라이드**: 사용자가 부재 시 (autopilot 모드,
auto-response "work autonomously", 또는 `--yolo` 플래그), brainstorming skill의
"Ask clarifying questions" 단계를 "지식 베이스 규칙에 따른 기본 결정"으로 대체해야 합니다.
`ask_user`를 호출하지 마세요 — 지식 베이스 기본값을 사용하여 brainstorming spec을
바로 생성하세요. 이후의 모든 게이트 (spec 검토, plan, TDD, 필수 산출물, 실행 검증)는
예외 없이 적용됩니다.

## Brainstorming — Plan 전 Spec (HARD GATE)

superpowers `brainstorming` skill 또는 `/dx-brainstorm-and-plan` 사용 시:

1. **Spec 문서는 필수** — `writing-plans`로 전환하기 전, spec
   문서를 `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`에 반드시 작성해야 합니다.
   spec을 건너뛰고 바로 plan 작성으로 가는 것은 위반입니다.
2. **사용자 승인 게이트는 필수** — spec 작성 후, 사용자가 반드시 검토하고
   승인해야 plan 작성을 진행할 수 있습니다. 관련 없는 사용자 응답
   (예: 다른 질문에 대한 답변)을 spec 승인으로 취급하지 마세요.
3. **Plan 문서는 spec을 참조해야 함** — plan 헤더에 승인된 spec 문서에 대한
   링크를 포함해야 합니다.
4. **`/dx-brainstorm-and-plan` 우선** — 범용 superpowers `brainstorming` skill 대신
   프로젝트 수준의 brainstorming skill을 사용하세요. 프로젝트 수준 skill에는
   도메인별 질문과 사전 점검이 있습니다.

## 자율 모드 보호 (필수)

사용자가 부재 시 — autopilot 모드, `--yolo` 플래그, 또는 시스템 auto-response
"The user is not available to respond" — 다음 규칙이 적용됩니다:

1. **"자율적으로 작업하라"는 "묻지 않고 모든 규칙을 따르라"는 뜻이지, "규칙을 건너뛰라"가 아닙니다.**
   모든 필수 게이트가 여전히 적용됩니다: brainstorming spec, plan, TDD, 필수
   산출물, 실행 검증, 자체 검증 체크.
2. **`ask_user`를 호출하지 마세요** — 지식 베이스 기본값과 문서화된 모범 사례를 사용하여
   결정하세요. autopilot에서 `ask_user` 호출은 턴을 낭비하며
   auto-response는 어떤 게이트도 우회할 권한을 부여하지 않습니다.
3. **사용자 승인 게이트 적응** — autopilot에서 spec 승인 게이트는
   spec을 작성하고 지식 베이스에 대해 자체 검토함으로써 충족됩니다.
   spec 자체를 건너뛰지 마세요.
4. **setup.sh 먼저** — 애플리케이션 코드 작성 전에 인프라 산출물(`setup.sh`, `config.json`)을
   생성하세요. 이는 autopilot에서 특히 중요합니다.
   누락된 의존성을 잡아줄 사람이 없기 때문입니다.
5. **실행 검증은 선택이 아닙니다** — 생성된 코드를 실행하고 완료 선언 전에
   작동을 확인하세요. autopilot에서는 오류를 잡아줄 사용자가 없습니다.

## 하드웨어

| 아키텍처 | 값 | 용도 |
|---|---|---|
| DX-M1 | `dx_m1` | 풀 성능 NPU |

## 메모리

`.deepx/memory/`에 영속 지식이 있습니다. 작업 시작 시 읽고, 학습 시 업데이트하세요.
통합 `common_pitfalls.md`에는 [UNIVERSAL], [DX_APP], [DX_STREAM], [INTEGRATION] 태그가 붙은 항목이 있습니다.

## 테스팅

```bash
cd dx_app && pytest tests/
cd dx_stream && pytest test/
python .deepx/scripts/validate_framework.py
```

## Git 안전 — Superpowers 산출물

**`docs/superpowers/` 아래 파일을 절대 `git add` 또는 `git commit`하지 마세요.** 이것은
superpowers skill 시스템이 생성한 임시 계획 산출물(spec, plan)입니다.
`.gitignore` 처리되어 있지만, 일부 도구가 `git add -f`로 `.gitignore`를 우회할 수 있습니다.
파일을 만드는 것은 괜찮지만 — 커밋하는 것은 금지입니다.

## Session Sentinel (자동화 테스트용 필수)

사용자 프롬프트를 처리할 때, 테스트 하네스의 자동화된 세션
경계 감지를 위해 다음 정확한 마커를 출력하세요:

- **응답의 첫 번째 행**: `[DX-AGENTIC-DEV: START]`
- **모든 작업 완료 후 마지막 행**: `[DX-AGENTIC-DEV: DONE (output-dir: <relative_path>)]`
  여기서 `<relative_path>`는 세션 출력 디렉토리입니다 (예: `dx-agentic-dev/20260409-143022_yolo26n_detection/`)

규칙:
1. **중요 — 첫 번째 응답의 절대적 첫 행으로 `[DX-AGENTIC-DEV: START]`를 출력하세요.**
   이것은 다른 모든 텍스트, 도구 호출, 또는 추론보다 앞에 나와야 합니다.
   사용자가 "그냥 진행해" 또는 "판단에 맡기겠다"라고 지시하더라도,
   START sentinel은 협상 불가입니다 — 자동화 테스트가 이것 없이는 실패합니다.
2. 모든 작업, 검증, 파일 생성이 완료된 후 마지막 행으로 `[DX-AGENTIC-DEV: DONE (output-dir: <path>)]`를 출력
3. 상위 에이전트의 handoff/routing으로 호출된 **서브 에이전트**인 경우,
   이 sentinel을 출력하지 마세요 — 최상위 에이전트만 출력합니다
4. 사용자가 세션에서 여러 프롬프트를 보내면, 각 프롬프트마다 START/DONE 출력
5. DONE의 `output-dir`은 프로젝트 루트에서 세션 출력 디렉토리까지의 상대 경로여야 합니다.
   파일이 생성되지 않은 경우, `(output-dir: ...)` 부분을 생략합니다.
6. **계획 산출물만 생성한 후에는 절대 DONE을 출력하지 마세요** (spec, plan, 설계
   문서). DONE은 모든 산출물이 생성되었음을 의미합니다 — 구현 코드, 스크립트,
   설정, 검증 결과. brainstorming 또는 계획 단계만 완료하고 실제 코드를
   아직 구현하지 않은 경우, DONE을 출력하지 마세요. 대신 구현을 진행하거나
   사용자에게 진행 방법을 물어보세요.
7. **DONE 전 필수 산출물 체크**: DONE 출력 전, 모든 필수 산출물이
   세션 디렉토리에 존재하는지 확인하세요. 필수 파일이 누락된 경우
   DONE 출력 전에 생성하세요. 각 서브 프로젝트는 skill 문서에 자체 필수
   파일 목록을 정의합니다 (예: `dx-build-pipeline-app.md` File Creation Checklist).
8. **세션 HTML 내보내기 안내** (Copilot CLI 전용): DONE sentinel 행 바로 앞에
   다음을 출력: `To save this session as HTML, type: /share html`
   — 이는 사용자에게 전체 대화를 보존할 수 있음을 알려줍니다. `/share html`
   커맨드는 GitHub Copilot CLI에만 해당됩니다; Claude Code,
   Copilot Chat (VS Code), 또는 OpenCode에서는 작동하지 않습니다. 테스트 하네스(`test.sh`)가
   내보낸 HTML 파일을 자동으로 감지하여 세션 출력 디렉토리에 복사합니다.

## Plan 출력 (필수)

plan 문서를 생성할 때 (예: writing-plans 또는 brainstorming skill을 통해),
파일 저장 직후 **전체 plan 내용을 대화 출력에 반드시 인쇄하세요.**
파일 경로만 언급하지 마세요 — 사용자가 별도 파일을 열지 않고도
프롬프트에서 직접 plan을 검토할 수 있어야 합니다.

## 출력 격리 (HARD GATE)

모든 AI 생성 파일은 대상 서브 프로젝트 내의 `dx-agentic-dev/<session_id>/`에
반드시 작성해야 합니다. 기존 소스 디렉토리에 생성 코드를 직접 쓰지 마세요
(예: `src/`, `pipelines/`, `semseg_260323/`, 또는 사용자의 기존 코드가 포함된 모든 디렉토리).

**세션 ID 형식**: `YYYYMMDD-HHMMSS_<model>_<task>` — 타임스탬프는
**시스템 로컬 시간대**를 사용해야 합니다 (UTC 아님). Bash에서 `$(date +%Y%m%d-%H%M%S)` 또는
Python에서 `datetime.now().strftime('%Y%m%d-%H%M%S')` 사용. `date -u`,
`datetime.utcnow()`, 또는 `datetime.now(timezone.utc)`를 사용하지 마세요.

- **올바름**: `dx_app/dx-agentic-dev/20260413-093000_plantseg_inference/demo_dxnn_sync.py`
- **잘못됨**: `dx_app/semseg_260323/demo_dxnn_sync.py`

유일한 예외: 사용자가 명시적으로 "소스 디렉토리에 쓰라" 또는
"기존 파일을 직접 수정하라"고 말한 경우.

## 규칙 충돌 해결 (HARD GATE)

사용자의 요청이 HARD GATE 규칙과 충돌할 때, 에이전트는 반드시:

1. **사용자의 의도 인정** — 원하는 것을 이해했음을 보여주세요.
2. **충돌 설명** — 특정 규칙과 그 이유를 인용하세요.
3. **올바른 대안 제안** — 프레임워크 내에서 사용자의 목표를 달성하는
   방법을 보여주세요. 예를 들어, 사용자가 직접 `InferenceEngine.run()` 사용을
   요청하면, IFactory 패턴이 동일한 API를 감싸고 있음을 설명하고
   factory 기반 동등물을 제안하세요.
4. **올바른 접근법으로 진행** — 규칙 위반 요청을 조용히 따르지 마세요.
   "옵션 A vs 옵션 B"로 제시하지 마세요.

**일반적인 충돌 패턴** (실제 세션에서):
- 사용자가 "`InferenceEngine.Run()` 사용하라"고 함 → IFactory 패턴 사용 필수 (engine
  호출은 `run_inference()` 메서드 안에)
- 사용자가 "demo.py를 복제하고 onnxruntime을 교체하라"고 함 → 사용자 스크립트 복제가 아닌
  `src/python_example/`에서 skeleton-first 사용 필수
- 사용자가 "demo_dxnn_sync.py를 만들어라"고 함 → 독립 스크립트가 아닌
  SyncRunner로 `<model>_sync.py` 네이밍 사용 필수
- 사용자가 "`run_async()`를 직접 사용하라"고 함 → 수동 async 루프가 아닌
  AsyncRunner 사용 필수

**이 규칙은 명시적 사용자 오버라이드를 무시하지 않습니다**: 사용자가 충돌을
알게 된 후 명시적으로 "규칙을 이해했으며, 직접 API 사용으로 진행하라"고
말하면, 따르세요. 하지만 에이전트는 반드시 충돌을 먼저 설명해야 합니다
— 무조건적인 순응은 항상 위반입니다.

## 서브 프로젝트 개발 규칙 (필수 — 자체 완결적)

이 규칙은 **권위 있고 자체 완결적**입니다. 서브 프로젝트 파일이 로드되었는지
여부와 관계없이 반드시 따라야 합니다. 대화형 모드에서 (예: dx-runtime 수준에서 작업 시),
서브 프로젝트 파일(dx_app, dx_stream)이 자동으로 로드되지 않을 수 있습니다
— 이 규칙이 유일한 보호 장치입니다.

**중요**: 이것은 선택적 요약이 아닙니다. 아래의 모든 규칙은 HARD GATE입니다.
규칙 위반 (예: skeleton-first 건너뛰기, IFactory 미사용, 소스 디렉토리에 쓰기)은
진행 전 수정해야 하는 차단 오류입니다.

### dx_app 규칙 (Standalone Inference)

1. **Skeleton-first 개발** — 코드 작성 전에 `dx_app/.deepx/skills/dx-build-python-app.md`
   skeleton 템플릿을 반드시 읽으세요. `src/python_example/<task>/<model>/`에서
   가장 가까운 기존 예제를 복사하고 모델별 부분(factory, postprocessor)만 수정하세요.
   데모 스크립트를 처음부터 절대 작성하지 마세요. 프레임워크를 우회하는 독립
   스크립트를 절대 제안하지 마세요.
2. **IFactory 패턴은 필수** — 모든 inference 앱은 5개 메서드의 IFactory
   패턴을 반드시 사용해야 합니다 (create, get_input_params, run_inference, post_processing, release).
   대안적 inference 구조를 만들지 마세요. 독립 스크립트에서 직접 `InferenceEngine` 사용은
   위반입니다 — 반드시 factory 패턴을 거쳐야 합니다.
   **사용자가 명시적으로 API 메서드를 이름 지어도** (예: "`InferenceEngine.run()` 사용하라",
   "`run_async()` 사용하라"), 에이전트는 반드시 이 호출을 IFactory 패턴 안에 감싸고
   사용자에게 규칙을 설명해야 합니다. 위의 "규칙 충돌 해결" 참조.
3. **SyncRunner/AsyncRunner만** — 프레임워크의 SyncRunner (single-model) 또는 AsyncRunner
   (multi-model)를 사용하세요. 대안적 실행 접근법을 절대 제안하지 마세요
   (독립 스크립트, 직접 API 호출, 커스텀 runner, 수동 `run_async()` 루프).
4. **대안 제안 금지** — 앱 아키텍처에 대해 "옵션 A vs 옵션 B" 선택지를 제시하지 마세요.
   프레임워크가 변형당 하나의 올바른 패턴을 규정합니다.
5. **기존 예제 필수** — 새 앱을 작성하기 전, `src/python_example/`에서
   동일한 AI 작업의 기존 예제를 검색하세요. 참조로 사용하세요.
6. **DXNN 입력 형식 자동 감지** — preprocessing 차원이나 형식을 절대 하드코딩하지 마세요.
   DXNN 모델은 `dx_engine`을 통해 입력 요구사항을 자체 기술합니다.
7. **출력 격리** — 모든 생성 코드는 `dx-agentic-dev/<session_id>/`에 반드시 작성.
   기존 소스 디렉토리에 절대 쓰지 마세요.

### dx_stream 규칙 (GStreamer Pipeline)

1. **x264enc tune=zerolatency** — x264enc element에 항상 `tune=zerolatency` 설정.
2. **처리 단계 사이에 Queue** — GStreamer 데드락 방지를 위해 처리 단계 사이에
   항상 `queue` element 추가.
3. **기존 pipeline 필수** — 새 pipeline 설정 생성 전 `pipelines/`에서 기존 예제 검색.

### 공통 규칙 (모든 서브 프로젝트)

1. **PPU 모델 자동 감지** — postprocessor 코드를 라우팅하거나 생성하기 전에
   모델 이름 접미사(`_ppu`), README, 또는 registry에서 PPU 플래그 확인.
   PPU 모델은 간소화된 postprocessing 사용 — 별도 NMS 불필요.
2. **빌드 순서** — dx_rt → dx_app → dx_stream. 순서를 어기지 마세요.
3. **서브 프로젝트 컨텍스트 로딩** — 서브 프로젝트로 라우팅하거나 작업할 때,
   해당 서브 프로젝트의 `CLAUDE.md`를 항상 먼저 읽으세요.
