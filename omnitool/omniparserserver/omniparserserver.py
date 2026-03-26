'''
python -m omniparserserver --som_model_path ../../weights/icon_detect/model.pt --caption_model_name florence2 --caption_model_path ../../weights/icon_caption_florence --device cuda --BOX_TRESHOLD 0.05
'''

import sys
import os
import time
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import argparse
import uvicorn
import gradio as gr
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)
from util.omniparser import Omniparser

def parse_arguments():
    parser = argparse.ArgumentParser(description='Omniparser API')
    parser.add_argument('--som_model_path', type=str, default='../../weights/icon_detect/model.pt', help='Path to the som model')
    parser.add_argument('--caption_model_name', type=str, default='florence2', help='Name of the caption model')
    parser.add_argument('--caption_model_path', type=str, default='../../weights/icon_caption_florence', help='Path to the caption model')
    parser.add_argument('--device', type=str, default='cpu', help='Device to run the model')
    parser.add_argument('--BOX_TRESHOLD', type=float, default=0.05, help='Threshold for box detection')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host for the API')
    parser.add_argument('--port', type=int, default=8000, help='Port for the API')
    args = parser.parse_args()
    return args

args = parse_arguments()
config = vars(args)

app = FastAPI()
omniparser = Omniparser(config)

from omnitool.omniparserserver.gradio_ui import create_gradio_app
gradio_app = create_gradio_app(args.port)
app = gr.mount_gradio_app(app, gradio_app, path="/gradio", root_path="/gradio")

class ParseRequest(BaseModel):
    base64_image: str
    box_threshold: Optional[float] = None
    iou_threshold: Optional[float] = 0.7
    use_paddleocr: Optional[bool] = False
    imgsz: Optional[int] = 640

@app.post("/parse/")
async def parse(parse_request: ParseRequest):
    print('start parsing...')
    start = time.time()
    dino_labled_img, parsed_content_list = omniparser.parse(
        parse_request.base64_image,
        box_threshold=parse_request.box_threshold,
        iou_threshold=parse_request.iou_threshold,
        use_paddleocr=parse_request.use_paddleocr,
        imgsz=parse_request.imgsz,
    )
    latency = time.time() - start
    print('time:', latency)
    return {"som_image_base64": dino_labled_img, "parsed_content_list": parsed_content_list, 'latency': latency}

@app.get("/probe/")
async def root():
    return {"message": "Omniparser API ready"}

if __name__ == "__main__":
    uvicorn.run("omnitool.omniparserserver.omniparserserver:app", host=args.host, port=args.port, reload=True)