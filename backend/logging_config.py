import logging
import sys

def setup_logger():
    logging.basicConfig(
        level=logging.DEBUG,  # Oder INFO
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("router_engine.log", mode='a')  # Optional: Log in Datei
        ]
    )
