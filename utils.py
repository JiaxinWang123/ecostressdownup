"""
Utility functions for path management and configuration
"""
import os


def create_download_paths(base_path, file_types):
    """
    Create download path dictionary from base path and file types
    
    Args:
        base_path: Base directory for downloads
        file_types: List of file type suffixes
        
    Returns:
        dict: Mapping of file types to download paths
    """
    download_paths = {}
    for file_type in file_types:
        type_name = file_type.split('.')[0]
        download_paths[file_type] = os.path.join(base_path, type_name)
    return download_paths


def create_upload_paths(base_path, file_types):
    """
    Create upload path dictionary for GEE
    
    Args:
        base_path: Base GEE path for uploads
        file_types: List of file type suffixes
        
    Returns:
        dict: Mapping of type names to GEE upload paths
    """
    upload_paths = {}
    for file_type in file_types:
        type_name = file_type.split('.')[0]
        upload_paths[type_name] = f"{base_path}/ecostress_{type_name.lower()}"
    return upload_paths


def organize_files_by_type(downloaded_files):
    """
    Organize downloaded files by type
    
    Args:
        downloaded_files: List of (filename, folder_path, file_type, metadata) tuples
        
    Returns:
        dict: Files organized by type
    """
    files_by_type = {}
    for filename, folder_path, file_type, granule_metadata in downloaded_files:
        if file_type not in files_by_type:
            files_by_type[file_type] = []
        files_by_type[file_type].append((filename, folder_path, file_type, granule_metadata))
    return files_by_type
