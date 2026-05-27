import os
from ultralytics import YOLO

def main():
    # Find latest training run folder dynamically
    detect_dir = os.path.join("runs", "detect")
    run_folders = [d for d in os.listdir(detect_dir) if d.startswith("train")] if os.path.exists(detect_dir) else []
    
    if run_folders:
        # Sort folders by modification time to get the latest one
        run_folders.sort(key=lambda x: os.path.getmtime(os.path.join(detect_dir, x)), reverse=True)
        model_path = os.path.join(detect_dir, run_folders[0], "weights", "best.pt")
    else:
        model_path = "yolov8n.pt"
        
    if not os.path.exists(model_path):
        print(f"Warning: {model_path} not found. Using yolov8n.pt as fallback.")
        model_path = "yolov8n.pt"
        
    print(f"Loading model from {model_path}...", flush=True)
    model = YOLO(model_path)
    
    # Export to FP32 ONNX
    print("Exporting to FP32 ONNX...", flush=True)
    fp32_onnx_path = model.export(format="onnx")
    # Rename to preserve FP32 version
    fp32_dest = fp32_onnx_path.replace(".onnx", "_fp32.onnx")
    if os.path.exists(fp32_dest):
        os.remove(fp32_dest)
    os.rename(fp32_onnx_path, fp32_dest)
    print(f"FP32 ONNX saved to: {fp32_dest}", flush=True)
    
    # Export to FP16 ONNX (Quantized/Half-precision)
    print("Exporting to FP16 ONNX...", flush=True)
    fp16_onnx_path = model.export(format="onnx", half=True)
    # Rename to preserve FP16 version
    fp16_dest = fp16_onnx_path.replace(".onnx", "_fp16.onnx")
    if os.path.exists(fp16_dest):
        os.remove(fp16_dest)
    os.rename(fp16_onnx_path, fp16_dest)
    print(f"FP16 ONNX saved to: {fp16_dest}", flush=True)
    
if __name__ == "__main__":
    main()
