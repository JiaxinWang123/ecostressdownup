"""
Configuration settings for ECOSTRESS data download and upload
"""

# Download parameters
MGRS_TILE = "18TUN"  # MGRS tile ID (e.g., 15SWD, 10SFH, 18SUE)
START_DATE = "2025-01-01"  # Start date (YYYY-MM-DD)
END_DATE = "2025-11-20"  # End date (YYYY-MM-DD)
DAY_NIGHT = "DAY"  # "DAY" or "NIGHT"

# File types to download
FILE_TYPES = [
    'LST.tif',  # Land Surface Temperature
    'LST_err.tif',  # LST Error
    'EmisWB.tif',  # Emissivity
    'view_zenith.tif',  # View zenith angle
    'height.tif',  # Height
    'QC.tif',  # Quality Control
    'cloud.tif',  # Cloud mask
    'water.tif'
]

# Paths configuration
DOWNLOAD_BASE = "/Users/jiaxinwang/Documents/ECOSTRESS/ecostress"
METADATA_PATH = "/Users/jiaxinwang/Documents/ECOSTRESS/metadata_ecostress.csv"

# GEE configuration
GEE_PROJECT = "ee-jiaxinwang36201"
GEE_UPLOAD_BASE = f"projects/{GEE_PROJECT}/Geneva/Ecostress"
GEE_EMAIL = "jiaxinwang362@gmail.com"

# Action to perform: "download", "upload", or "both"
ACTION = "both"

# Logging configuration
LOG_FILE = 'ecostress_download_upload.log'
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s:%(levelname)s:%(message)s'
