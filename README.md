# ECOv2 Stability Data Analysis

A Dash-based interactive tool for analyzing ECOv2 stability test data across serial numbers, channels, and metrics.

This application is designed for **engineering validation and production readiness analysis**, with support for:
- Multi-serial comparison
- Per-serial statistical overlays (mean ± σ)
- Large CSV ingestion
- Clear visual separation of early vs late samples
- Deterministic, reproducible plots

---

## Features

### 📊 Plotting
- Two synchronized plots:
  - **Top plot:** early samples (default 1–100)
  - **Bottom plot:** later samples (default 101+)
- Selectable metrics:
  - `HGO`, `LGO`, `LTC`, `RAW`, `VMain`
- One color per serial number (stable across a plot)
- Optional multi-serial comparison

### 📈 Statistical Overlays
For each plotted serial:
- Mean line (dashed)
- +1σ and −1σ lines (dotted)

These overlays are computed from the same data shown in the plot.

### 🧪 Data Handling
- Upload a master `data.csv`
- Automatically normalizes:
  - Serial numbers
  - Channels
  - Sample counts
  - Timestamps
- Supports multiple runs per serial
- Automatically selects **latest run only** for plotting

### ⚠️ Validation Feedback
- Warns when selected serials have no data
- Does not silently fail
- Continues plotting valid serials when some are missing

---

## Data Requirements

The input CSV **must** contain the following columns:

### Required
| Column Name | Description |
|------------|------------|
| `SerialNumber` | Full serial identifier (e.g. `ECOv2-10091`) |
| `Channel` | Channel number (1-based integer) |
| `SampleCount` | Sample index (numeric, increasing) |
| `HGO` | Measurement |
| `LGO` | Measurement |
| `LTC` | Measurement |
| `RAW` | Measurement |
| `VMain` | Measurement |

### Optional (recommended)
| Column Name | Description |
|------------|------------|
| `Date` | Date string |
| `Time` | Time string |
| `FileMTime` | Unix timestamp (used if Date/Time missing) |

---

## Installation

### Python Version
- Python **3.9+** recommended

### Install Dependencies
```bash
pip install -r requirements.txt