import os
import cv2
import time
import argparse
import numpy as np

# Try to import onnxruntime and ultralytics
try:
    import onnxruntime as ort
except ImportError:
    ort = None

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

def parse_args():
    parser = argparse.ArgumentParser(description="YOLOv8 Edge Inference Benchmarking")
    parser.add_argument("--model", type=str, default="yolov8n.onnx", help="Path to model file (.pt or .onnx)")
    parser.add_argument("--source", type=str, default="dataset/processed/images/test", 
                        help="Path to video file, image file, directory of images, or webcam index (int)")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--nms", type=float, default=0.45, help="NMS threshold")
    parser.add_argument("--save-dir", type=str, default="inference_results", help="Directory to save output results")
    parser.add_argument("--no-show", action="store_true", help="Disable display window")
    return parser.parse_args()

class ONNXYOLOModel:
    def __init__(self, model_path):
        print(f"Initializing ONNX Runtime session for {model_path}...")
        # Load the ONNX model using ONNX Runtime
        self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape # e.g. [1, 3, 640, 640]
        self.input_size = self.input_shape[2] # 640
        self.classes = {0: "hardhat", 1: "no-hardhat"} # Hard-coded from dataset data.yaml

    def predict(self, frame, conf_threshold=0.25, nms_threshold=0.45):
        h, w = frame.shape[:2]
        
        # 1. Preprocessing
        t0 = time.time()
        # Resize frame to model input size (640x640)
        img = cv2.resize(frame, (self.input_size, self.input_size))
        # Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Normalize to [0, 1]
        img = img.astype(np.float32) / 255.0
        # Transpose: HWC to CHW
        img = img.transpose(2, 0, 1)
        # Add batch dimension: (1, 3, 640, 640)
        blob = np.expand_dims(img, axis=0)
        preprocess_ms = (time.time() - t0) * 1000.0

        # 2. Inference
        t1 = time.time()
        outputs = self.session.run([self.output_name], {self.input_name: blob})
        inference_ms = (time.time() - t1) * 1000.0

        # 3. Postprocessing (parsing + NMS)
        t2 = time.time()
        output = outputs[0][0] # Shape: (6, 8400)
        output = output.T # Shape: (8400, 6)

        boxes = []
        confidences = []
        class_ids = []

        for row in output:
            scores = row[4:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > conf_threshold:
                # Bbox center_x, center_y, width, height (in 640x640 space)
                cx, cy, bw, bh = row[0:4]
                # Convert to top-left x, y
                x_min = cx - bw / 2.0
                y_min = cy - bh / 2.0
                
                # Scale coordinates to original frame size
                x = int(x_min * w / self.input_size)
                y = int(y_min * h / self.input_size)
                width = int(bw * w / self.input_size)
                height = int(bh * h / self.input_size)
                
                boxes.append([x, y, width, height])
                confidences.append(float(confidence))
                class_ids.append(int(class_id))

        # Apply Non-Maximum Suppression (NMS)
        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
        
        detections = []
        if len(indices) > 0:
            for idx in indices:
                # Handle varying shapes returned by NMSBoxes across OpenCV versions
                if isinstance(idx, (list, np.ndarray)):
                    i = idx[0]
                else:
                    i = idx
                detections.append({
                    "box": boxes[i],
                    "confidence": confidences[i],
                    "class_id": class_ids[i],
                    "label": self.classes.get(class_ids[i], f"class_{class_ids[i]}")
                })
        postprocess_ms = (time.time() - t2) * 1000.0

        return detections, preprocess_ms, inference_ms, postprocess_ms

def main():
    args = parse_args()
    
    # Create save directory
    os.makedirs(args.save_dir, exist_ok=True)
    
    # Initialize the correct model loader
    is_onnx = args.model.endswith(".onnx")
    is_pytorch = args.model.endswith(".pt")
    
    if is_onnx:
        if ort is None:
            raise ImportError("onnxruntime is not installed, but required to run ONNX models.")
        model = ONNXYOLOModel(args.model)
    elif is_pytorch:
        if YOLO is None:
            raise ImportError("ultralytics is not installed, but required to run PyTorch (.pt) models.")
        print(f"Loading PyTorch YOLO model from {args.model}...")
        model = YOLO(args.model)
    else:
        raise ValueError("Model file must end with .onnx or .pt")

    # Set up source
    # Check if source is integer (webcam index)
    try:
        source_idx = int(args.source)
        cap = cv2.VideoCapture(source_idx)
        is_video = True
        input_files = []
        print(f"Using webcam index {source_idx}...")
    except ValueError:
        # Source is a path
        if os.path.isdir(args.source):
            # Directory of images
            input_files = [os.path.join(args.source, f) for f in os.listdir(args.source) 
                           if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
            input_files.sort()
            cap = None
            is_video = False
            print(f"Found {len(input_files)} images in directory {args.source}")
        elif os.path.isfile(args.source):
            # Check if image or video
            ext = os.path.splitext(args.source)[1].lower()
            if ext in ('.mp4', '.avi', '.mov', '.mkv'):
                cap = cv2.VideoCapture(args.source)
                is_video = True
                input_files = []
                print(f"Opening video file: {args.source}")
            else:
                cap = None
                is_video = False
                input_files = [args.source]
                print(f"Opening image file: {args.source}")
        else:
            raise FileNotFoundError(f"Source path '{args.source}' not found.")

    frame_count = 0
    total_fps = 0.0
    
    # Loop over frames/images
    while True:
        t_frame_start = time.time()
        
        if is_video:
            ret, frame = cap.read()
            if not ret:
                break
            filename = f"frame_{frame_count:04d}.jpg"
        else:
            if frame_count >= len(input_files):
                break
            img_path = input_files[frame_count]
            frame = cv2.imread(img_path)
            if frame is None:
                frame_count += 1
                continue
            filename = os.path.basename(img_path)

        h, w = frame.shape[:2]
        
        # Run inference and time latencies
        if is_onnx:
            detections, prep_ms, inf_ms, post_ms = model.predict(frame, args.conf, args.nms)
        else:
            # PyTorch inference
            t0 = time.time()
            # Under the hood PyTorch preprocessing
            # Run inference
            t_inf_start = time.time()
            results = model(frame, conf=args.conf, iou=args.nms, verbose=False)
            t_inf_end = time.time()
            
            # Retrieve speed metrics dictionary from Ultralytics results
            # Speed is dict: {'preprocess': ms, 'inference': ms, 'postprocess': ms}
            speed = results[0].speed
            prep_ms = speed['preprocess']
            inf_ms = speed['inference']
            post_ms = speed['postprocess']
            
            detections = []
            boxes_data = results[0].boxes
            for box in boxes_data:
                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                label = model.names[cls_id]
                x1, y1, x2, y2 = xyxy
                detections.append({
                    "box": [x1, y1, x2 - x1, y2 - y1],
                    "confidence": conf,
                    "class_id": cls_id,
                    "label": label
                })

        # Calculate FPS based on end-to-end processing of this frame
        t_frame_end = time.time()
        frame_time = t_frame_end - t_frame_start
        fps = 1.0 / frame_time if frame_time > 0 else 0.0
        
        # Accumulate metrics
        frame_count += 1
        total_fps += fps

        # Draw bounding boxes and overlay information
        display_frame = frame.copy()
        
        for det in detections:
            x, y, bw, bh = det["box"]
            conf = det["confidence"]
            label = det["label"]
            
            # Choose color based on class
            # Hardhat = Green, No-Hardhat = Red
            color = (0, 255, 0) if det["class_id"] == 0 else (0, 0, 255)
            
            # Draw bbox
            cv2.rectangle(display_frame, (x, y), (x + bw, y + bh), color, 2)
            
            # Label text
            text = f"{label}: {conf:.2f}"
            (tw, th), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(display_frame, (x, y - th - 5), (x + tw, y), color, -1)
            cv2.putText(display_frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Draw performance overlay box
        # Dark semi-transparent box background for premium look
        overlay_bg = display_frame.copy()
        cv2.rectangle(overlay_bg, (10, 10), (320, 140), (0, 0, 0), -1)
        cv2.addWeighted(overlay_bg, 0.6, display_frame, 0.4, 0, display_frame)
        
        # Add metrics text
        cv2.putText(display_frame, f"Model: {os.path.basename(args.model)}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv2.putText(display_frame, f"FPS: {fps:.2f}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(display_frame, f"Pre-process: {prep_ms:.2f} ms", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(display_frame, f"Inference: {inf_ms:.2f} ms", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(display_frame, f"Post-process (NMS): {post_ms:.2f} ms", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(display_frame, f"Resolution: {w}x{h}", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Save result image
        save_path = os.path.join(args.save_dir, filename)
        cv2.imwrite(save_path, display_frame)

        # Display result
        if not args.no_show:
            cv2.imshow("YOLOv8 Edge Inference Benchmark", display_frame)
            
            # Wait key depending on source
            wait_time = 1 if is_video else 500
            key = cv2.waitKey(wait_time) & 0xFF
            if key == ord('q'):
                break

    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()
    
    avg_fps = total_fps / frame_count if frame_count > 0 else 0.0
    print("\n" + "="*40)
    print("INFERENCE SUMMARY")
    print("="*40)
    print(f"Model File: {args.model}")
    print(f"Processed:  {frame_count} frames/images")
    print(f"Average FPS: {avg_fps:.2f}")
    print(f"Results saved in: {args.save_dir}")
    print("="*40)

if __name__ == "__main__":
    main()
