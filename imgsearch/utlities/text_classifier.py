import os
import numpy as np
import onnxruntime as ort
from PIL import Image
import requests

UTILITIES_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(UTILITIES_DIR, "models")

MODEL_URL = "https://github.com/onnx/models/raw/main/validated/vision/classification/resnet/model/resnet50-v2-7.onnx"
MODEL_PATH = os.path.join(MODELS_DIR, "resnet50.onnx")

if not os.path.exists(MODEL_PATH):
    os.makedirs(MODELS_DIR, exist_ok=True)
    print("Downloading model...")
    r = requests.get(MODEL_URL)
    with open(MODEL_PATH, "wb") as f:
        f.write(r.content)

session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

LABELS_PATH = os.path.join(UTILITIES_DIR, "imagenet_classes.txt")
with open(LABELS_PATH) as f:
    labels = f.read().splitlines()


def preprocess(img: Image.Image) -> np.ndarray:
    img = img.convert("RGB").resize((224, 224))
    arr = np.array(img).astype(np.float32) / 255.0
    arr = (arr - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    return np.expand_dims(arr.transpose(2, 0, 1), 0).astype(np.float32)


def predict(img: Image.Image, top=5):
    preds = session.run([output_name], {input_name: preprocess(img)})[0][0]
    exp = np.exp(preds - preds.max())
    probs = exp / exp.sum()
    indices = probs.argsort()[-top:][::-1]
    return [(labels[i], round(float(probs[i]) * 100, 2)) for i in indices]
