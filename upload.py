"""
Google Earth Engine upload utilities
"""
import os
import logging
import subprocess
from csv_handler import enhance_metadata_csv


def upload_to_gee(folder_path, destination_path, metadata_path, user_email, downloaded_files=None):
    """
    Upload data to Google Earth Engine using geeup
    
    Args:
        folder_path: Local folder containing files to upload
        destination_path: GEE destination path
        metadata_path: Path to metadata CSV file
        user_email: GEE user email
        downloaded_files: Optional list of downloaded file information
        
    Returns:
        bool: True if successful, False otherwise
    """
    logging.info(f"Uploading data from {folder_path} to {destination_path}")

    # Generate folder-specific metadata path
    folder_name = os.path.basename(folder_path)
    folder_metadata_path = metadata_path.replace('.csv', f'_{folder_name}.csv')

    # Generate metadata CSV for this specific folder
    if not _generate_metadata_csv(folder_path, folder_metadata_path):
        return False

    # Enhance metadata with additional properties
    enhance_metadata_csv(
        folder_metadata_path,
        {folder_name: folder_path},
        downloaded_files
    )

    # Upload to GEE
    return _upload_with_geeup(folder_path, destination_path, folder_metadata_path, user_email)


def _generate_metadata_csv(folder_path, metadata_path):
    """Generate metadata CSV using geeup"""
    generate_csv_command = f'geeup getmeta --input {folder_path} --metadata {metadata_path}'
    logging.info(f"Running command: {generate_csv_command}")

    try:
        subprocess.run(generate_csv_command, shell=True, check=True)
        logging.info(f"Metadata CSV generated successfully")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error generating metadata CSV: {str(e)}")
        return False


def _upload_with_geeup(folder_path, destination_path, metadata_path, user_email):
    """Upload to GEE using geeup"""
    upload_command = f'geeup upload --source {folder_path} --dest {destination_path} -m {metadata_path} -u {user_email}'
    logging.info(f"Running command: {upload_command}")
    print(f"Uploading to GEE: {folder_path} -> {destination_path}")

    try:
        subprocess.run(upload_command, shell=True, check=True)
        logging.info(f"Upload to {destination_path} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during geeup upload: {str(e)}")
        return False
