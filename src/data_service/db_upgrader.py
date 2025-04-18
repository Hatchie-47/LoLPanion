import os
import logging
import psycopg
import common.db as db

base_folder = '/database'

def run_scripts() -> None:
    """
    This function runs all sql scripts in database folder, keeping all database objects up to date.
    """
    logging.info(f'Starting DB upgrader...')

    for folder in sorted(os.listdir(base_folder)):
        for filename in sorted(os.listdir(os.path.join(base_folder, folder))):
            try:
                with db.get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute(open(os.path.join(base_folder, folder, filename), 'r').read())
                        logging.info(f'Running {filename}')
            except psycopg.Error as e:
                logging.error(e, exc_info=True)

    logging.info(f'DB upgrader finished.')
