# AppleHealthAnalytics v0.1

Local macOS tool that processes Apple Health `export.xml` files of any size using streaming XML parsing. All processing stays on your machine.

## Requirements

- macOS
- Python 3.11 or newer
- No external Python dependencies (standard library only)

macOS does not include Python 3.11 by default. Install it before proceeding.

## Installation (clean macOS)

### 1. Install Python 3.11

Using Homebrew:

```bash
brew install python@3.11
```

Verify the version:

```bash
python3.11 --version
```

Alternatively, download the macOS installer from [python.org](https://www.python.org/downloads/).

### 2. Get the project

Clone or copy this repository to your Mac, then open a terminal in the project directory:

```bash
cd /path/to/AppleHealthAnalytics
```

### 3. Create a virtual environment (recommended)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 4. Install the project

```bash
pip install --upgrade pip setuptools
pip install -e .
```

Verify the installation:

```bash
applehealth --version
```

Expected output: `applehealth 0.1.0`

## Run without installing (alternative)

If you prefer not to install the package, run directly from the project root:

```bash
cd /path/to/AppleHealthAnalytics
python3.11 -m applehealth /path/to/export.xml -o output
```

## Process your Apple Health export

After exporting data from the Health app on iPhone, unzip the archive. The XML file is usually named `export.xml` or `exportar.xml`.

From the project directory (with the virtual environment activated if you created one):

```bash
applehealth /path/to/exportar.xml -o output
```

Replace `/path/to/exportar.xml` with the actual path to your file. Example if the file is on the Desktop:

```bash
applehealth ~/Desktop/exportar.xml -o output
```

Processing may take several minutes for large exports (multi-GB files). All output is written to the `output/` directory.

## Outputs

| File | Description |
|------|-------------|
| `health.sqlite` | SQLite database with all parsed records |
| `HeartRate.csv` | Heart rate samples |
| `HRV.csv` | Heart rate variability (SDNN) |
| `Workouts.csv` | Workout sessions |
| `Steps.csv` | Step count records |
| `ActiveEnergy.csv` | Active energy burned |
| `summary.json` | Machine-readable summary |
| `summary.md` | Human-readable summary |

## Options

```
usage: applehealth [-h] [-o OUTPUT_DIR] [--batch-size BATCH_SIZE] [-v] xml_file

positional arguments:
  xml_file              Path to Apple Health export.xml

options:
  -h, --help            show this help message and exit
  -o, --output-dir      Output directory (default: output)
  --batch-size          SQLite batch size (default: 5000)
  -v, --version         show program's version number and exit
```

## Architecture

```
export.xml  →  StreamParser  →  SQLite  →  CSV export
                                    ↓
                              summary.json / summary.md
```

- **Streaming parser** — `xml.etree.ElementTree.iterparse` with element clearing; never loads the full XML into memory.
- **SQLite** — WAL mode with batched inserts for files over 5 GB.
- **Modular packages** — `parser`, `db`, `export`, `summary`.

## Development

Install pytest separately (not required for normal use):

```bash
pip install pytest
python -m pytest tests/
```

Sample fixture: `tests/fixtures/sample_export.xml`
