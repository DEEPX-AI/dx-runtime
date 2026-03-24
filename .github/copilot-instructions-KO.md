# DEEPX dx-runtime — Copilot 전역 지침

> 3단계 DEEPX 지식 베이스 아키텍처를 위한 통합 진입점.

## 응답 언어

응답 언어는 사용자의 프롬프트 언어에 맞추십시오 — 질문하거나
응답할 때 사용자가 사용하는 언어와 동일한 언어를 사용하십시오.

**기술 용어 규칙**: 한국어로 응답할 때, 영어 기술 용어는
원래 영어 형태를 유지하십시오. 영어 용어를 한글 음차로 표기하지 마십시오
(한글 음차 표기 금지). 정착된 한국어 외래어(모델, 서버, 파일, 데이터)는 허용됩니다.

## 권장 모델 (사전 점검)

DX Agentic Development는 강력한 지시 따르기와 지식 베이스
활용 능력이 필요합니다. 작업을 시작하기 전에, 현재 권장 모델 중 하나로
실행 중인지 확인하십시오:

- **Claude Sonnet 4.6** 이상
- **Claude Opus 4.6** 이상

이 모델이 아닌 경우(예: GPT-4.1, GPT-4o, Gemini 등),
첫 번째 응답 시작 부분에 다음 안내를 출력하십시오:

```
══════════════════════════════════════════════════════════════
⚠  DX-AGENTIC-DEV: MODEL NOTICE

DX Agentic Development recommends Claude Sonnet 4.6+ or
Opus 4.6+. Your current model may produce lower quality
in instruction following, knowledge base utilization, and
API accuracy. Please switch to a recommended model.
══════════════════════════════════════════════════════════════
```

안내 상자 출력 후, 정상적으로 작업을 진행하십시오. 이것은 정보성
경고이며, 차단 게이트가 아닙니다.

### 모델 안내 반복 (비권장 모델만 해당)

위의 MODEL NOTICE 상자를 출력한 경우(즉, 권장 모델이 아닌 경우),
사용자가 답변해야 하는 **실제 질문 줄 바로 앞에** 이 축약된 알림을
**반드시** 출력해야 합니다 — brainstorming 흐름의 시작 부분이 아닙니다.

**타이밍**: 모든 파일 읽기, 컨텍스트 분석, 서문 텍스트 후에,
`?`(실제 질문)가 포함된 줄 바로 앞에 이 알림을 삽입하십시오:

```
---
⚠ **Non-recommended model** — output quality may be degraded. Recommended: Claude Sonnet 4.6+ / Opus 4.6+
---
```

**예시 — 잘못된 경우** (반복이 상자와 함께 스크롤됨):
```
[DX-AGENTIC-DEV: START]
══ MODEL NOTICE ══
---  ⚠ Non-recommended model ---     ← 너무 이름, 스크롤됨
... (파일 읽기, 컨텍스트 분석) ...
First question: ...?
```

**예시 — 올바른 경우** (반복이 질문 바로 앞에 표시됨):
```
[DX-AGENTIC-DEV: START]
══ MODEL NOTICE ══
... (파일 읽기, 컨텍스트 분석) ...
---  ⚠ Non-recommended model ---     ← 질문 바로 앞
First question: ...?
```

이 알림은 한 번만 출력하십시오(첫 번째 질문 전에만), 매 질문마다 출력하지 마십시오.

## 지식 베이스 아키텍처

| 레벨 | 경로 | 범위 |
|---|---|---|
| **dx_app** | `dx_app/.deepx/` | 독립형 추론 앱 (Python/C++) |
| **dx_stream** | `dx_stream/.deepx/` | GStreamer 파이프라인 앱 |
| **dx-runtime** | `.deepx/` | 크로스 프로젝트 통합 레이어 |

**dx_app 코드 작업 시** — `dx_app/.github/copilot-instructions.md`를 먼저 읽은 후, `dx_app/.deepx/` skill과 toolset을 읽으십시오.
**dx_stream 코드 작업 시** — `dx_stream/.github/copilot-instructions.md`를 먼저 읽은 후, `dx_stream/.deepx/` skill과 toolset을 읽으십시오.
**양쪽 모두 작업 시** — `.deepx/instructions/integration.md`를 읽으십시오.

## 빠른 참조

```bash
cd dx_app && ./install.sh && ./build.sh
cd dx_stream && ./install.sh
cd dx_app && ./setup.sh
cd dx_stream && ./setup.sh
cd dx_app && pytest tests/
cd dx_stream && pytest test/
python .deepx/scripts/validate_framework.py
```

## 모든 Skill (통합)

### dx_app Skill

| 명령 | 설명 |
|---------|-------------|
| /dx-build-python-app | Python 추론 앱 빌드 (sync, async, cpp_postprocess, async_cpp_postprocess) |
| /dx-build-cpp-app | InferenceEngine을 사용한 C++ 추론 앱 빌드 |
| /dx-build-async-app | 비동기 고성능 추론 앱 빌드 |

### dx_stream Skill

| 명령 | 설명 |
|---------|-------------|
| /dx-build-pipeline-app | GStreamer 파이프라인 앱 빌드 (6가지 카테고리: single-model, multi-model, cascaded, tiled, parallel, broker) |
| /dx-build-mqtt-kafka-app | MQTT/Kafka 메시지 브로커 파이프라인 앱 빌드 |

### 공유 Skill

| 명령 | 설명 |
|---------|-------------|
| /dx-model-management | .dxnn 모델 다운로드, 등록 및 구성 |
| /dx-validate | 모든 단계 게이트에서 검증 검사 실행 |
| /dx-validate-and-fix | 전체 피드백 루프: 검증, 수집, 승인, 적용, 확인 |

### 프로세스 Skill (모든 레벨에서 사용 가능)

| 명령 | 설명 |
|---------|-------------|
| /dx-brainstorm-and-plan | 프로세스: 코드 생성 전 협업 설계 세션 |
| /dx-tdd | 프로세스: 테스트 주도 개발 — 생성 직후 각 파일 검증 |
| /dx-verify-completion | 프로세스: 완료 선언 전 검증 — 주장 전 증거 |

## 대화형 워크플로우 (MUST FOLLOW)

**빌드 전에 항상 사용자와 핵심 결정을 함께 검토하십시오.** 이것은 **HARD GATE**입니다.

코드 생성 전에 반드시:
1. 2-3개의 명확화 질문을 하십시오 (앱 유형/변형, AI 작업, 입력 소스)
2. 빌드 계획을 제시하고 사용자 승인을 기다리십시오
3. 생성 후 각 파일을 검증하십시오

"그냥 만들어"는 기본값을 사용하라는 의미입니다 — brainstorming을 건너뛰라는 의미가 아닙니다.

사용자가 명시적으로 "그냥 만들어" 또는 "기본값 사용"이라고 말한 경우에만 질문을
건너뛰십시오 — 그러나 그때에도 코드 생성 전에 빌드 계획을 제시하고 확인을
기다리십시오.

## 통합 컨텍스트 라우팅 테이블

| 작업이 언급하는 내용... | 서브 프로젝트 | 읽어야 할 파일 |
|---|---|---|
| **Python 앱, 추론, factory** | dx_app | `dx_app/.github/copilot-instructions.md`, `dx_app/.deepx/skills/dx-build-python-app.md`, `dx_app/.deepx/toolsets/common-framework-api.md` |
| **C++ 앱, native, InferenceEngine** | dx_app | `dx_app/.github/copilot-instructions.md`, `dx_app/.deepx/skills/dx-build-cpp-app.md`, `dx_app/.deepx/toolsets/dx-engine-api.md` |
| **Async, 고처리량, batch** | dx_app | `dx_app/.github/copilot-instructions.md`, `dx_app/.deepx/skills/dx-build-async-app.md`, `dx_app/.deepx/memory/performance_patterns.md` |
| **Pipeline, GStreamer, stream** | dx_stream | `dx_stream/.github/copilot-instructions.md`, `dx_stream/.deepx/skills/dx-build-pipeline-app.md`, `dx_stream/.deepx/toolsets/dx-stream-elements.md` |
| **Multi-model, cascaded, tiled** | dx_stream | `dx_stream/.github/copilot-instructions.md`, `dx_stream/.deepx/skills/dx-build-pipeline-app.md`, `dx_stream/.deepx/toolsets/dx-stream-metadata.md` |
| **MQTT, Kafka, message broker** | dx_stream | `dx_stream/.github/copilot-instructions.md`, `dx_stream/.deepx/skills/dx-build-mqtt-kafka-app.md`, `dx_stream/.deepx/toolsets/dx-stream-elements.md` |
| **모델, 다운로드, registry** | shared | `dx_app/.deepx/skills/dx-model-management.md`, `dx_app/.deepx/toolsets/model-registry.md` |
| **검증, 테스팅** | shared | `dx_app/.deepx/skills/dx-validate.md`, `dx_app/.deepx/instructions/testing-patterns.md` |
| **검증, 피드백, 수정** | dx-runtime | `.deepx/skills/dx-validate-and-fix.md`, `.deepx/knowledge/feedback_rules.yaml` |
| **크로스 프로젝트, 통합** | dx-runtime | `.deepx/instructions/integration.md`, `.deepx/instructions/agent-protocols.md` |
| **항상 읽기 (모든 작업)** | dx-runtime | `.deepx/memory/common_pitfalls.md` |
| **Brainstorm, 계획, 설계** | 모든 레벨 | `.deepx/skills/dx-brainstorm-and-plan.md` |
| **TDD, 검증, 점진적** | 모든 레벨 | `.deepx/skills/dx-tdd.md` |
| **완료, 확인, 증거** | 모든 레벨 | `.deepx/skills/dx-verify-completion.md` |

## 핵심 규칙

### 범용

1. **절대 import**: `from dx_app.src.python_example.common.xyz import ...`
2. **로깅**: `logging.getLogger(__name__)` — 단독 `print()` 사용 금지
3. **하드코딩된 모델 경로 금지**: 모든 모델 경로는 CLI 인자, model_registry.json, 또는 model_list.json에서 가져와야 함
4. **Skill 문서로 충분**: Skill 문서를 먼저 읽으십시오. 소스 코드는 skill이 불충분한 경우에만 읽으십시오.
5. **NPU 확인**: 모든 추론 작업 전에 `dxrt-cli -s` 실행

### dx_app 전용

6. **Factory 패턴**: 모든 앱은 5개 메서드를 가진 IFactory를 구현해야 함 (`create_preprocessor`, `create_postprocessor`, `create_visualizer`, `get_model_name`, `get_task_type`)
7. **CLI 인자**: `common/runner/args.py`의 `parse_common_args()` 사용
8. **4가지 변형**: Python 앱은 sync, async, sync_cpp_postprocess, async_cpp_postprocess 변형이 있음

### dx_stream 전용

9. **preprocess-id 매칭**: 모든 `DxPreprocess` / `DxInfer` 쌍은 동일한 `preprocess-id`를 공유해야 함
10. **Queue 요소**: 모든 GStreamer 처리 단계 사이에 `queue`를 배치해야 함
11. **RTSP용 DxRate**: RTSP 소스 뒤에 항상 `DxRate rate=<fps>` 삽입
12. **DxMsgBroker 전에 DxMsgConv**: 게시 전에 항상 메타데이터를 직렬화해야 함

### 통합

13. **빌드 순서**: dx_app을 먼저, 그 다음 dx_stream (dx_stream은 dx_app 라이브러리에 링크됨)
14. **공유 .dxnn 모델**: 양쪽 서브 프로젝트 모두 `dx_app/config/model_registry.json`을 단일 소스로 공유
15. **Import 경로**: dx_stream은 dx_app에서 import 가능 — 역방향은 불가
16. **PPU 모델 자동 감지**: 컴파일된 .dxnn 모델 작업 시, 모델 이름 접미사(`_ppu`), `model_registry.json`의 `csv_task: "PPU"`, 또는 사용자 컨텍스트를 확인하여 PPU를 자동 감지하십시오. PPU 모델은 단순화된 후처리를 사용합니다 — 별도의 NMS 불필요.
17. **기존 예제 검색**: 새 예제 코드를 생성하기 전에, 항상 기존 예제를 검색하십시오. 발견된 경우, 사용자에게 선택지를 제시하십시오: (a) 기존 코드 설명만, 또는 (b) 기존 코드 기반으로 새로 생성. 무단으로 덮어쓰지 마십시오.

## 플레이스홀더 코드 금지 (MANDATORY)

스텁/플레이스홀더 코드를 절대 생성하지 마십시오. 이에 해당하는 것:
- 주석 처리된 import: `# from dxnn_sdk import InferenceEngine`
- 가짜 결과: `result = np.zeros(...)`
- TODO 마커: `# TODO: implement actual inference`
- 실제 async 구현 없이 "sync 버전과 유사"

모든 생성된 코드는 지식 베이스의 실제 API를 사용하여 기능적이어야 합니다.
필요한 SDK/API를 모르는 경우, 관련 skill 문서를 먼저 읽으십시오.

## 실험적 기능 — 금지

실험적이거나 존재하지 않는 기능을 제안, 제시, 또는 구현하지 마십시오. 이에 해당하는 것:
- "웹 기반 비주얼 컴패니언" (web-based visual companion)
- 로컬 URL 기반 다이어그램 뷰어 또는 대시보드
- 사용자에게 시각화를 위해 로컬 URL을 열도록 요구하는 기능
- 현재 toolset에 존재하지 않는 모든 기능

**Superpowers brainstorming skill 재정의**: superpowers `brainstorming` skill에는
"Visual Companion" 단계(체크리스트의 2단계)가 포함되어 있습니다. 이 단계는 DEEPX
프로젝트에서 반드시 건너뛰어야 합니다. Visual companion은 우리 환경에 존재하지 않습니다.
brainstorming 체크리스트에서 "Offer visual companion"이라고 되어 있으면, 건너뛰고
"Ask clarifying questions" (3단계)로 바로 진행하십시오.

기능이 존재하지 않으면, 존재하는 척하지 마십시오. 검증된, 문서화된
기능만 사용하십시오.

**자율 모드 보호 재정의**: 사용자가 부재 시(autopilot 모드,
자동 응답 "work autonomously", 또는 `--yolo` 플래그), brainstorming skill의
"Ask clarifying questions" 단계는 "지식 베이스 규칙에 따라 기본 결정 내리기"로
대체되어야 합니다. `ask_user`를 호출하지 마십시오 — 지식 베이스 기본값을 사용하여
brainstorming 스펙 작성으로 바로 진행하십시오. 이후의 모든 게이트(스펙 검토,
계획, TDD, 필수 산출물, 실행 검증)는 예외 없이 적용됩니다.

## 자율 모드 보호 (MANDATORY)

사용자가 부재 시 — autopilot 모드, `--yolo` 플래그, 또는 시스템 자동 응답
"The user is not available to respond" — 다음 규칙이 적용됩니다:

1. **"자율적으로 작업하라"는 "질문 없이 모든 규칙을 따르라"는 의미이며, "규칙을 건너뛰라"는 의미가 아닙니다.**
   모든 MANDATORY 게이트가 여전히 적용됩니다: brainstorming 스펙, 계획, TDD, 필수
   산출물, 실행 검증, 자체 검증 확인.
2. **`ask_user`를 호출하지 마십시오** — 지식 베이스 기본값과
   문서화된 모범 사례를 사용하여 결정을 내리십시오. autopilot에서 `ask_user` 호출은 턴을 낭비하며
   자동 응답은 어떤 게이트도 우회할 권한을 부여하지 않습니다.
3. **사용자 승인 게이트 적응** — autopilot에서, 스펙 승인 게이트는
   스펙을 작성하고 지식 베이스에 대해 자체 검토하는 것으로 충족됩니다.
   스펙 자체를 건너뛰지 마십시오.
4. **setup.sh 우선** — 애플리케이션 코드를 작성하기 전에 인프라 산출물(`setup.sh`, `config.json`)을
   먼저 생성하십시오. 이는 autopilot에서 특히 중요합니다.
   누락된 종속성을 잡아줄 사람이 없기 때문입니다.
5. **실행 검증은 선택 사항이 아닙니다** — 생성된 코드를 실행하고 완료 선언 전에
   작동하는지 확인하십시오. autopilot에서는 오류를 잡아줄 사용자가 없습니다.
6. **시간 예산 인식** — autopilot 세션에는 시간 제약이 있을 수 있습니다.
   행동을 효율적으로 계획하세요:
   - 컴파일 (ONNX → DXNN)은 5분 이상 걸릴 수 있습니다 — 일찍 시작하세요.
   - 시간이 부족하면 실행 검증보다 산출물 생성을 우선시하세요 — 테스트되지 않은
     완전한 파일 세트가 테스트된 불완전한 세트보다 낫습니다.
   - 우선순위: `setup.sh` > `run.sh` > 앱 코드 > `verify.py` > session.log.
   - **컴파일 병렬 워크플로 (HARD GATE)** — `dxcom` 또는 `dx_com.compile()`을
     bash 명령으로 시작한 후 기다리지 마세요. 즉시 모든 필수 산출물을 생성하세요:
     factory, 앱 코드, setup.sh, run.sh, verify.py. `.dxnn` 출력은 다른 모든
     산출물이 생성된 후에만 확인하세요. **이 규칙 위반 시 세션 실패입니다.**
   - **컴파일 대기를 위한 sleep-poll 금지** — `.dxnn` 파일을 폴링하기 위해
     `sleep`을 루프에서 사용하지 마세요. 금지된 패턴:
     `for i in ...; do sleep N; ls *.dxnn; done`,
     `while ! ls *.dxnn; do sleep N; done`,
     대기 사이에 반복되는 `ls *.dxnn` / `test -f *.dxnn` 확인.
     대신: 다른 모든 산출물을 먼저 생성한 후 `.dxnn` 파일이 존재하는지 한 번만
     확인하세요. 아직 존재하지 않으면 컴파일이 완료될 것이라는 가정하에 실행
     검증으로 진행하세요.
   - **필수 산출물은 컴파일과 독립적** — `setup.sh`, `run.sh`, `verify.py`,
     factory, 앱 코드는 `.dxnn` 파일이 존재할 필요가 없습니다. 알려진 모델 이름
     (예: `yolo26n.dxnn`)을 플레이스홀더 경로로 사용하여 생성하세요. 실행 검증만
     실제 `.dxnn`이 필요합니다.
7. **파일 읽기 도구 호출 최소화** — 컨텍스트에 이미 로드된 지침 파일, 에이전트 문서,
   스킬 문서를 다시 읽지 마세요. 불필요한 `cat` / `bash` 읽기마다 5-15초가
   낭비됩니다. 시스템 프롬프트와 대화 이력에 있는 지식을 사용하세요.

## Brainstorming — 계획 전 스펙 (HARD GATE)

superpowers `brainstorming` skill 또는 `/dx-brainstorm-and-plan` 사용 시:

1. **스펙 문서는 MANDATORY입니다** — `writing-plans`로 전환하기 전에, 스펙
   문서를 반드시 `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`에 작성해야 합니다.
   스펙을 건너뛰고 바로 계획 작성으로 가는 것은 위반입니다.
2. **사용자 승인 게이트는 MANDATORY입니다** — 스펙 작성 후, 사용자가 계획 작성
   진행 전에 반드시 검토하고 승인해야 합니다. 관련 없는 사용자 응답(예: 다른 질문에 답변)을
   스펙 승인으로 간주하지 마십시오.
3. **계획 문서는 스펙을 참조해야 합니다** — 계획 헤더에 승인된 스펙 문서에 대한
   링크를 포함해야 합니다.
4. **`/dx-brainstorm-and-plan` 우선** — 일반적인 superpowers `brainstorming` skill
   대신 프로젝트 레벨 brainstorming skill을 사용하십시오. 프로젝트 레벨 skill에는
    도메인별 질문과 사전 점검이 포함되어 있습니다.
5. **규칙 충돌 확인은 필수** — 브레인스토밍 중 에이전트는 사용자 요구사항이
   HARD GATE 규칙(IFactory 패턴, skeleton-first, Output Isolation,
   SyncRunner/AsyncRunner)과 충돌하는지 반드시 확인해야 합니다. 충돌이 감지되면
   브레인스토밍 단계에서 해결해야 하며, 위반 요청을 설계 사양에 조용히 따르면
   안 됩니다. "Rule Conflict Resolution" 섹션을 참조하세요.

## 하드웨어

| 아키텍처 | 값 | 사용 사례 |
|---|---|---|
| DX-M1 | `dx_m1` | 전체 성능 NPU |

## 메모리

영구 지식은 `.deepx/memory/`에 있습니다. 작업 시작 시 읽고, 학습 시 업데이트하십시오.
통합된 `common_pitfalls.md`에는 [UNIVERSAL], [DX_APP], [DX_STREAM], [INTEGRATION]으로 태그된 항목이 포함되어 있습니다.

## Git 작업 — 사용자가 처리

작업 완료 시 git 브랜치 작업(merge, PR, push, 정리)에 대해 묻지 마세요.
사용자가 모든 git 작업을 직접 처리합니다. "main에 merge", "PR 생성",
"브랜치 삭제"와 같은 옵션을 제시하지 마세요 — 작업을 마무리하기만 하세요.

## Python 임포트

```python
from dx_app.src.python_example.common.runner.args import parse_common_args
from dx_app.src.python_example.common.runner.factory_runner import FactoryRunner
from dx_app.src.python_example.common.utils.model_utils import load_model_config
import logging
logger = logging.getLogger(__name__)
```

## 테스팅

```bash
cd dx_app && pytest tests/
cd dx_stream && pytest test/
python .deepx/scripts/validate_framework.py
```

## Git 안전 — Superpowers 산출물

**`docs/superpowers/` 아래 파일을 절대 `git add` 또는 `git commit` 하지 마십시오.** 이들은 superpowers
skill 시스템에 의해 생성된 임시 계획 산출물(스펙, 계획)입니다. `.gitignore`에 포함되어 있지만,
일부 도구는 `git add -f`로 `.gitignore`를 우회할 수 있습니다. 파일 생성은 괜찮습니다 —
커밋하는 것은 금지됩니다.

## 세션 센티널 (MANDATORY — 자동화 테스트용)

사용자 프롬프트를 처리할 때, 테스트 하니스의 자동화된 세션
경계 감지를 위해 이 정확한 마커를 출력하십시오:

- **응답의 첫 번째 줄**: `[DX-AGENTIC-DEV: START]`
- **모든 작업 완료 후 마지막 줄**: `[DX-AGENTIC-DEV: DONE (output-dir: <relative_path>)]`
  여기서 `<relative_path>`는 세션 출력 디렉토리입니다 (예: `dx-agentic-dev/20260409-143022_yolo26n_detection/`)

규칙:
1. **중요 — 첫 번째 응답의 절대적 첫 줄로 `[DX-AGENTIC-DEV: START]`를 출력하십시오.**
   이것은 다른 텍스트, 도구 호출, 또는 추론보다 먼저 나타나야 합니다.
   사용자가 "그냥 진행해" 또는 "알아서 판단해"라고 지시하더라도,
   START 센티널은 협상 불가입니다 — 자동화 테스트가 이것 없이는 실패합니다.
2. 모든 작업, 검증, 파일 생성이 완료된 후 마지막 줄로 `[DX-AGENTIC-DEV: DONE (output-dir: <path>)]`를 출력하십시오
3. 상위 에이전트에서 handoff/routing으로 호출된 **하위 에이전트**인 경우,
   이 센티널을 출력하지 마십시오 — 최상위 에이전트만 출력합니다
4. 사용자가 세션에서 여러 프롬프트를 보내면, 각 프롬프트마다 START/DONE을 출력하십시오
5. DONE의 `output-dir`은 프로젝트 루트에서 세션 출력 디렉토리까지의 상대 경로여야 합니다.
   파일이 생성되지 않은 경우, `(output-dir: ...)` 부분을 생략하십시오.
6. **계획 산출물만 작성한 후에는 절대 DONE을 출력하지 마십시오** (스펙, 계획, 설계
   문서). DONE은 모든 산출물이 생성되었음을 의미합니다 — 구현 코드, 스크립트,
   설정, 검증 결과. brainstorming 또는 계획 단계를 완료했지만 아직 실제 코드를
   구현하지 않은 경우, DONE을 출력하지 마십시오. 대신, 구현을 진행하거나
   사용자에게 진행 방법을 문의하십시오.
7. **DONE 전 필수 산출물 확인**: DONE을 출력하기 전에, 세션 디렉토리에 모든
   필수 산출물이 존재하는지 확인하십시오. 필수 파일이 누락된 경우,
   DONE을 출력하기 전에 생성하십시오. 각 서브 프로젝트는 자체 skill 문서에
   필수 파일 목록을 정의합니다 (예: `dx-build-pipeline-app.md` 파일 생성 체크리스트).
8. **세션 HTML 내보내기 안내** (Copilot CLI 전용): DONE
   센티널 줄 바로 앞에 다음을 출력하십시오: `To save this session as HTML, type: /share html`
   — 이것은 사용자에게 전체 대화를 보존할 수 있음을 알려줍니다. `/share html`
   명령은 GitHub Copilot CLI 전용입니다; Claude Code,
   Copilot Chat (VS Code), 또는 OpenCode에서는 작동하지 않습니다. 테스트 하니스(`test.sh`)는
   내보낸 HTML 파일을 세션 출력 디렉토리로 자동으로 감지하고 복사합니다.

## 계획 출력 (MANDATORY)

계획 문서를 생성할 때(예: writing-plans 또는 brainstorming skill을 통해),
파일 저장 직후 **항상 대화 출력에 전체 계획 내용을 인쇄하십시오**. 파일 경로만
언급하지 마십시오 — 사용자가 별도의 파일을 열지 않고 프롬프트에서 직접
계획을 검토할 수 있어야 합니다.

## 출력 격리 (HARD GATE)

모든 AI 생성 파일은 대상 서브 프로젝트 내의 `dx-agentic-dev/<session_id>/`에
작성되어야 합니다. 생성된 코드를 기존 소스 디렉토리(예: `src/`, `pipelines/`,
`semseg_260323/`, 또는 사용자의 기존 코드가 있는 디렉토리)에 직접 작성하지 마십시오.

**세션 ID 형식**: `YYYYMMDD-HHMMSS_<model>_<task>` — 타임스탬프는
**시스템 로컬 시간대**를 사용해야 합니다(UTC가 아님). Bash에서 `$(date +%Y%m%d-%H%M%S)` 또는
Python에서 `datetime.now().strftime('%Y%m%d-%H%M%S')`를 사용하십시오. `date -u`,
`datetime.utcnow()`, 또는 `datetime.now(timezone.utc)`를 사용하지 마십시오.

- **올바름**: `dx_app/dx-agentic-dev/20260413-093000_plantseg_inference/demo_dxnn_sync.py`
- **잘못됨**: `dx_app/semseg_260323/demo_dxnn_sync.py`

유일한 예외: 사용자가 명시적으로 "소스 디렉토리에 작성해" 또는
"기존 파일을 직접 수정해"라고 말한 경우.

## 규칙 충돌 해결 (HARD GATE)

사용자의 요청이 HARD GATE 규칙과 충돌하는 경우, 에이전트는 반드시:

1. **사용자의 의도를 인정** — 사용자가 원하는 것을 이해했음을 보여주십시오.
2. **충돌을 설명** — 특정 규칙과 그 이유를 인용하십시오.
3. **올바른 대안을 제안** — 프레임워크 내에서 사용자의 목표를 달성하는
   방법을 보여주십시오. 예를 들어, 사용자가 직접
   `InferenceEngine.run()` 사용을 요청하면, IFactory 패턴이
   동일한 API를 래핑한다고 설명하고 factory 기반 대안을 제안하십시오.
4. **올바른 접근 방식으로 진행** — 규칙 위반 요청에 묵묵히
   따르지 마십시오. "옵션 A 대 옵션 B"로 제시하지 마십시오.

**일반적인 충돌 패턴** (실제 세션에서):
- 사용자가 "`InferenceEngine.Run()` 사용해"라고 말함 → IFactory 패턴을 사용해야 함 (engine
  호출은 `run_inference()` 메서드 내부에 위치)
- 사용자가 "demo.py를 복제하고 onnxruntime을 교체해"라고 말함 → 사용자 스크립트를 복제하지 않고
  `src/python_example/`에서 skeleton-first를 사용해야 함
- 사용자가 "demo_dxnn_sync.py를 만들어"라고 말함 → 독립형 스크립트가 아닌
  SyncRunner를 사용한 `<model>_sync.py` 명명을 사용해야 함
- 사용자가 "`run_async()`를 직접 사용해"라고 말함 → 수동 async 루프가 아닌
  AsyncRunner를 사용해야 함

**이 규칙은 명시적 사용자 재정의를 무효화하지 않습니다**: 사용자가 충돌에 대해
통보받은 후 명시적으로 "규칙을 이해했으며, 직접 API 사용으로 진행해"라고
말하면 따르십시오. 그러나 에이전트는 먼저 충돌을 설명해야 합니다 —
묵묵히 따르는 것은 항상 위반입니다.

## 서브 프로젝트 개발 규칙 (MANDATORY — 자체 포함)

이 규칙들은 **권위적이고 자체 포함됩니다**. 서브 프로젝트 파일이 로드되었는지
여부와 관계없이 반드시 따라야 합니다. 대화형 모드에서(예: dx-runtime 레벨에서
작업 시), 서브 프로젝트 파일(dx_app, dx_stream)이 자동으로 로드되지 않을 수
있습니다 — 이 규칙들이 유일한 보호장치입니다.

**중요**: 이것들은 선택적 요약이 아닙니다. 아래의 모든 규칙은 HARD GATE입니다.
어떤 규칙이든 위반하면(예: skeleton-first 건너뛰기, IFactory 미사용, 소스
디렉토리에 쓰기) 진행 전에 수정해야 하는 차단 오류입니다.

### dx_app 규칙 (독립형 추론)

1. **Skeleton-first 개발** — 코드를 작성하기 전에 `dx_app/.deepx/skills/dx-build-python-app.md`
   skeleton 템플릿을 먼저 읽으십시오. `src/python_example/<task>/<model>/`에서 가장 유사한
   기존 예제를 복사하고 모델별 부분(factory, postprocessor)만 수정하십시오. 처음부터
   데모 스크립트를 작성하지 마십시오. 프레임워크를 우회하는 독립형 스크립트를
   제안하지 마십시오.
2. **IFactory 패턴은 MANDATORY입니다** — 모든 추론 앱은 IFactory 5개 메서드
   패턴을 사용해야 합니다 (create, get_input_params, run_inference, post_processing, release).
   대안적 추론 구조를 발명하지 마십시오. 독립형 스크립트에서 직접 `InferenceEngine`
   사용은 위반입니다 — factory 패턴을 통해야 합니다.
   **사용자가 API 메서드를 명시적으로 언급하더라도** (예: "`InferenceEngine.run()` 사용해",
   "`run_async()` 사용해"), 에이전트는 반드시 이 호출들을 IFactory 패턴 내부에 래핑하고
   사용자에게 규칙을 설명해야 합니다. 위의 "규칙 충돌 해결"을 참조하십시오.
3. **SyncRunner/AsyncRunner만 사용** — 프레임워크의 SyncRunner(단일 모델) 또는
   AsyncRunner(다중 모델)를 사용하십시오. 대안적 실행 접근 방식(독립형 스크립트,
   직접 API 호출, 커스텀 runner, 수동 `run_async()` 루프)을 제안하지 마십시오.
4. **대안 제안 금지** — 앱 아키텍처에 대해 "옵션 A 대 옵션 B" 선택지를
   제시하지 마십시오. 프레임워크가 변형별로 하나의 올바른 패턴을 지시합니다.
5. **기존 예제 MANDATORY** — 새 앱을 작성하기 전에, 동일한 AI 작업의 기존 예제를
   `src/python_example/`에서 검색하십시오. 참조로 사용하십시오.
6. **DXNN 입력 형식 자동 감지** — 전처리 차원이나 형식을 하드코딩하지 마십시오.
   DXNN 모델은 `dx_engine`을 통해 입력 요구사항을 자체 기술합니다.
7. **출력 격리** — 모든 생성된 코드는 `dx-agentic-dev/<session_id>/`에 위치해야 합니다.
   기존 소스 디렉토리에 절대 쓰지 마십시오.

### dx_stream 규칙 (GStreamer 파이프라인)

1. **x264enc tune=zerolatency** — x264enc 요소에 항상 `tune=zerolatency`를 설정하십시오.
2. **처리 단계 사이 Queue** — GStreamer 데드락 방지를 위해 처리 단계 사이에
   항상 `queue` 요소를 추가하십시오.
3. **기존 파이프라인 MANDATORY** — 새 파이프라인 구성을 생성하기 전에
   `pipelines/`에서 기존 예제를 검색하십시오.

### 공통 규칙 (모든 서브 프로젝트)

1. **PPU 모델 자동 감지** — 라우팅 또는 postprocessor 코드 생성 전에 모델 이름 접미사(`_ppu`), README, 또는 registry에서 PPU 플래그를 확인하십시오. PPU 모델은 단순화된 후처리를 사용합니다 — 별도의 NMS 불필요.
2. **빌드 순서** — dx_rt → dx_app → dx_stream. 순서를 어기지 마십시오.
3. **서브 프로젝트 컨텍스트 로딩** — 서브 프로젝트로 라우팅하거나 그 안에서 작업할 때,
   항상 해당 서브 프로젝트의 `.github/copilot-instructions.md`를 먼저 읽으십시오.

---

## Instruction File Verification Loop (HARD GATE) — 내부 개발 전용

에이전트 지식 베이스 파일 수정 시 — 다음 패턴에 해당하는 파일:
`**/.cursor/**/*.mdc`, `**/.github/**/*.md`, `**/.opencode/**/*.md`,
`**/AGENTS*.md`, `**/CLAUDE*.md`, 또는 `**/.deepx/**/*.md` — 작업 완료를
선언하기 전에 다음 검증-수정 루프를 **반드시** 수행해야 합니다:

1. **자동화 테스트 루프** — `tests/test_agentic_scenarios/`를 실행하고 모든 실패를 수정:
   ```bash
   python -m pytest tests/test_agentic_scenarios/ -v --tb=short
   ```
2. **수동 감사** — 테스트 결과를 사용하지 않고, 실제 파일 내용을 읽어 크로스 플랫폼
   sync (CLAUDE vs AGENTS vs copilot)와 레벨 간 sync (suite → 하위 레벨)를 독립적으로
   검증합니다.
3. **갭 분석** — 수동 감사에서 테스트가 잡지 못한 이슈를 발견하면, **먼저 테스트
   케이스를 강화**한 후 파일을 수정합니다.
4. **반복** — 1단계로 돌아갑니다. 자동화 테스트 통과 AND 수동 감사 이슈 0건이
   될 때까지 계속 반복합니다.

**수동 감사가 필요한 이유**: 테스트는 알려진 패턴만 검증할 수 있습니다. 수동 감사는
상호 참조 방향 오류, 섹션 순서 문제, 의미론적 갭 등 기존 테스트가 커버하지 못하는
새로운 이슈를 발견합니다. 테스트 강화 후에도 수동 감사가 추가 이슈를 일관되게
발견해왔습니다.

이 게이트는 instruction 파일이 작업의 *주요 산출물*인 경우(예: 규칙 추가, 플랫폼 sync,
KO 번역 생성)에 적용됩니다. 기능 구현의 일부로 instruction 파일에 단순 한 줄 수정이
발생하는 경우에는 적용되지 않습니다.
