"""
ECOSTRESS Data Download and Upload to Google Earth Engine
Main script to orchestrate the entire workflow
"""
import os
import logging

# Import configuration
from config import (
    MGRS_TILE, START_DATE, END_DATE, DAY_NIGHT, FILE_TYPES,
    DOWNLOAD_BASE, METADATA_PATH, GEE_PROJECT, GEE_UPLOAD_BASE, GEE_EMAIL,
    ACTION, LOG_FILE, LOG_LEVEL, LOG_FORMAT
)

# Import modules
from auth import authenticate_earthaccess, authenticate_gee
from download import search_ecostress_data, download_data
from upload import upload_to_gee
from utils import create_download_paths, create_upload_paths, organize_files_by_type


def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        filename=LOG_FILE,
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT
    )


def authenticate_services(action):
    """
    Authenticate with required services based on action
    
    Args:
        action: The action to perform ("download", "upload", or "both")
        
    Returns:
        tuple: (earthaccess_success, gee_success)
    """
    earthaccess_success = False
    gee_success = False
    
    # Authenticate with earthaccess if downloading
    if action in ["download", "both"]:
        if not authenticate_earthaccess("netrc"):
            print("Authentication failed with netrc. Trying interactive login...")
            if not authenticate_earthaccess("interactive"):
                print("Earthaccess authentication failed. Cannot proceed with download.")
                return False, False
        earthaccess_success = True

    # Authenticate with GEE if uploading
    if action in ["upload", "both"]:
        print("\n" + "="*60)
        print("Checking Google Earth Engine Authentication")
        print("="*60)
        if not authenticate_gee(GEE_PROJECT):
            print("\nGEE authentication failed. Cannot proceed with upload.")
            print("Please fix the authentication issue and try again.")
            if action == "both":
                user_input = input("\nContinue with download only? (y/n): ").strip().lower()
                if user_input == 'y':
                    return True, False
            return earthaccess_success, False
        gee_success = True
    
    return earthaccess_success, gee_success


def download_workflow(download_paths):
    """
    Execute the download workflow
    
    Args:
        download_paths: Dictionary of download paths
        
    Returns:
        list: Downloaded files information
    """
    # Search for data
    results = search_ecostress_data(
        short_name='ECO_L2T_LSTE',
        mgrs_tile=MGRS_TILE,
        start_date=START_DATE,
        end_date=END_DATE,
        day_night=DAY_NIGHT
    )

    # Download data
    downloaded_files = download_data(results, FILE_TYPES, download_paths)

    logging.info(f"Downloaded {len(downloaded_files)} files")
    print(f"Downloaded {len(downloaded_files)} files")
    
    return downloaded_files


def upload_workflow(download_paths, upload_paths, downloaded_files_by_type):
    """
    Execute the upload workflow
    
    Args:
        download_paths: Dictionary of download paths
        upload_paths: Dictionary of upload paths
        downloaded_files_by_type: Files organized by type
    """
    for file_type, folder_path in download_paths.items():
        if os.path.exists(folder_path) and os.listdir(folder_path):
            type_name = file_type.split('.')[0]
            destination_path = upload_paths[type_name]

            print(f"Processing folder: {folder_path} -> {destination_path}")

            # Get files for this type
            files_for_type = downloaded_files_by_type.get(type_name, None)

            # Upload to GEE
            success = upload_to_gee(
                folder_path=folder_path,
                destination_path=destination_path,
                metadata_path=METADATA_PATH,
                user_email=GEE_EMAIL,
                downloaded_files=files_for_type
            )

            if success:
                print(f"Successfully uploaded {type_name} data to {destination_path}")
            else:
                print(f"Failed to upload {type_name} data")


def main():
    """Main function to execute the script"""
    setup_logging()
    
    print("=" * 60)
    print("ECOSTRESS Data Download and Upload")
    print("=" * 60)
    
    # Create paths
    download_paths = create_download_paths(DOWNLOAD_BASE, FILE_TYPES)
    upload_paths = create_upload_paths(GEE_UPLOAD_BASE, FILE_TYPES)

    # Authenticate based on action
    earthaccess_auth, gee_auth = authenticate_services(ACTION)
    
    if not earthaccess_auth and not gee_auth:
        print("\nAuthentication failed. Exiting.")
        return

    # Initialize variables
    downloaded_files_by_type = {}

    # Execute download workflow
    if ACTION in ["download", "both"] and earthaccess_auth:
        print("\n--- Starting Download Workflow ---")
        downloaded_files = download_workflow(download_paths)
        downloaded_files_by_type = organize_files_by_type(downloaded_files)

    # Execute upload workflow
    if ACTION in ["upload", "both"] and gee_auth:
        print("\n--- Starting Upload Workflow ---")
        upload_workflow(download_paths, upload_paths, downloaded_files_by_type)
    elif ACTION in ["upload", "both"] and not gee_auth:
        print("\n--- Skipping Upload Workflow (GEE authentication failed) ---")

    logging.info("Script execution completed")
    print("\n" + "=" * 60)
    print("Script execution completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
