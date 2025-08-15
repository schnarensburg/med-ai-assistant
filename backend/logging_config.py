import logging
import sys

def setup_logger():
    """
    Configures a comprehensive logging system for the RouterEngine with:
    - Dual output to console and log file
    - Debug-level verbosity
    - Structured timestamped format
    """
    logging.basicConfig(
        # Set minimum logging level (DEBUG captures everything, INFO for production)
        level=logging.DEBUG,  
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("router_engine.log", mode='a')  # Optional: Log in Datei
        ]
    )

# Note: This basicConfig should only be called once per application
# Subsequent calls won't have effect unless force=True is specified