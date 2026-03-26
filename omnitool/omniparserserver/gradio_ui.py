import base64
import io
from typing import Optional

import gradio as gr
import requests
from PIL import Image

MARKDOWN = """
# OmniParser API Test UI
Upload a screenshot to test the `/parse/` endpoint with configurable parameters.
"""


def create_gradio_app(port: int) -> gr.Blocks:
    def process(
        image_input: Image.Image,
        box_threshold: float,
        iou_threshold: float,
        use_paddleocr: bool,
        imgsz: int,
    ) -> tuple[Optional[Image.Image], str]:
        # Encode image to base64
        buffer = io.BytesIO()
        image_input.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        # Call /parse/ endpoint
        response = requests.post(
            f"http://127.0.0.1:{port}/parse/",
            json={
                "base64_image": image_base64,
                "box_threshold": box_threshold,
                "iou_threshold": iou_threshold,
                "use_paddleocr": use_paddleocr,
                "imgsz": imgsz,
            },
            timeout=300,
        )
        response.raise_for_status()
        result = response.json()

        # Decode annotated image
        som_image = Image.open(io.BytesIO(base64.b64decode(result["som_image_base64"])))

        # Format parsed content list
        parsed_content = result["parsed_content_list"]
        text_output = "\n".join(
            f"icon {i}: {v}" for i, v in enumerate(parsed_content)
        )
        text_output += f"\n\nLatency: {result['latency']:.2f}s"

        return som_image, text_output

    with gr.Blocks() as demo:
        gr.Markdown(MARKDOWN)
        with gr.Row():
            with gr.Column():
                image_input_component = gr.Image(type="pil", label="Upload image")
                box_threshold_component = gr.Slider(
                    label="Box Threshold",
                    minimum=0.01,
                    maximum=1.0,
                    step=0.01,
                    value=0.05,
                )
                iou_threshold_component = gr.Slider(
                    label="IOU Threshold",
                    minimum=0.01,
                    maximum=1.0,
                    step=0.01,
                    value=0.1,
                )
                use_paddleocr_component = gr.Checkbox(
                    label="Use PaddleOCR", value=False
                )
                imgsz_component = gr.Slider(
                    label="Icon Detect Image Size",
                    minimum=640,
                    maximum=1920,
                    step=32,
                    value=640,
                )
                submit_button_component = gr.Button(
                    value="Submit", variant="primary"
                )
            with gr.Column():
                image_output_component = gr.Image(
                    type="pil", label="Image Output"
                )
                text_output_component = gr.Textbox(
                    label="Parsed screen elements",
                    placeholder="Text Output",
                )

        submit_button_component.click(
            fn=process,
            inputs=[
                image_input_component,
                box_threshold_component,
                iou_threshold_component,
                use_paddleocr_component,
                imgsz_component,
            ],
            outputs=[image_output_component, text_output_component],
        )

    return demo
