import common.lol_logging
import api
import db_upgrader
import logging

"""
The main file run by the container on startup.
"""

if __name__ == '__main__':
    try:
        db_upgrader.run_scripts()
        api.main()
    except Exception as e:
        logging.critical(e, exc_info=True)
