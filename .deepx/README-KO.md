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
│   ├── dx-agent-runtime-validate/
│   │   └── SKILL.md                   # 전체 validate → collect → approve → apply → verify 루프
│   ├── dx-agent-brainstorm/
│   │   └── SKILL.md                   # 프로세스 skill — 코드 생성 전 브레인스토밍 및 계획 수립
│   ├── dx-agent-tdd/
│   │   └── SKILL.md                   # 프로세스 skill — test-driven development, 점진적 검증
│   └── dx-agent-verify/
│       └── SKILL.md                   # 프로세스 skill — 완료 주장 전 검증
└── templates/
    ├── en/                            # 영문 지침 템플릿 (.tmpl) — dx-agent-gen이 처리
    └── ko/                            # 한국어 지침 템플릿 (.tmpl) — dx-agent-gen이 처리
```

> 플랫폼 파일 생성은 suite 레벨의 **`dx-agent-gen`** CLI가 담당합니다
> (정식 source는 suite root에 있습니다).

## 지원 도구

이 integration-layer 지식 베이스는 다음 5개 AI 코딩 도구가 사용합니다:

- **Claude Code** — `CLAUDE.md` + 필요 시 `.deepx/` 직접 참조
- **GitHub Copilot** — `.github/copilot-instructions.md`, `.github/agents/`, `.github/skills/`
- **Cursor** — `.cursor/rules/*.mdc`
- **OpenCode** — `AGENTS.md`, `opencode.json`, `.opencode/agents/`
- **Codex CLI** — `AGENTS.md`, `.codex/skills/dx-codex-identity/SKILL.md`, 그리고 `.deepx/skills/*/SKILL.md` 직접 참조

Codex CLI는 이 레이어에서 Copilot이나 OpenCode와 같은 `@mention` 또는
slash-command wrapper를 사용하지 않습니다. 대신 `AGENTS.md`를 진입점으로 삼고,
더 깊은 grounding이 필요할 때 canonical `.deepx/` 파일을 직접 읽습니다.

---

## 스크립트 — 누가, 언제 사용하는가

`.deepx/scripts/` 하위의 4개 스크립트는 **하네스 / 지식 베이스 유지보수
도구**입니다. `dx-agent-dev` 자체를 개발·개선하는 엔지니어(KB maintainer)가
실행합니다. **agent-driven CLI가 만든 엔드유저용 앱이 런타임에서 실패해도 이
스크립트들이 자동으로 호출되지 않습니다.**

| Script | 누가 실행 | 언제 | 검증 대상 |
|---|---|---|---|
| `validate_framework.py` | KB maintainer / pre-commit hook | `.deepx/` 파일 수정 후 | `.deepx/` 자체의 내적 일관성 (link drift, 누락된 참조, cross-level 정합성) |
| `validate_app.py` | KB maintainer / E2E test harness | 생성된 앱 산출물 검사 시 | 생성된 앱이 KB가 명시한 패턴을 따르는가 (IFactory 5메서드, `app.yaml` 필드, GStreamer 패턴 등) |
| `feedback_collector.py` | KB maintainer (수동) | `DX Suite Validator` agent 5-step 워크플로의 Step 3 | 위 validator들의 비균질 출력을 통합 → KB 수정 **제안(proposals)** 생성 (`feedback_report.json`) |
| `apply_feedback.py` | KB maintainer (수동, 승인 후) | 위 워크플로의 Step 4 | 엔지니어가 승인한 제안(`--approve FB-001,…`)을 실제 `.deepx/` 파일에 반영 |

### 두 가지 시나리오 — 무엇이 이 루프에 포함되고 무엇이 아닌가

**❌ Scenario A — 엔드유저가 생성된 앱을 실행하다 실패 (이 루프 아님)**

1. 엔드유저가 agent-driven CLI로 생성된 앱을 실행 → 실패 (예: `setup.sh`가
   venv 생성을 누락해 `ImportError`).
2. 실패 로그는 `dx-agent-dev/<session>/` 세션 출력에 남음.
3. **이 스크립트들은 자동으로 호출되지 않음.**
4. KB maintainer가 별도로:
   - E2E autopilot 분석기(`.deepx/e2e/agent_analyzer/`)로 실패 패턴
     집계, 또는
   - 사용자 issue report를 수동으로 검토,
   - 어떤 `.deepx/` 규칙이 부족·약한지 판단한 뒤 Scenario B로 진입.

**✅ Scenario B — KB maintainer가 프레임워크를 점검·개선 (이 루프)**

1. 엔지니어가 `.deepx/skills/…` 또는 `instructions/…` 수정 후 **DX Suite
   Validator** agent 호출.
2. **Step 1** — `validate_framework.py`를 3개 레벨 모두 실행 → 내적
   일관성 점검.
3. **Step 2** — `validate_app.py`로 샘플/예제 앱 검사 → KB ↔ 생성된 앱
   정합성 점검.
4. **Step 3** — `feedback_collector.py --all` → 제안 묶음
   (`feedback_report.json`, FB-001·FB-002·…) 생성.
5. **Step 4** — 엔지니어가 제안 검토 후
   `apply_feedback.py --report … --approve FB-001,…`로 승인 항목만 반영.
6. **Step 5** — validator 재실행으로 fix 확인.
7. 끝에 `dx-agent-gen generate`로 KB 변경 사항을 플랫폼 파일(CLAUDE.md,
   AGENTS.md, copilot-instructions.md 등)에 propagate.

### 경계 (Boundary)

- ✅ **KB / framework 정합성 점검** — 이 스크립트들이 책임.
- ✅ **생성된 앱이 KB 명세를 따르는지** — `validate_app.py`가 책임.
- ❌ **엔드유저 앱의 런타임 실패 자동 대응** — 이 루프에 포함되지 않음.
  엔드유저 런타임 실패는 E2E autopilot 분석기(`.deepx/e2e/agent_analyzer/`)
  를 통해 간접적으로만 유입되며, maintainer가 어떤 발견이 KB 변경으로
  이어질 가치가 있는지 수동으로 판단.

---

## 통합 Context Routing 표

Agent는 어떤 하위 프로젝트 지식 베이스를 로드할지 결정하기 위해 이 표를 사용합니다.
모든 경로는 dx-runtime 저장소 root 기준 상대 경로입니다.

| 작업이 다음을 언급한다면... | 하위 프로젝트 | 읽어야 할 파일 |
|---|---|---|
| **Python 앱, detection, factory** | dx_app | `dx_app/.deepx/skills/dx-agent-app-build-python/SKILL.md`, `dx_app/.deepx/toolsets/common-framework-api.md` |
| **C++ 앱, native engine** | dx_app | `dx_app/.deepx/skills/dx-agent-app-build-cpp/SKILL.md`, `dx_app/.deepx/toolsets/dx-engine-api.md` |
| **Async, high-throughput** | dx_app | `dx_app/.deepx/skills/dx-agent-app-build-async/SKILL.md`, `dx_app/.deepx/memory/performance_patterns.md` |
| **Model, download, registry** | dx_app | `dx_app/.deepx/skills/dx-agent-app-model-management/SKILL.md`, `dx_app/.deepx/toolsets/model-registry.md` |
| **GStreamer, pipeline, stream** | dx_stream | `dx_stream/.deepx/skills/dx-agent-stream-build-pipeline/SKILL.md`, `dx_stream/.deepx/toolsets/dx-stream-elements.md` |
| **MQTT, Kafka, message broker** | dx_stream | `dx_stream/.deepx/skills/dx-agent-stream-build-mqtt-kafka/SKILL.md`, `dx_stream/.deepx/toolsets/dx-stream-elements.md` |
| **Cross-project, integration** | dx-runtime | `.deepx/instructions/integration.md`, `.deepx/memory/common_pitfalls.md` |
| **Validation, testing** | 양쪽 | `.deepx/scripts/validate_app.py`, 하위 프로젝트의 `instructions/testing-patterns.md` |
| **Validation, feedback, fix** | dx-runtime | `.deepx/skills/dx-agent-runtime-validate/SKILL.md`, `.deepx/knowledge/feedback_rules.yaml` |
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
3. Generate →  dx-agent-gen generate   (또는: suite root에서 bash .deepx/tools/scripts/run_all.sh generate)
4. Commit   →  git add .deepx/ && git commit
```

모든 변경 사항은 `.deepx/`에서 바깥으로 흐릅니다. 생성된 플랫폼 파일을
직접 수정하지 마세요 — 다음 재생성 시 덮어쓰여집니다.
