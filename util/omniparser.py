from util.utils import get_som_labeled_img, get_caption_model_processor, get_yolo_model, check_ocr_box
import torch
from PIL import Image
import io
import base64
from typing import Dict
class Omniparser(object):
    def __init__(self, config: Dict):
        self.config = config
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

        self.som_model = get_yolo_model(model_path=config['som_model_path'])
        self.caption_model_processor = get_caption_model_processor(model_name=config['caption_model_name'], model_name_or_path=config['caption_model_path'], device=device)
        print('Omniparser initialized!!!')

    def parse(self, image_base64: str, box_threshold: float = None, iou_threshold: float = 0.7, use_paddleocr: bool = False, imgsz: int = 640):
        import time

        if box_threshold is None:
            box_threshold = self.config['BOX_TRESHOLD']

        t0 = time.time()
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes))
        t_decode = time.time() - t0
        print(f'[timing] image decode: {t_decode:.3f}s | size: {image.size}')

        box_overlay_ratio = max(image.size) / 3200
        draw_bbox_config = {
            'text_scale': 0.8 * box_overlay_ratio,
            'text_thickness': max(int(2 * box_overlay_ratio), 1),
            'text_padding': max(int(3 * box_overlay_ratio), 1),
            'thickness': max(int(3 * box_overlay_ratio), 1),
        }

        t1 = time.time()
        ocr_engine = 'PaddleOCR' if use_paddleocr else 'EasyOCR'
        print(f'[timing] using OCR engine: {ocr_engine}')
        (text, ocr_bbox), _ = check_ocr_box(image, display_img=False, output_bb_format='xyxy', goal_filtering=None, easyocr_args={'paragraph': False, 'text_threshold': 0.9}, use_paddleocr=use_paddleocr)
        t_ocr = time.time() - t1
        print(f'[timing] OCR: {t_ocr:.3f}s')

        t2 = time.time()
        dino_labled_img, label_coordinates, parsed_content_list = get_som_labeled_img(image, self.som_model, BOX_TRESHOLD=box_threshold, output_coord_in_ratio=True, ocr_bbox=ocr_bbox, draw_bbox_config=draw_bbox_config, caption_model_processor=self.caption_model_processor, ocr_text=text, use_local_semantics=True, iou_threshold=iou_threshold, scale_img=False, batch_size=128, imgsz=imgsz)
        t_detect_caption = time.time() - t2
        print(f'[timing] detection + captioning: {t_detect_caption:.3f}s')

        # Encode PIL Image to base64 string for JSON serialization
        t3 = time.time()
        buffered = io.BytesIO()
        dino_labled_img.save(buffered, format="JPEG", quality=85)
        dino_labled_img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        t_encode = time.time() - t3
        print(f'[timing] image encode: {t_encode:.3f}s')

        # Ensure parsed_content_list is JSON-serializable (bbox may contain tensor floats)
        serializable_content = []
        for item in parsed_content_list:
            serializable_content.append({
                'type': item.get('type', 'icon'),
                'bbox': [float(x) for x in item['bbox']],
                'interactivity': item.get('interactivity', False),
                'content': item.get('content'),
                'source': item.get('source', ''),
            })

        t_total = time.time() - t0
        print(f'[timing] TOTAL: {t_total:.3f}s (decode: {t_decode:.3f}s, ocr: {t_ocr:.3f}s, detect+caption: {t_detect_caption:.3f}s, encode: {t_encode:.3f}s)')

        return dino_labled_img_base64, serializable_content