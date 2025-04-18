import common.data_models as data_models
import utils
import requests
import logging
from typing import Any


class SettingsModel(utils.Observable):
    """
    Model handling settings.
    """

    def __init__(self) -> None:
        """
        Inits SettingsModel.
        """
        super().__init__()

        self._settings = dict(user=None, riot_api_key=None, ddragon_version=None)

    @utils.logged_func
    def init_load(self, *args, **kwargs) -> None:
        """
        Loads the settings values at start.
        """

        r = requests.get(url='http://data_service:4701/config/summoner')
        if r and r.status_code == 200:
            self._settings['user'] = data_models.Summoner(name=r.json()['name'],
                                                          tagline=r.json()['tagline'],
                                                          server=r.json()['server'])
            logging.debug(f'SettingsModel User loaded: {self._settings["user"].name}#{self._settings["user"].tagline}')

        r2 = requests.get(url='http://data_service:4701/config/riot_api_key')
        if r2 and r2.status_code == 200:
            self._settings['riot_api_key'] = r2.json()['riot_api_key']
            logging.debug(f'SettingsModel RIOT API key loaded: {self._settings["riot_api_key"]}')

        r3 = requests.get(url='http://data_service:4701/config/ddragon_version')
        if r3 and r3.status_code == 200:
            self._settings['ddragon_version'] = r3.json()['ddragon_version']
            logging.debug(f'SettingsModel current ddragon version: {self._settings["ddragon_version"]}')

    @utils.logged_func
    def switch_riot_api_key(self, *args, riot_api_key: str, **kwargs) -> int:
        """
        Handles setting of new API key to be used for communication with RIOT.
        :param riot_api_key: The API key to be set.
        :return: Returns 0 if the API key was successfully changed, 1 if the key was incorrect, 2 if it was changed but
            key might not be correct, 3 if data service failed to change it.
        """
        r = requests.post(url='http://data_service:4701/config/riot_api_key',
                          params={
                              'riot_api_key': riot_api_key
                          })
        if r.status_code == 200:
            logging.info(f'SettingsModel succesfully switched RIOT API key to {riot_api_key}')
            self._settings['riot_api_key'] = riot_api_key
            return 0
        elif r.status_code == 403:
            logging.info('SettingsModel RIOT API key provided is invalid!')
            return 1
        elif r.status_code == 503:
            logging.warning('SettingsModel RIOT API couldn\'t be reached during switching the key.')
            return 2
        else:
            logging.error(f'SettingsModel got unexpected response status from data service: {r.status_code}')
            return 3

    @utils.logged_func
    def switch_user(self, *args, name: str, tagline: str, **kwargs) -> int:
        """
        Handles setting of a different player account to be used as a user.
        :param name: The name of new user.
        :param tagline: The tagline of new user.
        :return: Returns 0 if the user was successfully changed, 1 if user wasn't found, 2 if RIOT API call failed,
            3 if data service failed to change the user.
        """
        r = requests.post(url='http://data_service:4701/config/summoner',
                          params={
                              'name': name,
                              'tagline': tagline
                          })
        if r.status_code == 200:
            logging.info(f'SettingsModel succesfully switched user to {name}#{tagline}')
            self._settings['user'] = data_models.Summoner(name=r.json()['name'],
                                                          tagline=r.json()['tagline'],
                                                          server=r.json()['server'])
            return 0
        elif r.status_code == 404:
            logging.warning(f'SettingsModel provided user "{name}#{tagline}" doesn\'t exist.')
            return 1
        elif r.status_code == 503:
            logging.warning('SettingsModel RIOT API couldn\'t be reached during switching user.')
            return 2
        else:
            logging.error(f'SettingsModel got unexpected response status from data service: {r.status_code}')
            return 3

    @utils.logged_func
    def switch_ddragon_version(self, *args, ddragon_version: str, **kwargs) -> int:
        """
        Handles setting a new value as a version of ddragon data.
        :param ddragon_version: The new ddragon version.
        :return: Returns 0 if the value is successfully changed, 1 if there was an error.
        """
        r = requests.post(url='http://data_service:4701/config/ddragon_version',
                          params={
                              'ddragon_version': ddragon_version if ddragon_version else ''
                          })
        if r.status_code == 200:
            logging.info(f'SettingsModel succesfully switched ddragon version to {ddragon_version}')
            self._settings['ddragon_version'] = ddragon_version
            return 0
        else:
            logging.error(f'SettingsModel got unexpected response status from data service: {r.status_code}')
            return 1

    @utils.logged_func
    def get_setting(self, setting: str) -> Any:
        """
        Gets value of a setting.
        :param setting: Setting to be returned.
        :return: Value of the setting.
        """
        return self._settings[setting]

    @utils.logged_func
    def check_all_settings(self) -> bool:
        """
        Checks if all settings have a value. Setting is considered having a value unless it is None.
        :return: Returns True if all settings have a value, False if any setting is None.
        """
        logging.debug(f'Values of SettingsModel._settings.values() {self._settings.values()}')
        if None in self._settings.values():
            return False
        return True
