"""
CSV metadata enhancement utilities
"""
import os
import csv
import re
import logging
from datetime import datetime
from metadata import get_epsg_from_mgrs


def enhance_metadata_csv(metadata_path, download_folders, downloaded_files=None):
    """
    Enhance the CSV metadata file with information from granule metadata
    
    Args:
        metadata_path: Path to the metadata CSV file
        download_folders: Dictionary of folder paths
        downloaded_files: Optional list of downloaded file information
        
    Returns:
        bool: True if successful, False otherwise
    """
    logging.info(f"Enhancing metadata in {metadata_path}")

    if not os.path.exists(metadata_path):
        logging.error(f"Metadata file not found: {metadata_path}")
        return False

    try:
        # Read existing CSV
        with open(metadata_path, mode='r') as file:
            reader = csv.DictReader(file)
            rows = list(reader)

        # Add essential fields to each row
        _initialize_metadata_fields(rows)

        # Populate metadata from downloaded files or folders
        if downloaded_files:
            _populate_from_downloaded_files(rows, downloaded_files)
        else:
            _populate_from_folders(rows, download_folders)

        # Write updated CSV
        with open(metadata_path, mode='w', newline='') as file:
            fieldnames = rows[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        logging.info(f"Enhanced metadata saved to {metadata_path}")
        return True

    except Exception as e:
        logging.error(f"Error enhancing metadata: {str(e)}")
        return False


def _initialize_metadata_fields(rows):
    """Initialize metadata fields in CSV rows"""
    field_list = [
        'system:time_start', 'system:time_end', 'EPSG', 'band_type',
        'attr_identifier_product_doi', 'attr_identifier_product_doi_authority',
        'begin_orbit_number', 'beginning_date_time', 'collection_concept_id',
        'concept_id', 'concept_type', 'day_night_flag', 'east_lon',
        'end_orbit_number', 'ending_date_time', 'format', 'granule_ur',
        'mgrs_tile', 'native_id', 'north_lat', 'orbit_number',
        'orbit_number_from_filename', 'parameter_names', 'pge_version',
        'platform_short_name', 'processing_ID', 'processing_level',
        'production_date_time', 'provider_date_insert', 'provider_date_update',
        'provider_id', 'revision_date', 'revision_id', 'sensor', 'short_name',
        'size_mb', 'south_lat', 'time_start', 'version', 'version_from_filename',
        'west_lon', 'scene', 'orbit_scene'
    ]
    
    for row in rows:
        for field in field_list:
            row[field] = ''


def _populate_from_downloaded_files(rows, downloaded_files):
    """Populate metadata from downloaded files information"""
    for filename, folder_path, file_type, granule_metadata in downloaded_files:
        for row in rows:
            if row['id_no'] in filename:
                _update_row_with_metadata(row, granule_metadata, file_type)


def _populate_from_folders(rows, download_folders):
    """Populate basic metadata from folder structure"""
    for folder_type, folder_path in download_folders.items():
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith('.tif'):
                    for row in rows:
                        if row['id_no'] in filename:
                            row['band_type'] = folder_type.replace('.tif', '')

                            mgrs_match = re.search(r'_(\d{2}[A-Z]{3})_', filename)
                            if mgrs_match:
                                mgrs_tile = mgrs_match.group(1)
                                row['mgrs_tile'] = mgrs_tile
                                epsg = get_epsg_from_mgrs(mgrs_tile)
                                if epsg:
                                    row['EPSG'] = epsg


def _update_row_with_metadata(row, granule_metadata, file_type):
    """Update a CSV row with granule metadata"""
    # Handle system time fields
    if 'time_start' in granule_metadata and granule_metadata['time_start']:
        row['system:time_start'] = granule_metadata['time_start']
        row['system:time_end'] = granule_metadata.get('time_start', '')
    elif 'beginning_date_time' in granule_metadata and granule_metadata['beginning_date_time']:
        try:
            begin_date = datetime.fromisoformat(
                granule_metadata['beginning_date_time'].replace('Z', '+00:00')
            )
            row['system:time_start'] = int(begin_date.timestamp() * 1000)

            if 'ending_date_time' in granule_metadata and granule_metadata['ending_date_time']:
                end_date = datetime.fromisoformat(
                    granule_metadata['ending_date_time'].replace('Z', '+00:00')
                )
                row['system:time_end'] = int(end_date.timestamp() * 1000)
            else:
                row['system:time_end'] = row['system:time_start']
        except Exception as e:
            logging.error(f"Error parsing datetime: {str(e)}")

    # Set band type
    row['band_type'] = file_type

    # Set EPSG based on MGRS tile
    if 'mgrs_tile' in granule_metadata and granule_metadata['mgrs_tile']:
        epsg = get_epsg_from_mgrs(granule_metadata['mgrs_tile'])
        if epsg:
            row['EPSG'] = epsg

    # Transfer all metadata to row
    for key, value in granule_metadata.items():
        if value is not None and key in row:
            row[key] = value
