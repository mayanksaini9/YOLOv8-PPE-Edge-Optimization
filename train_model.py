import os
from ultralytics import YOLO

def main():
    # Load pretrained YOLOv8n model
    print("Loading pretrained YOLOv8n model...", flush=True)
    model = YOLO("yolov8n.pt")
    
    # Train the model
    # We train for 3 epochs, image size 640, and force CPU training
    # Set workers=0 to avoid potential Windows multiprocessing issues
    print("Starting training...", flush=True)
    results = model.train(
        data=os.path.join("dataset", "processed", "data.yaml"),
        epochs=3,
        imgsz=320,
        device="cpu",
        workers=0
    )
    print("Training completed successfully!", flush=True)
    
if __name__ == "__main__":
    main()
