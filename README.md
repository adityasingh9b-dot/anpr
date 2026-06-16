# 🚗 Low-Latency Indian ANPR Video Ingestion Pipeline (Week 1)

A high-performance **hybrid C++ and Python video ingestion engine** designed for real-time **Indian Automatic Number Plate Recognition (ANPR)** systems.

This module eliminates runtime memory allocation bottlenecks commonly found in pure Python video pipelines by leveraging:

* Native hardware video streams
* In-place matrix transformations
* Pre-allocated memory buffers
* Zero-copy memory sharing using PyBind11

---

# 📖 Overview

The goal of this project is to build a low-latency video ingestion layer capable of feeding downstream ANPR models efficiently.

Instead of repeatedly allocating memory for every incoming frame, the pipeline performs all processing inside pre-allocated native buffers and exposes the processed frame directly to Python through NumPy-compatible memory views.

---

# 🏎️ The Problem: Pure Python Video Processing

## 🔴 Baseline Approach (`ingestion.py`)

The initial implementation was written entirely in Python.

While functional, high-frequency video processing introduces significant overhead due to continuous memory allocation and deallocation.

### Bottlenecks

For every captured frame:

* Python allocates fresh memory buffers.
* Color-space conversions create additional temporary arrays.
* Resizing operations allocate new matrices.
* Garbage collection introduces unpredictable latency spikes.

At **30+ FPS**, these repeated allocations consume CPU cycles and increase end-to-end latency.

---

# ⚡ Optimized Hybrid Architecture

## 🟢 C++ Core + Python Interface

The ingestion layer was rewritten in native C++ and exposed to Python through **PyBind11**.

Relevant files:

* `src/pipeline.cpp`
* `test_pipeline.py`

### Key Optimizations

#### 1. Pre-Allocated Static Context

Memory buffers are allocated only once during startup:

* `frame` → Raw BGR frame
* `gray` → Grayscale buffer
* `resized` → Downsampled output buffer

No allocations occur inside the processing loop.

---

#### 2. In-Place Frame Processing

All frame transformations occur within the same memory regions.

Benefits:

* No repeated heap allocations
* Reduced CPU overhead
* Consistent frame processing latency

---

#### 3. Zero-Copy Memory Sharing

Instead of copying frame data from C++ into Python:

* PyBind11 exports a `py::buffer_info`
* Buffer metadata includes:

  * Dimensions
  * Strides
  * Raw data pointers

Python then creates a NumPy array directly over the native C++ memory buffer.

Result:

* No frame duplication
* No serialization overhead
* Near-zero transfer latency

---

# 📁 Repository Structure

```text
.
├── CMakeLists.txt
├── README.md
├── .gitignore
├── src/
│   └── pipeline.cpp
├── test_pipeline.py
└── ingestion.py
```

### File Descriptions

| File               | Description                                    |
| ------------------ | ---------------------------------------------- |
| `CMakeLists.txt`   | Build configuration for CMake                  |
| `README.md`        | Project documentation                          |
| `.gitignore`       | Excludes build artifacts and environment files |
| `src/pipeline.cpp` | Native C++ ingestion engine (V4L2)             |
| `test_pipeline.py` | Zero-copy evaluation script                    |
| `ingestion.py`     | Legacy pure Python implementation              |

---

# 🛠️ Prerequisites

## Linux / Ubuntu Dependencies

Install compiler toolchains and OpenCV development libraries:

```bash
sudo apt update
sudo apt install build-essential cmake libopencv-dev python3-dev
```

---

## Python Environment Setup

Activate your virtual environment:

```bash
source venv/bin/activate
```

Install required packages:

```bash
pip install opencv-python pybind11 numpy ultralytics
```

---

# ⚙️ Build Instructions

## Step 1: Compile the Native C++ Module

Generate and build the shared object library:

```bash
# Create build directory
mkdir build
cd build

# Generate build files
cmake ..

# Compile
make

# Copy generated module to project root
cp cpp_ingestion*.so ..

cd ..
```

After compilation, the generated module will be available as:

```text
cpp_ingestion.so
```

---

# ▶️ Running the Optimized Pipeline

Launch the zero-copy testing pipeline:

```bash
python3 test_pipeline.py
```

The script will:

* Load the compiled C++ module
* Connect to the camera using Linux V4L2
* Perform grayscale conversion and resizing
* Display the processed stream
* Report live latency metrics

### Exit

Press:

```text
q
```

to terminate the stream safely.

---

# 🧪 Baseline Comparison

To compare performance against the original Python implementation:

```bash
python3 ingestion.py
```

This provides a direct reference for measuring:

* Memory overhead
* CPU utilization
* Frame latency
* Allocation cost

---

# 📊 Week 1 Achievements

### ✅ Zero Runtime Allocation

Moved frame buffers from dynamic per-frame allocations to static native memory.

### ✅ Native Hardware Ingestion

Integrated Linux camera streams using:

```cpp
cv::CAP_V4L2
```

for lower-overhead video capture.

### ✅ Zero-Copy Python Integration

Mapped native C++ memory directly into NumPy arrays using PyBind11 buffer interfaces.

### ✅ Efficient Memory Layout Management

Implemented stride-aware buffer descriptors:

```cpp
sizeof(unsigned char) * columns
```

ensuring correct multidimensional memory mapping without pixel corruption.

---

# 🎯 Current Outcome

The ingestion pipeline now delivers:

* Low-latency frame acquisition
* Zero-copy C++ → Python transfer
* Minimal memory overhead
* Stable real-time performance suitable for ANPR workloads

This forms the foundation for upcoming stages involving:

* Vehicle detection
* Number plate localization
* OCR inference
* End-to-end Indian ANPR deployment

