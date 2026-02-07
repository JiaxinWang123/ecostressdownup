"""
ECOSTRESS data search and download utilities
"""
import os
import logging
import earthaccess
from metadata import extract_granule_metadata


def search_ecostress_data(short_name, mgrs_tile, start_date, end_date, day_night='DAY'):
    """
    Search for ECOSTRESS data with the given parameters
    
    Args:
        short_name: ECOSTRESS product short name (e.g., 'ECO_L2T_LSTE')
        mgrs_tile: MGRS tile identifier
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        day_night: Day/night flag ('DAY' or 'NIGHT')
        
    Returns:
        list: Search results
    """
    logging.info(f"Searching for {short_name} data from {start_date} to {end_date}, MGRS: {mgrs_tile}")
    print(f"Searching for {short_name} data from {start_date} to {end_date}, MGRS: {mgrs_tile}")

    granule_name = f'*{mgrs_tile}*' if mgrs_tile else '*'

    results = earthaccess.search_data(
        short_name=short_name,
        cloud_hosted=True,
        day_night_flag=day_night,
        granule_name=granule_name,
        temporal=(start_date, end_date),
    )

    logging.info(f"Found {len(results)} results")
    print(f"Found {len(results)} results")
    return results


def download_data(results, file_types, download_paths):
    """
    Download ECOSTRESS data to specified paths based on file types
    
    Args:
        results: Search results from earthaccess
        file_types: List of file type suffixes to download
        download_paths: Dictionary mapping file types to download paths
        
    Returns:
        list: List of tuples (filename, destination_path, file_type, granule_metadata)
    """
    downloaded_files = []
    skipped_count = 0
    download_count = 0
    error_count = 0

    for granule in results:
        granule_metadata = extract_granule_metadata(granule)

        for url in granule.data_links(access="external"):
            filename = url.split('/')[-1]
            file_processed = False

            for suffix in file_types:
                if filename.endswith(suffix):
                    destination_path = download_paths[suffix]
                    target_file_path = os.path.join(destination_path, filename)

                    # Check if file already exists and is valid
                    if os.path.exists(target_file_path):
                        file_size = os.path.getsize(target_file_path)
                        if file_size > 0:  # File exists and is not empty
                            print(f"⏭️  Skipped (already exists): {filename}")
                            logging.info(f"File already exists, skipping: {filename} ({file_size} bytes)")
                            downloaded_files.append((filename, destination_path, suffix.split('.')[0], granule_metadata))
                            skipped_count += 1
                        else:
                            # File exists but is empty or corrupted, re-download
                            print(f"⚠️  Re-downloading (corrupted file): {filename}")
                            logging.warning(f"File corrupted (0 bytes), re-downloading: {filename}")
                            os.remove(target_file_path)
                            _download_file(url, destination_path, filename, suffix, granule_metadata, downloaded_files)
                            download_count += 1
                    else:
                        # File doesn't exist, download it
                        _download_file(url, destination_path, filename, suffix, granule_metadata, downloaded_files)
                        download_count += 1

                    file_processed = True
                    break

            if not file_processed:
                logging.debug(f"Skipping unrelated file: {filename}")

    # Print summary
    print(f"\n📊 Download Summary:")
    print(f"   ✅ New downloads: {download_count}")
    print(f"   ⏭️  Skipped (existing): {skipped_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"   📁 Total files tracked: {len(downloaded_files)}")

    return downloaded_files


def _download_file(url, destination_path, filename, suffix, granule_metadata, downloaded_files):
    """
    Helper function to download a single file
    
    Args:
        url: URL to download from
        destination_path: Local destination directory
        filename: Name of the file
        suffix: File type suffix
        granule_metadata: Metadata for the granule
        downloaded_files: List to append successful downloads to
    """
    print(f"⬇️  Downloading: {filename}")
    logging.info(f"Downloading: {filename} -> {destination_path}")

    os.makedirs(destination_path, exist_ok=True)

    try:
        earthaccess.download(url, destination_path)
        
        # Verify the downloaded file
        target_file_path = os.path.join(destination_path, filename)
        if os.path.exists(target_file_path) and os.path.getsize(target_file_path) > 0:
            downloaded_files.append(
                (filename, destination_path, suffix.split('.')[0], granule_metadata))
            logging.info(f"Successfully downloaded: {filename} ({os.path.getsize(target_file_path)} bytes)")
            print(f"   ✅ Success: {filename}")
        else:
            logging.error(f"Download verification failed: {filename}")
            print(f"   ❌ Verification failed: {filename}")
            
    except Exception as e:
        logging.error(f"Error downloading {filename}: {str(e)}")
        print(f"   ❌ Error: {filename} - {str(e)}")
