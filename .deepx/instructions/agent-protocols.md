# DEEPX Agent Behavioral Protocols — Integration Layer

> Slim integration-scoped protocol reference. For the full 11-protocol behavioral
> specification, see the sub-project versions:
> - `dx_app/.deepx/instructions/agent-protocols.md`
> - `dx_stream/.deepx/instructions/agent-protocols.md`

---

## Integration-Specific Protocols

These protocols apply ONLY when working across dx_app and dx_stream boundaries.
Sub-project-specific protocols (Context-First Execution, Factory Pattern, Phase Gates,
Convention Verification, etc.) are defined in each sub-project's `.deepx/instructions/`.

---

### Protocol: Cross-Project Consistency

**Rule:** When modifying shared models, APIs, or configuration schemas, verify the
impact on BOTH dx_app and dx_stream before marking the task complete.

**Trigger conditions:**

| Change in... | Must also verify... |
|---|---|
| `model_registry.json` (dx_app) | `model_list.json` (dx_stream) has matching entry |
| `.dxnn` model file rename | Both registries reference the new filename |
| Postprocessor output format | dx_stream `DxPostprocess` handles the new format |
| InferenceEngine API change | dx_stream `DxInfer` wrapper is updated |
| `parse_common_args()` flags | dx_stream CLI scripts accept the same flags |

**Enforcement:**

```
BEFORE marking a cross-project task complete:
  1. List all files modified in dx_app
  2. List all files modified in dx_stream
  3. For each shared artifact (model name, API signature, config key):
     Verify both projects are consistent
  4. Run: python .deepx/scripts/validate_framework.py
```

---

### Protocol: Sub-Agent Routing

**Rule:** Use the DX Runtime Builder agent (`agents/dx-runtime-builder.md`) as the
entry point. It classifies and routes to the correct sub-project agent.

**Routing decision tree:**

```
User request
  ├── Mentions GStreamer, pipeline, stream, RTSP, DxInfer?
  │     → Route to dx_stream agent
  ├── Mentions Python app, C++ app, IFactory, SyncRunner, AsyncRunner?
  │     → Route to dx_app agent
  ├── Mentions BOTH pipeline AND standalone inference?
  │     → Handle as cross-project: dispatch sub-agents to both
  └── Mentions build, install, validate, model download (generic)?
        → Check scope and route accordingly
```

---

### Protocol: Memory Feedback (Integration Scope)

**Rule:** When a new integration pitfall is discovered, add it to
`.deepx/memory/common_pitfalls.md` with the `[INTEGRATION]` domain tag.

Integration pitfalls typically involve:
- Model name mismatches between dx_app and dx_stream registries
- Build order failures
- Import path confusion between sub-projects
- GStreamer plugin resolution failures after dx_rt reinstall
