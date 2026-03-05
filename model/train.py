from ultralytics import YOLO
import torch

def main():
    model = YOLO("yolo-weights/yolo26s-seg.pt")

    model.train(
        data="dataset/data.yaml",
        epochs=100,
        imgsz=960,
        batch=8,
        device=0
    )

if __name__ == "__main__":
    torch.multiprocessing.set_start_method("spawn", force=True) 
    main()
