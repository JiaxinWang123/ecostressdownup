# ECOSTRESS Data Download and Upload Tool

A modular Python application for downloading ECOSTRESS satellite data and uploading it to Google Earth Engine.

## Project Structure

```
.
├── main.py              # Main orchestration script
├── config.py            # Configuration settings
├── auth.py              # Authentication utilities
├── download.py          # Data search and download
├── upload.py            # GEE upload functionality
├── metadata.py          # Metadata extraction and processing
├── csv_handler.py       # CSV metadata enhancement
└── utils.py             # Utility functions
```

## Module Overview

### `config.py`
Centralized configuration for all settings:
- Download parameters (MGRS tile, date range, day/night)
- File types to download
- Local paths
- GEE configuration
- Logging settings

### `auth.py`
Authentication utilities:
- `authenticate_earthaccess()` - Authenticate with NASA Earthdata
- `authenticate_gee()` - Authenticate with Google Earth Engine

### `download.py`
Data acquisition:
- `search_ecostress_data()` - Search for ECOSTRESS granules
- `download_data()` - Download files to local directories

### `metadata.py`
Metadata extraction and processing:
- `extract_granule_metadata()` - Extract comprehensive metadata from granules
- `get_epsg_from_mgrs()` - Convert MGRS tiles to EPSG codes
- Various helper functions for parsing metadata components

### `csv_handler.py`
CSV metadata management:
- `enhance_metadata_csv()` - Add metadata to CSV files for GEE upload
- Helper functions for populating metadata fields

### `upload.py`
GEE upload functionality:
- `upload_to_gee()` - Upload data to Google Earth Engine using geeup

### `utils.py`
Utility functions:
- `create_download_paths()` - Generate download directory structure
- `create_upload_paths()` - Generate GEE upload paths
- `organize_files_by_type()` - Organize downloaded files by type

### `main.py`
Main orchestration script that coordinates the entire workflow

## Usage

1. **Configure settings** in `config.py`:
   ```python
   MGRS_TILE = "18TUN"
   START_DATE = "2025-01-01"
   END_DATE = "2025-08-14"
   ACTION = "both"  # "download", "upload", or "both"
   ```

2. **Run the script**:
   ```bash
   python main.py
   ```

## Workflow

1. **Authentication**: Authenticate with Earthdata and GEE
2. **Search**: Find ECOSTRESS granules matching criteria
3. **Download**: Download specified file types to organized directories
4. **Metadata Enhancement**: Extract and enhance metadata from granules
5. **Upload**: Upload to Google Earth Engine with enhanced metadata

## File Types

The tool downloads these ECOSTRESS data products:
- `LST.tif` - Land Surface Temperature
- `LST_err.tif` - LST Error
- `EmisWB.tif` - Emissivity
- `view_zenith.tif` - View zenith angle
- `height.tif` - Height
- `QC.tif` - Quality Control
- `cloud.tif` - Cloud mask
- `water.tif` - Water mask

## Requirements

- Python 3.7+
- `earthaccess` - NASA Earthdata access
- `ee` - Google Earth Engine Python API
- `geeup` - Command-line tool for GEE uploads
- GDAL - Geospatial Data Abstraction Library (required by geeup)

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install packages individually:

```bash
pip install earthaccess
pip install earthengine-api
pip install geeup
```

### 2. Install GDAL

GDAL is required by geeup for handling GeoTIFF files.

**Windows:**
- Download and install from [OSGeo4W](https://trac.osgeo.org/osgeo4w/) or
- Use conda: `conda install -c conda-forge gdal`

**macOS:**
```bash
brew install gdal
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install gdal-bin python3-gdal
```

### 3. Authenticate Services

**NASA Earthdata:**

Option A - Using .netrc file (recommended):
- Create a `.netrc` file in your home directory with your Earthdata credentials:
  ```
  machine urs.earthdata.nasa.gov
  login YOUR_USERNAME
  password YOUR_PASSWORD
  ```
- Set permissions: `chmod 600 ~/.netrc`

Option B - Interactive login:
- The script will prompt you for credentials if `.netrc` is not found

**Google Earth Engine:**

**IMPORTANT: You must authenticate BEFORE running the script for the first time.**

1. Run the authentication command:
   ```bash
   earthengine authenticate
   ```
   
2. Follow the browser prompts to authorize access

3. Make sure you have:
   - Registered for Google Earth Engine at https://earthengine.google.com/
   - Access to your GEE project (or created a new one)
   - Updated `GEE_PROJECT` in `config.py` with your project ID

**Note:** The script will check authentication status and guide you if authentication is needed.

## Logging

Logs are written to `ecostress_download_upload.log` with timestamps and severity levels.

## Notes

- Files are organized by type in separate subdirectories
- Existing files are skipped (not re-downloaded)
- Metadata is automatically extracted and enhanced
- Each file type is uploaded to a separate GEE ImageCollection
