# Hard Hat & PPE Detection: Edge Optimization and Benchmarking

This project implements a lightweight object detection model (YOLOv8n) trained on a custom dataset for **Hard Hat and PPE Detection**, and optimizes it for edge devices using **ONNX format conversion and FP16 half-precision quantization**.

## 🛠️ Requirements & Installation

Install the required Python packages:
```bash
pip install ultralytics onnx onnxruntime opencv-python numpy huggingface_hub
```

## 🚀 Pipeline Steps

### 1. Data Sourcing & Preprocessing
The raw dataset contains 13,000+ images in COCO format. To train efficiently on CPU, we extract a subset of **500 training images, 100 validation images, and 50 test images**, and convert their COCO bounding boxes to YOLO normalized coordinates:
```bash
python convert_coco_to_yolo.py
```

### 2. Training the PyTorch Baseline
Train the pretrained YOLOv8n model on the custom subset for 3 epochs:
```bash
python train_model.py
```
*This saves the baseline weights to `runs/detect/train-2/weights/best.pt`.*

### 3. Edge Export & Quantization
Export the PyTorch model to optimized **FP32 ONNX** and **FP16 half-precision ONNX** formats:
```bash
python convert_model.py
```
*This saves the optimized weights to `runs/detect/train-2/weights/best_fp32.onnx` and `runs/detect/train-2/weights/best_fp16.onnx`.*

### 4. Edge Inference Benchmarking
Run the customized inference benchmarking script on the test images split. The script overlays bounding boxes, labels, confidence, real-time FPS, and processing latencies (pre-process, model inference, post-process/NMS):
```bash
python live_inference.py --model runs/detect/train-2/weights/best_fp16.onnx --source dataset/processed/images/test
```

## 📊 Performance Benchmark Summary

For a detailed performance breakdown, including model size reductions, speed (FPS) increases, and accuracy, see the [Edge Benchmarking Report](file:///C:/Users/Mayank/.gemini/antigravity/brain/65189261-0fd5-4598-8f71-d1a65df3c7d2/artifacts/edge_benchmarking_results.md).
