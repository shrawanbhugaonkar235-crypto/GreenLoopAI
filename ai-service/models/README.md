# GreenLoopAI Model Directory

Place your custom or pretrained YOLO weights (`.pt` file) in this directory or configure its absolute path in `.env`:

```env
YOLO_MODEL_PATH=models/yolov8n-waste.pt
```

## Model Architecture
- **Inference Engine**: Ultralytics YOLOv8 / YOLOv9 / YOLOv11
- **Expected Classes**: Plastic, Paper, Cardboard, Metal, Glass, E-Waste
- **Confidence Threshold**: Configured via `YOLO_CONFIDENCE_THRESHOLD` (default: 0.45)

If no model is configured or available, the system will explicitly report `AI detection model unavailable` without fabricating simulated data.
