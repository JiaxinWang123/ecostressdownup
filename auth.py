"""
Authentication utilities for earthaccess and Google Earth Engine
"""
import logging
import earthaccess
import ee


def authenticate_earthaccess(auth_mode="netrc"):
    """
    Authenticate with earthaccess
    
    Args:
        auth_mode: Authentication mode ("netrc" or "interactive")
        
    Returns:
        bool: True if authentication successful, False otherwise
    """
    logging.info(f"Authenticating with earthaccess using {auth_mode} mode")
    try:
        auth = earthaccess.login(strategy=auth_mode)
        if not auth:
            logging.error("Authentication with earthaccess failed")
            return False

        logging.info("Authentication with earthaccess successful")
        return True
    except Exception as e:
        logging.error(f"Error during authentication: {str(e)}")
        return False


def authenticate_gee(project_name):
    """
    Authenticate with Google Earth Engine
    
    Args:
        project_name: GEE project name
        
    Returns:
        bool: True if authentication successful, False otherwise
    """
    try:
        # First check if already authenticated, if not, prompt user
        try:
            ee.Initialize(project=project_name)
            logging.info("Already authenticated with Google Earth Engine")
            print("Already authenticated with Google Earth Engine")
            return True
        except Exception:
            # Not authenticated yet, run authentication flow
            print("\n" + "="*60)
            print("Google Earth Engine Authentication Required")
            print("="*60)
            print("You need to authenticate with Google Earth Engine.")
            print("This will open a browser window for authorization.")
            print("="*60 + "\n")
            
            ee.Authenticate()
            ee.Initialize(project=project_name)
            logging.info("Successfully authenticated with Google Earth Engine")
            print("\nSuccessfully authenticated with Google Earth Engine")
            return True
            
    except Exception as e:
        logging.error(f"Error authenticating with GEE: {str(e)}")
        print(f"\nError authenticating with GEE: {str(e)}")
        print("\nPlease ensure:")
        print("1. You have access to the GEE project: " + project_name)
        print("2. You've registered for Google Earth Engine at https://earthengine.google.com/")
        print("3. Your project ID in config.py is correct")
        return False
