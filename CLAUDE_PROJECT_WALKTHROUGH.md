# Detecto Project Walkthrough (for Claude)

This repository contains a **malware analysis desktop app** built with **PyQt5**.  
It combines:

1. **Static analysis** (hashes, PE parsing, strings/IOCs, entropy, heuristic threat scoring)
2. **VirusTotal lookup** (by SHA-256, integrated into the static workflow)
3. **Dynamic analysis** via **Hybrid Analysis API** (parallel background flow)

---

## 1) Repository layout

```text
Detecto/
├─ requirements.txt
├─ StaticAnlysis/                      # legacy prototype scripts
│  ├─ hash_logic.py
│  ├─ strings.py
│  ├─ main.py                          # empty
│  └─ file.txt
└─ malware_analyzer/                   # main application
   ├─ main.py                          # app entry point
   ├─ config.py                        # API keys + dynamic timing config
   ├─ example_usage.py                 # CLI static-analysis example
   ├─ controller/
   │  └─ main_controller.py
   ├─ workers/
   │  ├─ analysis_worker.py            # static + VT worker
   │  └─ dynamic_analysis_worker.py    # Hybrid Analysis worker
   ├─ model/
   │  ├─ static/
   │  │  ├─ static_analyzer.py
   │  │  ├─ hash_analysis.py
   │  │  ├─ pe_analysis.py
   │  │  ├─ string_extractor.py
   │  │  ├─ entropy_analysis.py
   │  │  └─ strings_analysis.py        # empty
   │  ├─ dynamic/
   │  │  └─ hybrid_analysis_client.py
   │  └─ report/
   │     └─ generator.py               # empty
   ├─ view/
   │  ├─ main_window.py                # splash/upload/processing/results screens
   │  ├─ styles.py                     # QSS/theme constants
   │  └─ components/
   │     ├─ processing_widget.py
   │     ├─ result_viewer.py
   │     ├─ dashboard_widgets.py
   │     ├─ file_uploader.py           # empty (upload UI lives in main_window.py)
   │     └─ progress_bar.py            # empty
   ├─ utils/
   │  ├─ helpers.py
   │  └─ constants.py
   └─ resources/
      └─ styles.qss                    # empty
```

---

## 2) Runtime architecture and control flow

### Entry wiring
- `malware_analyzer/main.py` creates `QApplication`, `MainWindow`, and `FileController`.
- It connects `view.upload_clicked` to:
  - `controller.start_processing` (static flow)
  - a local `_start_dynamic()` wrapper that calls `controller.on_continue_clicked(...)` (dynamic flow)

So one upload click starts **both flows in parallel**.

### UI lifecycle
`view/main_window.py` uses a stacked UI with 4 screens:
1. Splash
2. Upload
3. Processing
4. Results

Main signal path:
- Upload screen emits selected file path
- MainWindow switches to processing and emits `upload_clicked(path)`
- Controller starts workers on QThreads
- Workers emit progress/status/results/errors
- MainWindow forwards to results dashboard (`ResultsWidget`)

### Worker model
- `workers/analysis_worker.py`:
  - Runs `StaticAnalyzer.analyze_file()`
  - Adds compatibility fields and metadata
  - Performs VirusTotal lookup (`_analyze_virustotal`)
  - Emits unified result dict

- `workers/dynamic_analysis_worker.py`:
  - Uses `HybridAnalysisClient`
  - Submits sample, polls report until ready/timeout
  - Emits parsed dynamic result or typed error code

---

## 3) Static analysis pipeline (core engine)

`model/static/static_analyzer.py` orchestrates:

1. `hash_analysis.py`  
   - MD5 / SHA1 / SHA256 in streaming mode
   - basic file-type detection by magic bytes

2. `pe_analysis.py`  
   - PE headers, sections, imports/exports
   - anomalies (RWX sections, entry-point anomalies, disabled ASLR/DEP, TLS callbacks, suspicious imports)

3. `string_extractor.py`  
   - ASCII + UTF-16LE strings
   - IOC categories: URLs, IPs, emails, registry keys, file paths, PowerShell, suspicious commands, crypto wallets

4. `entropy_analysis.py`  
   - whole-file Shannon entropy
   - per-section entropy and packing suspicion

5. Threat scoring engine (inside `static_analyzer.py`)  
   - weighted heuristic scoring mapped to levels: `Low`, `Medium`, `High`, `Critical`
   - returns factors used to build timeline and executive summary

Output is a JSON-serializable dict with sections like:
- `file_info`, `hashes`, `pe_analysis`, `strings`, `entropy`, `threat_assessment`, `summary`

---

## 4) Dynamic analysis flow (Hybrid Analysis)

### Client
`model/dynamic/hybrid_analysis_client.py`:
- Reads API key from:
  1. passed argument
  2. `HA_API_KEY` env var
  3. `config.HYBRID_ANALYSIS_API_KEY`
- Handles typed errors: missing key, invalid key, rate limit, network, not ready, generic analysis errors

### Worker behavior
`workers/dynamic_analysis_worker.py`:
- Submit file
- Poll `/report/{sha256}:{env}/summary` every configured interval
- Stop on timeout
- Normalize response with `parse_report()`

### UI merge
`MainWindow.show_dynamic_results()` merges dynamic payload under:
- `result["dynamic"] = <parsed dynamic report>`

Results dashboard focuses mostly on static/VT surfaces, but raw JSON includes dynamic data.

---

## 5) Results dashboard behavior

`view/components/result_viewer.py` renders a SOC-style dashboard with tabs:
- Overview
- PE Analysis
- Strings & IOCs
- Entropy
- VirusTotal
- Findings Timeline
- Raw JSON
- Export (JSON/HTML/PDF)

Important behavior:
- Tabs are conditionally shown based on available data.
- VirusTotal section expects `virustotal.engines`, `detection_ratio`, `scan_date`, `permalink`.
- Failed analyses are shown with banner/status while still allowing raw result export.

---

## 6) Configuration and external dependencies

### Python dependencies
- `PyQt5`
- `pefile`
- `requests` is used in code (`hybrid_analysis_client.py`) but currently **not listed** in `requirements.txt`.

### Config values
`malware_analyzer/config.py` contains:
- `VT_API_KEY`
- `HYBRID_ANALYSIS_API_KEY`
- `HYBRID_ANALYSIS_ENV_ID`
- timeout + polling controls

Environment variables are supported and should be preferred in production.

---

## 7) Legacy and placeholder files

These are currently not active in the main app flow:
- `StaticAnlysis/*` (legacy prototype scripts; likely earlier phase)
- Empty files:
  - `malware_analyzer/model/report/generator.py`
  - `malware_analyzer/model/static/strings_analysis.py`
  - `malware_analyzer/view/components/file_uploader.py`
  - `malware_analyzer/view/components/progress_bar.py`
  - `malware_analyzer/resources/styles.qss`
  - `StaticAnlysis/main.py`

---

## 8) Quick run guide

From repo root:

```bash
pip install -r requirements.txt
cd malware_analyzer
python main.py
```

Optional CLI static analysis path:

```bash
cd malware_analyzer
python example_usage.py <path_to_sample>
```

---

## 9) Practical notes for future contributors (or Claude)

1. Upload triggers static and dynamic workers simultaneously; they are independent.
2. Cancel currently targets the static worker path; dynamic cancellation is not fully wired into the same cancel button flow.
3. VirusTotal is queried inside the static worker after static analysis finishes.
4. Results UI is dense and mostly centralized in `result_viewer.py`; most rendering/debugging work will happen there.
5. `main_window.py` includes both splash and upload widget definitions (not split into separate component files yet).
