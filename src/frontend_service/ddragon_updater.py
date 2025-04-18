import logging
import requests
import tarfile
import shutil
import os


def unpack_file(version: str) -> None:
    """
    Unpacks .tar file.
    :param version: Version of data to unpack.
    """
    logging.debug(f'Unpacking {version}.tgz')
    with tarfile.open(f'/{version}.tgz') as f:
        f.extractall('/ddragon')


def clear_ddragon_folder() -> None:
    """
    Removes all content from folder hosting ddragon data.
    """
    logging.debug(f'Cleaning ddragon folder.')
    with os.scandir('/ddragon') as entries:
        for entry in entries:
            if entry.is_file():
                os.unlink(entry.path)
            else:
                shutil.rmtree(entry.path)


def download_ddragon_version(version: str) -> bool:
    """
    Downloads ddragon data from RIOT.
    :param version: Version fo the data to download.
    """
    logging.info(f'Starting downloading ddragon version {version} ...')
    r = requests.get(url=f'https://ddragon.leagueoflegends.com/cdn/dragontail-{version}.tgz', allow_redirects=True)

    if r.status_code == 200:
        logging.info(f'Ddragon version {version} downloaded.')
        with open(f'/{version}.tgz', 'wb') as f:
            f.write(r.content)
        return True
    else:
        logging.error(f'Failed to download ddragon version {version}!')
        return False
