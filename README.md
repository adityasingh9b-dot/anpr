# 🚗 Real-Time Indian ANPR System (Full-Stack)

> High-performance, low-latency Automatic Number Plate Recognition (ANPR) system built with a hybrid **C++ ingestion engine**, **YOLOv8 plate detector**, **EasyOCR recognition pipeline**, **FastAPI backend**, and a real-time operator dashboard.

---

## ✨ Features

* ⚡ Native C++ OpenCV ingestion pipeline
* 🔄 Zero-copy frame transfer via PyBind11
* 🎯 YOLOv8 fine-tuned for Indian number plates
* 🔤 EasyOCR-based plate text extraction
* 🚦 Vehicle pass lifecycle management
* 🗄️ SQLite relational database
* 🌐 FastAPI REST backend
* 📊 Real-time operator dashboard
* 🔍 OCR voting mechanism for stable recognition
* 📈 Designed for sub-100ms processing latency

---

# 📐 System Architecture

```text
┌─────────────────────┐
│ USB/IP Camera Feed  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ C++ OpenCV Engine   │
│ Frame Acquisition   │
└──────────┬──────────┘
           │ Zero-Copy
           ▼
┌─────────────────────┐
│ PyBind11 Interface  │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ YOLOv8 Detector     │
│ Plate Localization  │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ EasyOCR Engine      │
│ Plate Recognition   │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ SQLite Database     │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ FastAPI Dashboard   │
└─────────────────────┘
```

---

# 📅 Development Roadmap

| Week | Milestone          | Deliverables                                            |
| ---- | ------------------ | ------------------------------------------------------- |
| 1    | Ingestion Pipeline | Native C++ OpenCV loop with PyBind11 zero-copy sharing  |
| 2    | ML Engine          | YOLOv8 detector + EasyOCR integration for Indian plates |
| 3    | Data Lifecycle     | Vehicle pass schema, business rules & audit history     |
| 4    | Operator UI        | Dashboard, APIs, documentation and deployment           |

---

# 🛠️ Technology Stack

## Core Processing

* C++
* OpenCV
* PyBind11

## Machine Learning

* YOLOv8
* EasyOCR
* NumPy

## Backend

* FastAPI
* Uvicorn

## Database

* SQLite

## Frontend

* Bootstrap 5
* JavaScript
* Glassmorphism UI

---

# 📂 Project Structure

```text
anpr/
│
├── src/
│   └── pipeline.cpp
│
├── models/
│   └── anpr_plate_detector_v1.pt
│
├── datasets/
│   └── indian_anpr/
│
├── runs/
│
├── build/
│
├── ingestion.py
├── test_pipeline.py
├── main.py
│
└── README.md
```

---

# 🚀 Quick Start

## 1. Clone Repository

```bash
git clone https://github.com/adityasingh9b-dot/anpr.git

cd anpr
```

---

## 2. Install Dependencies

### System Packages

```bash
sudo apt update

sudo apt install \
build-essential \
cmake \
libopencv-dev \
python3-dev
```

### Python Packages

```bash
pip install -r requirements.txt
```

---

## 3. Build C++ Engine

```bash
mkdir build

cd build

cmake ..

make -j$(nproc)
```

---

## 4. Test Camera Pipeline

```bash
python test_pipeline_with_ocr.py
```

---

## 5. Run Full ANPR Pipeline

```bash
LD_PRELOAD="/usr/lib/x86_64-linux-gnu/libglib-2.0.so.0 /usr/lib/x86_64-linux-gnu/libpango-1.0.so.0" python3 test_pipeline_with_ocr.py
```

---

## 6. Launch Dashboard

```bash
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

---

# 🧠 Machine Learning Pipeline

### Stage 1 — Detection

Custom YOLOv8 model trained on Indian license plate datasets.

Output:

```text
Vehicle Image
        ↓
Plate Bounding Box
```

---

### Stage 2 — OCR

EasyOCR extracts text from cropped plate image.

Output:

```text
UP76AB1234
```

---

### Stage 3 — Voting Logic

Multiple frame predictions are aggregated.

Example:

```text
UP76AB1234
UP76AB1234
UP76AB1234
UP76AB1284
UP76AB1234
```

Final Output:

```text
UP76AB1234
```

---

# 🗄️ Database Design

## vehicles

| Column       | Type     |
| ------------ | -------- |
| id           | INTEGER  |
| plate_number | TEXT     |
| status       | TEXT     |
| created_at   | DATETIME |

---

## passes

| Column      | Type     |
| ----------- | -------- |
| id          | INTEGER  |
| vehicle_id  | INTEGER  |
| detected_at | DATETIME |
| confidence  | REAL     |

---

# ⚡ Performance Optimizations

## Zero-Copy Memory Sharing

Frames are transferred directly from C++ memory into NumPy without heap duplication.

Benefits:

* Reduced memory usage
* Lower latency
* Higher FPS

---

## OCR Stabilization

Uses frame voting:

```python
Counter(predictions).most_common(1)
```

to eliminate OCR jitter.

---

## Database Efficiency

Optimized JOIN queries for dashboard updates.

---

# 📊 Current Model Performance

| Metric    | Score |
| --------- | ----- |
| Precision | 95.2% |
| Recall    | 79.0% |
| mAP@50    | 85.4% |
| mAP@50-95 | 42.4% |

Model:

```text
YOLOv8n
```

Dataset:

```text
Indian Number Plates
```

---

# 📸 Screenshots

## Detection

```text
[Insert Detection Screenshot]
```

## OCR Recognition

```text
[Insert OCR Screenshot]
```

## Operator Dashboard

```text
[Insert Dashboard Screenshot]
```

---

# 🔮 Future Improvements

* TensorRT acceleration
* Multi-camera support
* Redis event queue
* PostgreSQL migration
* Docker deployment
* Kubernetes scaling
* Automatic blacklist alerts
* HSRP-specific OCR model
* DeepSORT vehicle tracking

---

# 🤝 Contributing

Pull requests are welcome.

For major changes, open an issue first to discuss the proposed modifications.

---

# 📄 License

MIT License

---

# 👨‍💻 Author

Aditya Singh

Real-Time Indian ANPR System

Built as a full-stack computer vision engineering project combining native systems programming, machine learning, backend APIs, and operator-facing web interfaces.

