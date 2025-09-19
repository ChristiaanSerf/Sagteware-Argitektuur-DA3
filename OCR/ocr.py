from flask import Flask, request, jsonify
from PIL import Image
import io

app = Flask(__name__)

@app.post("/ocr")
def ocr():
    # PoC stub: accept an image, pretend to extract stats, return constants
    if "file" not in request.files:
        return jsonify({"error": "missing file"}), 400
    _ = Image.open(io.BytesIO(request.files["file"].read()))  # ensures it's a real image
    return jsonify({"kda": 1.05, "adr": 62.3, "rounds": 24})

@app.get("/health")
def health():
    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
