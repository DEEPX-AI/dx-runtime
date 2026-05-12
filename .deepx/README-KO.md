# `.deepx/` — DEEPX Runtime 통합 지식 베이스

DEEPX dx-runtime 지식 시스템의 **통합 계층(integration layer)** 입니다.
이 계층은 하위 프로젝트 지식 베이스의 내용을 중복하지 않습니다. 대신
dx_app과 dx_stream 양쪽에 걸친 작업을 위한 cross-project routing,
통합된 agent, 그리고 통합 전용 지침을 제공합니다.

---

## 아키텍처

| 레벨 | 경로 | 범위 | 사용 시점 |
|---|---|---|---|
| **dx_app** | `dx_app/.deepx/` | 독립형 inference 앱 (Python/C++) | dx_app submodule 단독으로 개발할 때 |
| **dx_stream** | `dx_stream/.deepx/` | GStreamer pipeline 앱 | dx_stream submodule 단독으로 개발할 때 |
| **dx-runtime** (현재) | `.deepx/` | Cross-project 통합 | dx_app + dx_stream 양쪽에 걸쳐 작업할 때 |

각 하위 프로젝트의 `.deepx/`는 완전히 자기완결적이며, submodule이 단독으로
clone되어도 독립적으로 동작합니다. 이 통합 계층은 다음을 추가합니다:

- **통합 라우팅(Unified routing)** — 모든 작업 타입을 포괄하는 단일 context routing 표
- **Cross-project agent** — 올바른 하위 프로젝트 builder로 dispatch하는 router
- **통합 지침(Integration instructions)** — build 순서, 공유 model 경로, cross-validation
- **통합 메모리(Unified memory)** — 두 프로젝트에 걸쳐 도메인별로 태그된 공통 함정(pitfalls)
- **통합 스크립트(Unified scripts)** — 세 개의 `.deepx/` 디렉터리 전체에서 동작하는 validator와 generator

---

## 디렉터리 구조

```
.deepx/
├── README.md                          # 본 파일 — 통합 계층 인덱스
├── agents/
│   ├── dx-runtime-builder.md          # 통합 router agent
│   └── dx-validator.md                # 통합 validation orchestrator
├── instructions/
│   ├── integration.md                 # Cross-project 통합 패턴
│   └── agent-protocols.md             # 행동 프로토콜 (통합 범위)
├── knowledge/
│   └── feedback_rules.yaml            # Validation 발견 사항 → 지식 베이스 매핑 규칙
├── memory/
│   └── common_pitfalls.md             # 도메인 태그가 부여된 통합 함정 모음
├── scripts/
│   ├── validate_app.py                # 통합 앱 validator (dx_app + dx_stream)
│   ├── validate_framework.py          # 3개의 .deepx/ 디렉터리 모두 검증
│   ├── feedback_collector.py          # Validation 발견 사항을 feedback 제안으로 수집
│   └── apply_feedback.py              # 승인된 feedback 수정 사항을 .deepx/ 파일에 적용
├── skills/
│   ├── dx-agentic-runtime-validate.md         # 전체 validate → collect → approve → apply → verify 루프
│   ├── dx-brainstorm-and-plan.md      # 프로세스 skill — 코드 생성 전 브레인스토밍 및 계획 수립
│   ├── dx-tdd.md                      # 프로세스 skill — test-driven development, 점진적 검증
│   └── dx-verify-completion.md        # 프로세스 skill — 완료 주장 전 검증
└── templates/
    ├── en/                            # 영문 지침 템플릿 (.tmpl) — dx-agentic-gen이 처리
    └── ko/                            # 한국어 지침 템플릿 (.tmpl) — dx-agentic-gen이 처리
```

> 플랫폼 파일 생성은 suite 레벨의 **`dx-agentic-gen`** CLI가 담당합니다
> (정식 source는 suite root의 `.deepx/tools/`에 있음). 사용법은
> [`.deepx/tools/README.md`](../../.deepx/tools/README.md)를 참고하세요.

---

## 통합 Context Routing 표

Agent는 어떤 하위 프로젝트 지식 베이스를 로드할지 결정하기 위해 이 표를 사용합니다.
모든 경로는 dx-runtime 저장소 root 기준 상대 경로입니다.

| 작업이 다음을 언급한다면... | 하위 프로젝트 | 읽어야 할 파일 |
|---|---|---|
| **Python 앱, detection, factory** | dx_app | `dx_app/.deepx/skills/dx-agentic-app-build-python.md`, `dx_app/.deepx/toolsets/common-framework-api.md` |
| **C++ 앱, native engine** | dx_app | `dx_app/.deepx/skills/dx-agentic-app-build-cpp.md`, `dx_app/.deepx/toolsets/dx-engine-api.md` |
| **Async, high-throughput** | dx_app | `dx_app/.deepx/skills/dx-agentic-app-build-async.md`, `dx_app/.deepx/memory/performance_patterns.md` |
| **Model, download, registry** | dx_app | `dx_app/.deepx/skills/dx-agentic-app-model-management.md`, `dx_app/.deepx/toolsets/model-registry.md` |
| **GStreamer, pipeline, stream** | dx_stream | `dx_stream/.deepx/skills/dx-agentic-stream-build-pipeline.md`, `dx_stream/.deepx/toolsets/dx-stream-elements.md` |
| **MQTT, Kafka, message broker** | dx_stream | `dx_stream/.deepx/skills/dx-agentic-stream-build-mqtt-kafka.md`, `dx_stream/.deepx/toolsets/dx-stream-elements.md` |
| **Cross-project, integration** | dx-runtime | `.deepx/instructions/integration.md`, `.deepx/memory/common_pitfalls.md` |
| **Validation, testing** | 양쪽 | `.deepx/scripts/validate_app.py`, 하위 프로젝트의 `instructions/testing-patterns.md` |
| **Validation, feedback, fix** | dx-runtime | `.deepx/skills/dx-agentic-runtime-validate.md`, `.deepx/knowledge/feedback_rules.yaml` |
| **항상 읽을 것 (모든 작업)** | dx-runtime | `.deepx/memory/common_pitfalls.md` |

---

## 하위 프로젝트 진입점

| 하위 프로젝트 | CLAUDE.md | .deepx/ |
|---|---|---|
| dx_app | `dx_app/CLAUDE.md` | `dx_app/.deepx/README.md` |
| dx_stream | `dx_stream/CLAUDE.md` | `dx_stream/.deepx/README.md` |

---

## 개발자 워크플로우

```
1. Edit     →  .deepx/ 내 파일 수정 (현재 레벨 또는 하위 프로젝트)
2. Validate →  python .deepx/scripts/validate_framework.py
3. Generate →  dx-agentic-gen generate   (또는: suite root에서 bash .deepx/tools/scripts/run_all.sh generate)
4. Commit   →  git add .deepx/ && git commit
```

모든 변경 사항은 `.deepx/`에서 바깥으로 흐릅니다. 생성된 플랫폼 파일을
직접 수정하지 마세요 — 다음 재생성 시 덮어쓰여집니다.
