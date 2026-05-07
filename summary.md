# Detecto — Project Analysis & Summary

## 1. Project Overview
**Detecto** is a premium malware analyzer application built with **Python** and **PyQt5**. It features a modern, frameless dark-mode interface with rich animations, implementing a robust **MVC (Model-View-Controller)** architecture and asynchronous file processing.

---

## 2. System Architecture (MVC)

### **View (UI Layer)**
- **Location:** `malware_analyzer/view/`
- **Main Class:** `MainWindow`
- **Responsibility:** Manages the visual state, transitions, and user interactions.
- **Key Components:**
  - `SplashWidget`: Animated logo entry screen.
  - `UploadWidget`: File selection area with drag-and-drop simulation.
  - `ProcessingWidget`: Progress tracking with a custom circular ring.
  - `ResultsWidget`: Dynamic grid display for analysis metadata.

### **Controller (Logic Layer)**
- **Location:** `malware_analyzer/controller/`
- **Main Class:** `FileController`
- **Responsibility:** Orchestrates the flow between the UI and the background worker.
- **Pattern:** Uses **Callback Injection** to update the UI without being tightly coupled to the View classes. It manages the lifecycle of worker threads.

### **Worker (Execution Layer)**
- **Location:** `malware_analyzer/workers/`
- **Main Class:** `FileWorker`
- **Responsibility:** Performs the "heavy lifting" on a separate `QThread`. It iterates through analysis steps and emits signals back to the controller.

### **Model (Data & Analysis Layer)**
- **Location:** `malware_analyzer/model/`
- **Modules:**
  - `static/`: Contains logic for PE structure, hash calculations (`hash_analysis.py`), and string extraction.
  - `dynamic/`: Contains placeholders/logic for sandbox monitoring and behavior analysis.
  - `report/`: Handles JSON export and report generation.

---

## 3. Step-by-Step Execution Flow

1.  **Initialization:** `main.py` initializes the `QApplication`, creates the `MainWindow`, and sets up the `FileController` with UI-update callbacks.
2.  **Splash Stage:** The app starts with the `SplashWidget`, animating the "Detecto" title. Once finished, it fades into the Upload stage.
3.  **Upload Stage:** The user selects a file via `UploadWidget`. Clicking "Continue" triggers the `upload_clicked` signal.
4.  **Analysis Stage:** 
    - `FileController` receives the path and spawns a `FileWorker` in a new `QThread`.
    - The `ProcessingWidget` is shown, animating a circular ring as the worker sends progress updates (e.g., "Reading file headers", "Computing hashes").
5.  **Results Stage:** 
    - Upon completion, the worker emits the final results.
    - `MainWindow` transitions to `ResultsWidget`, which populates and animates metadata cards (MD5, SHA256, Threat Level, etc.).
    - The user can export these results to a JSON file.

---

## 4. File-to-Class Connections

| File Path | Class / Main Logic | Connections |
| :--- | :--- | :--- |
| `main.py` | Entry Point | Wires `MainWindow` to `FileController`. |
| `main_window.py` | `MainWindow` | Owns `SplashWidget`, `UploadWidget`, `ProcessingWidget`, `ResultsWidget`. |
| `main_controller.py` | `FileController` | Instantiates `FileWorker`; connects signals to `MainWindow` slots. |
| `analysis_worker.py` | `FileWorker` | Inherits `QObject`; runs in `QThread`; emits progress/results signals. |
| `processing_widget.py`| `ProcessingWidget` | Uses `ProgressRing` (QPainter) to visualize percentage. |
| `result_viewer.py` | `ResultsWidget` | Uses `ResultCard` to display key-value pairs from analysis. |
| `hash_analysis.py` | `calculate_hash` | Provides utility functions for MD5/SHA256 generation. |

---

## 5. Key Design Patterns
- **Asynchronous Threading:** Uses `QThread` and `moveToThread` for a responsive UI.
- **Signal/Slot Communication:** Decouples worker logic from the main thread.
- **Callback Injection:** Allows the Controller to trigger UI updates without importing View classes.
- **Custom Painting:** Uses `QPainter` for high-end visual components like the rotating dashed circle and progress ring.
