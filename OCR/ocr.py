from flask import Flask, request, jsonify
import base64
from io import BytesIO
from PIL import Image
from paddleocr import PaddleOCR
import cv2
import numpy as np

app = Flask(__name__)

# Initialize PaddleOCR with English language
ocr = PaddleOCR(use_angle_cls=True, lang='en')

@app.route("/extract_table", methods=["POST"])
def extract_table():
    try:
        # 1. Parse JSON and get base64 string
        data = request.get_json()
        if not data or "image_base64" not in data:
            return jsonify({"error": "Missing 'image_base64' field"}), 400

        # 2. Decode base64 to image and run OCR inference, return raw PaddleOCR results as JSON
        img_data = base64.b64decode(data["image_base64"])
        img = Image.open(BytesIO(img_data)).convert("RGB")
        # Run OCR inference using PaddleOCR
        # Run OCR inference using the predict method
        result = ocr.predict(input=np.array(img))
        # Convert any numpy arrays in the result to lists for JSON serialization
        def serialize_item(item):
            if isinstance(item, np.ndarray):
                return item.tolist()
            elif isinstance(item, (list, tuple)):
                return [serialize_item(i) for i in item]
            elif isinstance(item, dict):
                return {k: serialize_item(v) for k, v in item.items()}
            else:
                # Handle non-serializable objects like Font by converting to string
                try:
                    return str(item)
                except Exception:
                    return None

        serializable_result = serialize_item(result)
        return jsonify({"result": serializable_result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0")
