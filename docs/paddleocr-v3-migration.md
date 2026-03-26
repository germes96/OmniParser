# PaddleOCR v3 Migration Guide

## Current State (v2.7.3)

```python
from paddleocr import PaddleOCR

paddle_ocr = PaddleOCR(
    lang='en',
    use_angle_cls=False,
    use_gpu=True,
    show_log=False,
)

result = paddle_ocr.ocr(image_np, cls=False)[0]
# result: [[box_coords, (text, confidence)], ...]
# box_coords: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]

coord = [item[0] for item in result if item[1][1] > text_threshold]
text = [item[1][0] for item in result if item[1][1] > text_threshold]
```

## v3 API Changes

### Initialization

```python
# v2.7.x
paddle_ocr = PaddleOCR(lang='en', use_angle_cls=False, use_gpu=True, show_log=False)

# v3.x
paddle_ocr = PaddleOCR(
    lang='en',
    use_textline_orientation=False,  # replaces use_angle_cls
    device='gpu:0',                  # replaces use_gpu=True ('cpu' for CPU, None for auto-detect)
)
```

| v2.7.x param | v3.x param | Notes |
|---|---|---|
| `use_gpu=True` | `device='gpu:0'` | `None` auto-detects |
| `use_angle_cls=False` | `use_textline_orientation=False` | Deprecated alias still accepted |
| `show_log=False` | *(removed)* | No direct equivalent |
| `cls=False` (in `.ocr()`) | *(removed)* | `predict()` has no `cls` param |

### Calling Convention

```python
# v2.7.x
result = paddle_ocr.ocr(image_np, cls=False)[0]

# v3.x
results = paddle_ocr.predict(image_np)
# ocr() exists as deprecated wrapper but does NOT accept cls= kwarg
```

### Result Format

```python
# v2.7.x — list of [box, (text, confidence)]
result[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]], ("hello", 0.95)

# v3.x — dict-based
results = paddle_ocr.predict(image_np)
res = results[0]['res']
res['rec_polys']   # numpy array shape (n, 4, 2) — polygon coordinates
res['rec_texts']   # list of strings
res['rec_scores']  # list of floats
res['rec_boxes']   # numpy array [x_min, y_min, x_max, y_max]
```

## Migration Steps

### 1. Update dependencies

```txt
# requirements.txt
paddlepaddle>=3.0.0      # was paddlepaddle==3.3.0 (but now needs v3 framework)
paddleocr>=3.0.0,<4.0    # was paddleocr==2.7.3
```

**Warning:** PaddleOCR v3 pulls in PaddleX which hard-pins `opencv-contrib-python==4.10.0.84`. This conflicts with `opencv-python-headless`. You may need to:
- Install paddleocr first, then force-reinstall opencv-python-headless
- Or patch PaddleX's dependency to accept headless

### 2. Update `util/utils.py` — initialization (line 23-28)

```python
# Before
paddle_ocr = PaddleOCR(
    lang='en',
    use_angle_cls=False,
    use_gpu=True,
    show_log=False,
)

# After
paddle_ocr = PaddleOCR(
    lang='en',
    use_textline_orientation=False,
    device=None,  # auto-detect GPU
)
```

### 3. Update `util/utils.py` — `check_ocr_box()` PaddleOCR branch (line 516-523)

```python
# Before
if use_paddleocr:
    if easyocr_args is None:
        text_threshold = 0.5
    else:
        text_threshold = easyocr_args['text_threshold']
    result = paddle_ocr.ocr(image_np, cls=False)[0]
    coord = [item[0] for item in result if item[1][1] > text_threshold]
    text = [item[1][0] for item in result if item[1][1] > text_threshold]

# After
if use_paddleocr:
    if easyocr_args is None:
        text_threshold = 0.5
    else:
        text_threshold = easyocr_args['text_threshold']
    results = paddle_ocr.predict(image_np)
    res = results[0]['res']
    polys = res['rec_polys']
    texts = res['rec_texts']
    scores = res['rec_scores']
    coord = [polys[i].tolist() for i in range(len(texts)) if scores[i] > text_threshold]
    text = [texts[i] for i in range(len(texts)) if scores[i] > text_threshold]
```

### 4. Verify bounding box format compatibility

The rest of the pipeline expects 4-corner polygon format `[[x1,y1], [x2,y2], [x3,y3], [x4,y4]]` from PaddleOCR. In v3, `rec_polys` is a numpy array of shape `(n, 4, 2)` — calling `.tolist()` on each entry produces the same format. Verify this with:

```python
# Should produce same structure as v2.7.x
for i, poly in enumerate(polys):
    print(poly.tolist())  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
```

### 5. Optional: Enable performance features

```python
# TensorRT acceleration (requires tensorrt installed)
paddle_ocr = PaddleOCR(
    lang='en',
    use_textline_orientation=False,
    device='gpu:0',
    use_tensorrt=True,
    precision='fp16',
)

# High-performance inference mode
paddle_ocr = PaddleOCR(
    lang='en',
    use_textline_orientation=False,
    device='gpu:0',
    enable_hpi=True,
)
```

## Known Blockers

| Issue | Severity | Workaround |
|---|---|---|
| `opencv-contrib-python==4.10.0.84` hard-pinned by PaddleX | High | Force-reinstall `opencv-python-headless` after installing paddleocr |
| Massive dependency footprint (PaddleX, aistudio-sdk, modelscope) | Medium | None — required by v3 architecture |
| `paddlepaddle >= 3.0.0` required | Medium | Separate from paddlepaddle-gpu CUDA compatibility |
| CUDA support: 11.8 and 12.6 only | Medium | CUDA 12.4 not officially supported |

## Alternative: RapidOCR (Recommended)

If the goal is GPU-accelerated OCR without PaddlePaddle dependency issues, consider `rapidocr-onnxruntime` + `onnxruntime-gpu` instead. Same PP-OCR model architecture, CUDA 12.x compatible, minimal dependencies. See CLAUDE.md TODO section.
