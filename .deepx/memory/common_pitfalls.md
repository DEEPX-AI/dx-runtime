# Common Pitfalls

Read this file at every task start. Each entry is tagged with a domain and follows the Symptom / Root Cause / Fix structure.

**Domain tags:** `[UNIVERSAL]` (applies everywhere), `[DX_APP]` (standalone inference), `[DX_STREAM]` (GStreamer pipelines), `[PPU]` (pre/post-processing unit models), `[INTEGRATION]` (cross-project issues).

---

## [UNIVERSAL] model_registry.json Model Name Case Mismatch

- **Symptom**: `KeyError` or `ModelNotFoundError` when loading a model by name. The .dxnn file exists on disk but the registry lookup fails silently.
- **Root Cause**: Model names in `model_registry.json` are case-sensitive. Entries like `"YOLOv8s"` will not match a query for `"yolov8s"` or `"Yolov8s"`. The registry performs exact string matching with no normalization.
- **Fix**: Always use the exact case from `model_registry.json`. Run `grep -i <model_name> model_registry.json` to find the canonical name. When writing config files, copy-paste the model name rather than typing it manually.

---

## [DX_STREAM] DxPreprocess preprocess-id / DxInfer preprocess-id Mismatch

- **Symptom**: Pipeline runs but inference results are garbage — bounding boxes in wrong locations, classifications always wrong, or segmentation masks are shifted.
- **Root Cause**: `DxPreprocess` and `DxInfer` elements are linked by a `preprocess-id` property. If the IDs do not match, `DxInfer` receives unprocessed or incorrectly-processed frames. The pipeline does not raise an error because the buffer dimensions may still be valid.
- **Fix**: Ensure every `DxPreprocess` / `DxInfer` pair shares the same `preprocess-id` value. In multi-model pipelines, use distinct IDs per model stage (e.g., `preprocess-id=0` for detection, `preprocess-id=1` for classification).

```
DxPreprocess preprocess-id=0 ! ... ! DxInfer preprocess-id=0 model=detect.dxnn
DxPreprocess preprocess-id=1 ! ... ! DxInfer preprocess-id=1 model=classify.dxnn
```

---

## [DX_APP] AsyncRunner Frame Order Inversion

- **Symptom**: Displayed detections lag behind the video by 1-2 frames, or bounding boxes appear on the wrong frame. Most visible when objects move quickly.
- **Root Cause**: `AsyncRunner` uses a 3-stage pipeline (frame N-1 postprocess, frame N inference, frame N+1 preprocess). If the callback consumes results without matching them to the correct frame index, results are drawn on the wrong frame.
- **Fix**: Use the `frame_id` field returned in the `AsyncRunner` result callback. Match `result.frame_id` to the display buffer's frame index. Never assume results arrive in submission order when `num_workers > 1`.

```python
runner = AsyncRunner(engine, num_workers=2)
for frame in source:
    runner.submit(frame, frame_id=frame.index)
    results = runner.get_ready()
    for r in results:
        display_buffer[r.frame_id].draw(r.detections)
```

---

## [DX_APP] dx_postprocess Not Installed — C++ Postprocessor ImportError

- **Symptom**: `ImportError: No module named 'dx_postprocess'` or `cannot find libdx_postprocess.so` when running an app that uses the C++ postprocessor variant.
- **Root Cause**: The `dx_postprocess` package is a compiled C++ extension that ships separately from the Python SDK. It is not installed by `pip install deepx-runtime`. The Python-only fallback postprocessor works but is 5-10x slower.
- **Fix**: Install the native postprocessor package: `sudo apt install dx-postprocess` or build from source with `cmake .. && make install` in the `dx_postprocess/` directory. Verify: `python -c "import dx_postprocess"`.

---

## [DX_STREAM] RTSP Stream Buffer Overload Without DxRate

- **Symptom**: Memory usage grows steadily over minutes. Pipeline eventually crashes with `GStreamer: out of memory` or frames visibly freeze while buffers accumulate.
- **Root Cause**: RTSP sources push frames at the camera's native rate (e.g., 30 FPS) regardless of downstream processing speed. Without rate limiting, queues between elements overflow. The NPU inference stage is the usual bottleneck.
- **Fix**: Insert a `DxRate` element immediately after the RTSP source to drop excess frames before they enter the processing pipeline:

```
rtspsrc location=rtsp://... ! rtph264depay ! h264parse ! avdec_h264 ! DxRate rate=15 ! DxPreprocess ...
```

Set `rate` to the target inference FPS (not the camera FPS).

---

## [PPU] PPU Models Require Dedicated Postprocessors

- **Symptom**: Standard YOLO postprocessor returns zero detections or crashes with shape mismatch when used with PPU model variants (e.g., `YoloV5S_PPU.dxnn`).
- **Root Cause**: PPU (Pre/Post-Processing Unit) models offload NMS and output formatting to dedicated hardware. Their output tensor layout differs from standard models — they emit final detection tuples directly rather than raw feature maps.
- **Fix**: Use the PPU-specific postprocessor: `PPUPostprocessor` instead of `YoloPostprocessor`. In config, set `"postprocessor": "ppu_nms"`. The PPU output format is `[batch, max_detections, 7]` where columns are `[batch_id, x1, y1, x2, y2, score, class_id]`.

---

## [DX_APP] OBB Detection Uses score_threshold Only (No NMS)

- **Symptom**: OBB (Oriented Bounding Box) detections show excessive overlapping boxes, and adjusting `nms_threshold` has no visible effect.
- **Root Cause**: OBB models (e.g., `yolo26n-obb`) use rotated bounding boxes that are not compatible with standard axis-aligned NMS. The postprocessor filters by `score_threshold` only. The `nms_threshold` parameter is accepted but ignored.
- **Fix**: Use a stricter `score_threshold` (e.g., 0.5 instead of 0.25) to control detection density. For custom overlap filtering, implement rotated IoU in post-processing:

```python
config = {"score_threshold": 0.5}  # nms_threshold has no effect for OBB
```

---

## [DX_STREAM] DxMsgBroker Must Follow DxMsgConv

- **Symptom**: `DxMsgBroker` element fails to start or sends empty messages. Pipeline logs show `No metadata found on buffer` warnings.
- **Root Cause**: `DxMsgBroker` (MQTT/Kafka publisher) expects serialized message metadata on incoming buffers. `DxMsgConv` converts inference results into the wire format. Without `DxMsgConv`, `DxMsgBroker` receives raw video buffers with no message payload.
- **Fix**: Always place `DxMsgConv` before `DxMsgBroker` in the pipeline:

```
... ! DxInfer model=detect.dxnn ! DxMsgConv ! DxMsgBroker topic=detections conn-str=mqtt://broker:1883
```

---

## [UNIVERSAL] Headless Mode — Check DISPLAY/WAYLAND_DISPLAY Before OpenCV imshow

- **Symptom**: `cv2.error: (-2:Unspecified error) The function is not implemented` or `cannot open display` crash on headless servers, Docker containers, or SSH sessions.
- **Root Cause**: `cv2.imshow()` requires a display server (X11 or Wayland). Headless environments have neither `DISPLAY` nor `WAYLAND_DISPLAY` set.
- **Fix**: Check for display availability before enabling visualization:

```python
import os
HAS_DISPLAY = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))

if HAS_DISPLAY:
    cv2.imshow("output", frame)
else:
    # Write to file or stream via RTSP
    cv2.imwrite(f"output_{frame_id:06d}.jpg", frame)
```

Use `--no-display` flag in CLI apps built with `parse_common_args()`.

---

## [UNIVERSAL] DX-RT Version < 3.0.0 Causes Silent Inference Failures

- **Symptom**: Inference returns all-zero tensors or nonsensical values. No error messages in logs. Model loads successfully but produces no valid detections.
- **Root Cause**: DX-RT versions prior to 3.0.0 have a tensor memory alignment bug that corrupts output buffers on certain .dxnn model architectures. The bug is data-dependent and does not trigger error codes.
- **Fix**: Upgrade DX-RT to >= 3.0.0: `sudo apt update && sudo apt install dx-runtime>=3.0.0`. Verify version: `dxrt-cli --version`. If upgrading is not possible, force explicit output buffer allocation with `InferenceEngine.set_output_buffer(np.zeros(...))`.

---

## [DX_APP] config.json score_threshold Alias Confusion

- **Symptom**: Setting `score_threshold` in config.json has no effect. Detections still appear at very low confidence.
- **Root Cause**: Some older model configs and community examples use `conf_threshold` instead of `score_threshold`. The postprocessor silently ignores unrecognized keys and falls back to the default (typically 0.25).
- **Fix**: Check the model's reference config to determine the correct key name. Current standard is `score_threshold`. If inheriting from an older config, rename the field:

```json
{
    "score_threshold": 0.5,
    "nms_threshold": 0.45
}
```

Avoid using both keys simultaneously — the postprocessor uses whichever it recognizes and ignores the other.

---

## [DX_STREAM] Secondary Mode ROI Extraction Requires DxScale Before 2nd DxInfer

- **Symptom**: In a two-stage pipeline (detection -> classification), the second-stage model receives incorrectly-sized crops. Classifications are random or always predict the same class.
- **Root Cause**: After ROI extraction from the primary detection stage, the cropped regions are at variable sizes. The second `DxInfer` expects fixed-size input matching the classification model's input dimensions. Without explicit scaling, the crop is padded or truncated incorrectly.
- **Fix**: Insert `DxScale` between ROI extraction and the secondary `DxInfer` to resize crops to the expected input dimensions:

```
... ! DxInfer preprocess-id=0 model=detect.dxnn ! DxRoiExtract ! DxScale width=224 height=224 ! DxInfer preprocess-id=1 model=classify.dxnn
```

---

## [INTEGRATION] model_registry.json and model_list.json Model Name Mismatch

- **Symptom**: A model works correctly in dx_app standalone tests but fails to load in dx_stream pipeline, or vice versa. Error messages reference different model names or file paths.
- **Root Cause**: dx_app uses `config/model_registry.json` and dx_stream uses `model_list.json` at the repository root. These two registries are maintained independently. If a model is added to one but not the other, or if the model name differs (e.g., `"yolov8n"` vs `"YOLOv8n-Detection"`), cross-project workflows break.
- **Fix**: When adding a new model, always update BOTH registries simultaneously. Use the exact same model name in both files. Run the unified validator to catch mismatches:

```bash
python .deepx/scripts/validate_framework.py
```

---

## [INTEGRATION] Build Order Dependency — dx_rt Must Be Installed First

- **Symptom**: `cmake` fails with `cannot find -ldx_engine` when building dx_app, or `gst-inspect-1.0 dxinfer` returns "No such element" when running dx_stream pipelines.
- **Root Cause**: Both dx_app and dx_stream depend on the dx_rt runtime library. If dx_rt is not installed (or is at an incompatible version), downstream builds and plugin registrations fail. The error messages do not always clearly indicate the missing dependency.
- **Fix**: Always install dx_rt first:

```bash
cd dx-runtime && ./install.sh       # Install dx_rt
cd dx_app && ./install.sh && ./build.sh   # Then dx_app
cd dx_stream && ./install.sh        # Then dx_stream
```

Verify with `dxrt-cli --version` before proceeding with sub-project builds.

---

## [INTEGRATION] Different Python Import Paths Between dx_app and dx_stream

- **Symptom**: `ModuleNotFoundError` when importing a utility from the wrong sub-project. Code copied from a dx_app example fails when pasted into a dx_stream script.
- **Root Cause**: dx_app and dx_stream have distinct Python package roots. dx_app uses `dx_app.src.python_example.*` and dx_stream uses `dx_stream.dx_stream.*`. Copying code between sub-projects without updating import paths causes immediate failures.
- **Fix**: Never copy imports between sub-projects. Each sub-project is self-contained. If shared functionality is needed, it should be in the dx_rt runtime library (`dx_runtime.*`). When building cross-project scripts, import from each sub-project explicitly:

```python
# Cross-project script — imports from both
from dx_app.src.python_example.common.utils.model_utils import load_model_config
from dx_stream.dx_stream.pipeline import DxPipeline
```
