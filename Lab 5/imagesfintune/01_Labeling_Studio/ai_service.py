"""
================================================================================
AI Auto-Labeling Backend Service for Nabataean & Aramaic Epigraphy Studio
Powered by YOLOv8 (Stage 2 Inscription Model)
================================================================================
"""

import os
import sys
import io
import base64
import json
import numpy as np
import cv2
import torch
from flask import Flask, request, jsonify

# Set UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Resolve best Stage 3 / Master model
CANDIDATE_MODELS = [
    os.path.join(ROOT_DIR, "project_requirment", "01_Model", "viking_master_model_best.pt"),
    os.path.join(ROOT_DIR, "LASTMODEL", "best(1).pt"),
    os.path.join(ROOT_DIR, "best.pt"),
    os.path.join(BASE_DIR, "04_Models_and_Weights", "finetunemodel", "epigraphy_master_finetuned_best.pt"),
    os.path.join(BASE_DIR, "04_Models_and_Weights", "epigraphy_master_best", "epigraphy_master_best.pt"),
    os.path.join(BASE_DIR, "04_Models_and_Weights", "modelstagethree", "best.pt"),
]

MODEL_PATH = None
for p in CANDIDATE_MODELS:
    if os.path.exists(p):
        MODEL_PATH = p
        break

if not MODEL_PATH:
    raise FileNotFoundError("Could not find any suitable YOLO Viking model!")

print(f"Loading YOLO Epigraphy Model from: {MODEL_PATH}")
from ultralytics import YOLO
model = YOLO(MODEL_PATH)
print(f"✅ Model loaded successfully: {os.path.basename(MODEL_PATH)} with {len(model.names)} classes on device: {model.device}")

from flask import Flask, request, jsonify, send_from_directory

STUDIO_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=STUDIO_DIR)

# Manual CORS wrapper to ensure file:// and any port can access without extra pip dependencies
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@app.route("/", methods=["GET"])
def serve_index():
    return send_from_directory(STUDIO_DIR, "index.html")

@app.route("/status", methods=["GET"])
def get_status():
    return jsonify({
        "status": "online",
        "service": "Nabataean & Aramaic AI Auto-Labeler",
        "model_file": os.path.basename(MODEL_PATH),
        "model_path": MODEL_PATH,
        "classes_count": len(model.names),
        "device": str(model.device),
        "cuda_available": torch.cuda.is_available()
    })

@app.route("/<path:path>", methods=["GET"])
def serve_static(path):
    file_path = os.path.join(STUDIO_DIR, path)
    if os.path.exists(file_path):
        return send_from_directory(STUDIO_DIR, path)
    return jsonify({"status": "error", "message": "Not found"}), 404

@app.route("/classes", methods=["GET"])
def get_classes():
    return jsonify({
        "classes": model.names
    })

@app.route("/predict", methods=["POST", "OPTIONS"])
def predict():
    if request.method == "OPTIONS":
        return "", 200

    try:
        conf = float(request.args.get("conf", 0.03))
        imgsz = int(request.args.get("imgsz", 640))
        
        cv_img = None
        
        # 1. Check if uploaded as multipart file
        if "image" in request.files:
            file_bytes = np.frombuffer(request.files["image"].read(), np.uint8)
            cv_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            
        # 2. Check if sent as JSON base64
        elif request.is_json:
            data = request.get_json()
            if "conf" in data:
                conf = float(data["conf"])
            if "imgsz" in data:
                imgsz = int(data["imgsz"])
                
            raw_b64 = data.get("image", "")
            if "," in raw_b64:
                raw_b64 = raw_b64.split(",")[1]
            img_bytes = base64.b64decode(raw_b64)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            cv_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if cv_img is None:
            return jsonify({"status": "error", "message": "No valid image provided!"}), 400

        h, w = cv_img.shape[:2]

        # Run inference
        results = model.predict(source=cv_img, conf=conf, imgsz=imgsz, verbose=False)
        res = results[0]
        boxes = res.boxes

        detections = []
        for b in boxes:
            cid = int(b.cls[0].item())
            cname = model.names.get(cid, f"class_{cid}")
            cconf = float(b.conf[0].item())
            
            # xyxy format: [x1, y1, x2, y2]
            x1, y1, x2, y2 = b.xyxy[0].tolist()
            
            # Convert to x, y, width, height clamped to image
            bx = max(0, min(w - 1, int(round(x1))))
            by = max(0, min(h - 1, int(round(y1))))
            bw = max(2, min(w - bx, int(round(x2 - x1))))
            bh = max(2, min(h - by, int(round(y2 - y1))))

            detections.append({
                "class_id": cid,
                "class_name": cname,
                "confidence": round(cconf, 4),
                "confidence_percent": round(cconf * 100, 1),
                "box": {
                    "x": bx,
                    "y": by,
                    "width": bw,
                    "height": bh
                }
            })

        # Sort detections by confidence descending
        detections.sort(key=lambda d: d["confidence"], reverse=True)

        return jsonify({
            "status": "success",
            "image_size": {"width": w, "height": h},
            "detections_count": len(detections),
            "detections": detections
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = 5005
    print("\n" + "=" * 70)
    print(f"🌟 Nabataean AI Auto-Label Service running at: http://127.0.0.1:{port}")
    print(f"🎯 Ready to auto-detect ancient characters in Labeling Studio!")
    print("=" * 70 + "\n")
    app.run(host="127.0.0.1", port=port, debug=False)
