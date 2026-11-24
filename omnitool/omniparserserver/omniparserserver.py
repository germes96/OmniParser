'''
python -m omniparserserver --som_model_path ../../weights/icon_detect/model.pt --caption_model_name florence2 --caption_model_path ../../weights/icon_caption_florence --device cuda --BOX_TRESHOLD 0.05

Endpoints
- POST /parse/        one screenshot per request (unchanged contract; new optional
                      field return_image=false skips the labelled image).
- WS   /ws/parse      persistent connection: send one JSON message per screenshot
                      ({"id": ..., <same fields as /parse/>}), receive one JSON
                      message back with the same "id". Requests on one connection
                      are answered in order. The server pings every 20 s.
- GET  /probe/        health check.

Every parse answer carries "latency" (GPU work), "queue_s" (time waiting for the
GPU behind other requests) and "timings" (per phase), so a client can tell server
work from network.

Auth: if OMNIPARSER_API_TOKEN is set, /parse/ and /ws/parse require
"Authorization: Bearer <token>". Unset = open (previous behaviour).
'''

import sys
import os
import threading
import time
from typing import Optional
from fastapi import FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ValidationError
from starlette.concurrency import run_in_threadpool
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

# One GPU, one parse at a time. The parse is blocking CPU/GPU work, so it runs in
# a worker thread (never on the event loop) and waits here for its turn.
_GPU_LOCK = threading.Lock()
_API_TOKEN = os.environ.get('OMNIPARSER_API_TOKEN', '')


class ParseRequest(BaseModel):
    base64_image: str
    box_threshold: Optional[float] = None
    iou_threshold: Optional[float] = 0.7
    use_paddleocr: Optional[bool] = False
    imgsz: Optional[int] = 640
    # False: skip drawing and encoding the labelled image. The element list (its
    # order is the label ids) is identical, so the client can draw the labels.
    return_image: Optional[bool] = True


def _authorized(authorization: Optional[str]) -> bool:
    return not _API_TOKEN or authorization == f'Bearer {_API_TOKEN}'


def _run_parse(req: ParseRequest) -> dict:
    arrived = time.time()
    with _GPU_LOCK:
        start = time.time()
        labelled, content, timings = omniparser.parse_with_timings(
            req.base64_image,
            box_threshold=req.box_threshold,
            iou_threshold=req.iou_threshold,
            use_paddleocr=req.use_paddleocr,
            imgsz=req.imgsz,
            return_image=req.return_image,
        )
        latency = time.time() - start
    print(f'time: {latency:.3f}s queue: {start - arrived:.3f}s image: {req.return_image}')
    return {
        'som_image_base64': labelled or '',
        'parsed_content_list': content,
        'latency': latency,
        'queue_s': start - arrived,
        'timings': timings,
    }


@app.post("/parse/")
def parse(parse_request: ParseRequest, authorization: Optional[str] = Header(default=None)):
    # Plain def: FastAPI runs it in its threadpool, so /probe/ and other
    # connections keep being served while a parse runs.
    if not _authorized(authorization):
        raise HTTPException(status_code=401, detail='invalid or missing bearer token')
    return _run_parse(parse_request)


@app.websocket("/ws/parse")
async def ws_parse(ws: WebSocket):
    if not _authorized(ws.headers.get('authorization')):
        await ws.close(code=1008)
        return
    await ws.accept()
    try:
        while True:
            message = await ws.receive_json()
            request_id = message.pop('id', None)
            try:
                answer = await run_in_threadpool(_run_parse, ParseRequest(**message))
            except ValidationError as exc:
                answer = {'error': 'invalid request', 'detail': exc.errors()}
            except Exception as exc:  # report it on this request; keep the connection
                answer = {'error': f'{type(exc).__name__}: {exc}'}
            answer['id'] = request_id
            await ws.send_json(answer)
    except WebSocketDisconnect:
        return


@app.get("/probe/")
async def root():
    return {"message": "Omniparser API ready"}

if __name__ == "__main__":
    # Pass the app object, no reload: reload=True re-imported this module in a
    # child process and loaded the models a second time on the GPU.
    uvicorn.run(app, host=args.host, port=args.port, ws_ping_interval=20, ws_ping_timeout=20)
