"""
Metadata extraction and processing utilities
"""
import re
from datetime import datetime


def extract_granule_metadata(granule):
    """
    Extract comprehensive metadata from a granule object
    
    Args:
        granule: ECOSTRESS granule object from earthaccess
        
    Returns:
        dict: Extracted metadata
    """
    metadata = {}

    # Extract basic metadata
    meta = granule.get("meta", {})
    umm = granule.get("umm", {})

    # Add basic identifiers
    metadata['concept_type'] = meta.get("concept-type", "")
    metadata['concept_id'] = meta.get("concept-id", "")
    metadata['revision_id'] = meta.get("revision-id", "")
    metadata['native_id'] = meta.get("native-id", "")
    metadata['collection_concept_id'] = meta.get("collection-concept-id", "")
    metadata['provider_id'] = meta.get("provider-id", "")
    metadata['format'] = meta.get("format", "")
    metadata['revision_date'] = meta.get("revision-date", "")
    granule_ur = umm.get("GranuleUR", "")
    metadata['granule_ur'] = granule_ur

    # Initialize filename-derived fields
    metadata['processing_ID'] = ""
    metadata['mgrs_tile'] = ""
    metadata['orbit_number_from_filename'] = ""
    metadata['version_from_filename'] = ""
    metadata['processing_level'] = ""

    # Extract metadata from filename directly
    if granule_ur:
        metadata.update(_extract_filename_metadata(granule_ur))

    # Add collection reference information
    collection_ref = umm.get("CollectionReference", {})
    metadata['short_name'] = collection_ref.get("ShortName", "")
    metadata['version'] = collection_ref.get("Version", "")

    # Add PGE version information
    pge_version = umm.get("PGEVersionClass", {})
    metadata['pge_version'] = pge_version.get("PGEVersion", "")

    # Add temporal information
    temporal_extent = umm.get("TemporalExtent", {}).get("RangeDateTime", {})
    beginning_datetime = temporal_extent.get("BeginningDateTime", "")
    metadata['beginning_date_time'] = beginning_datetime
    metadata['ending_date_time'] = temporal_extent.get("EndingDateTime", "")

    # Add time_start for Google Earth Engine (in milliseconds)
    if beginning_datetime:
        metadata['time_start'] = _convert_to_timestamp(beginning_datetime)

    # Add spatial information
    metadata.update(_extract_spatial_metadata(umm))

    # Add provider dates
    metadata.update(_extract_provider_dates(umm))

    # Add data quality information
    data_granule = umm.get("DataGranule", {})
    metadata['day_night_flag'] = data_granule.get("DayNightFlag", "")
    metadata['production_date_time'] = data_granule.get("ProductionDateTime", "")

    # Add platform and instrument information
    metadata.update(_extract_platform_metadata(umm))

    # Add size information
    metadata['size_mb'] = granule.size()

    # Add orbit information
    metadata.update(_extract_orbit_metadata(umm))

    # Add measured parameters
    metadata['parameter_names'] = _extract_parameter_names(umm)

    # Add additional attributes
    metadata.update(_extract_additional_attributes(umm))

    return metadata


def _extract_filename_metadata(granule_ur):
    """Extract metadata from filename"""
    metadata = {}
    
    # Extract processing ID suffix (0712_01)
    suffix_match = re.search(r'T\d{6}_(\d{4}_\d{2})$', granule_ur)
    if suffix_match:
        metadata['processing_ID'] = suffix_match.group(1)

    # Extract MGRS tile (e.g., 19FGE)
    mgrs_match = re.search(r'_(\d{2}[A-Z]{3})_', granule_ur)
    if mgrs_match:
        metadata['mgrs_tile'] = mgrs_match.group(1)

    # Extract orbit number (e.g., 00048)
    orbit_match = re.search(r'_LSTE_(\d+)_', granule_ur)
    if orbit_match:
        metadata['orbit_number_from_filename'] = orbit_match.group(1)

    # Extract version (e.g., 002)
    version_match = re.search(r'ECOv(\d+)_', granule_ur)
    if version_match:
        metadata['version_from_filename'] = version_match.group(1)

    # Extract processing level (e.g., L2T)
    level_match = re.search(r'ECOv\d+_(L\d[A-Z]?)_', granule_ur)
    if level_match:
        metadata['processing_level'] = level_match.group(1)

    # Extract scene number (e.g., 003 → 3)
    scene_match = re.search(r'_LSTE_\d+_(\d{3})_', granule_ur)
    if scene_match:
        metadata['scene'] = int(scene_match.group(1))

    # Extract orbit_scene (e.g., 00048_003)
    orbit_scene_match = re.search(r'_LSTE_(\d+_\d{3})_', granule_ur)
    if orbit_scene_match:
        metadata['orbit_scene'] = orbit_scene_match.group(1)
    
    return metadata


def _convert_to_timestamp(datetime_str):
    """Convert ISO datetime string to timestamp in milliseconds"""
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return int(dt.timestamp() * 1000)
    except Exception as e:
        print(f"Error converting beginning_date_time to timestamp: {str(e)}")
        return ""


def _extract_spatial_metadata(umm):
    """Extract spatial extent metadata"""
    spatial_extent = umm.get("SpatialExtent", {}).get("HorizontalSpatialDomain", {}).get("Geometry", {})
    bounding_rect = spatial_extent.get("BoundingRectangles", [{}])[0] if "BoundingRectangles" in spatial_extent else {}

    return {
        'north_lat': bounding_rect.get("NorthBoundingCoordinate", ""),
        'south_lat': bounding_rect.get("SouthBoundingCoordinate", ""),
        'east_lon': bounding_rect.get("EastBoundingCoordinate", ""),
        'west_lon': bounding_rect.get("WestBoundingCoordinate", "")
    }


def _extract_provider_dates(umm):
    """Extract provider date information"""
    metadata = {}
    provider_dates = umm.get("ProviderDates", [])
    for pdate in provider_dates:
        date_type = pdate.get("Type", "")
        if date_type:
            metadata[f'provider_date_{date_type.lower()}'] = pdate.get("Date", "")
    return metadata


def _extract_platform_metadata(umm):
    """Extract platform and instrument information"""
    metadata = {'platform_short_name': '', 'sensor': ''}
    
    platforms = umm.get("Platforms", [])
    if platforms:
        metadata['platform_short_name'] = platforms[0].get("ShortName", "ISS")
        instruments = platforms[0].get("Instruments", [])
        if instruments:
            metadata['sensor'] = instruments[0].get("ShortName", "ECOSTRESS")
    
    return metadata


def _extract_orbit_metadata(umm):
    """Extract orbit information"""
    metadata = {
        'orbit_number': '',
        'begin_orbit_number': '',
        'end_orbit_number': ''
    }

    # Check OrbitCalculatedSpatialDomains
    if "OrbitCalculatedSpatialDomains" in umm:
        orbits = umm.get("OrbitCalculatedSpatialDomains", [])
        if orbits and isinstance(orbits, list) and len(orbits) > 0:
            if "BeginOrbitNumber" in orbits[0]:
                metadata['begin_orbit_number'] = orbits[0].get("BeginOrbitNumber", "")
                metadata['end_orbit_number'] = orbits[0].get("EndOrbitNumber", "")
                metadata['orbit_number'] = orbits[0].get("BeginOrbitNumber", "")

    # Check OrbitParameters
    if "OrbitParameters" in umm and not metadata['orbit_number']:
        orbits = umm.get("OrbitParameters", [])
        if orbits and isinstance(orbits, list) and len(orbits) > 0:
            if "OrbitNumber" in orbits[0]:
                metadata['orbit_number'] = orbits[0].get("OrbitNumber", "")

    return metadata


def _extract_parameter_names(umm):
    """Extract measured parameter names"""
    measured_params = umm.get("MeasuredParameters", [])
    if measured_params:
        param_names = [param["ParameterName"] for param in measured_params if "ParameterName" in param]
        return ", ".join(param_names)
    return ""


def _extract_additional_attributes(umm):
    """Extract additional attributes"""
    metadata = {}
    add_attrs = umm.get("AdditionalAttributes", [])
    for attr in add_attrs:
        attr_name = attr.get("Name", "")
        if attr_name and "Values" in attr and attr["Values"]:
            safe_name = attr_name.lower().replace("-", "_")
            metadata[f'attr_{safe_name}'] = ", ".join(attr["Values"])
    return metadata


def get_epsg_from_mgrs(mgrs_tile):
    """
    Extract EPSG code from MGRS tile string
    
    Args:
        mgrs_tile: MGRS tile string (e.g., "18TUN")
        
    Returns:
        str: EPSG code (e.g., "EPSG32618")
    """
    if not mgrs_tile or len(mgrs_tile) < 3:
        return ""

    utm_zone = mgrs_tile[:2]
    hemisphere = 'north' if mgrs_tile[2] in 'NPQRSTUVWX' else 'south'
    epsg_code = f"EPSG326{utm_zone}" if hemisphere == 'north' else f"EPSG327{utm_zone}"
    return epsg_code
