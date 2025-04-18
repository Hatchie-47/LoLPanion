from views.main import View
from views.shared import ChangeUserWindow, ChangeRiotApiKeyWindow
from models.main import Model
import ddragon_updater
import requests
import utils
import time
import logging


class SettingsController:
    """
    Controller responsible for all settings changes and ddragon data.
    """

    def __init__(self, model: Model, view: View) -> None:
        """
        Inits SettingsController.
        :param model: The main model.
        :param view: The main view.
        """
        self.model = model
        self.view = view
        self.frame = self.view.frames['settings']
        self._bind()

    @utils.logged_func
    def _bind(self, *args, **kwargs) -> None:
        """
        Binds all necessary events.
        """
        self.frame.user_button.configure(
            command=lambda parent=self.frame,
                           button_callback=self._switch_user: ChangeUserWindow(parent, button_callback))
        self.frame.riot_api_key_button.configure(
            command=lambda parent=self.frame,
                           button_callback=self._set_riot_api_key: ChangeRiotApiKeyWindow(parent, button_callback))
        self.frame.repair_data_button.configure(command=self._repair_data)

    @utils.logged_func
    def _switch_user(self, *args, name: str, tagline: str, **kwargs) -> int:
        """
        Handles setting of a different player account to be used as a user.
        :param name: The name of new user.
        :param tagline: The tagline of new user.
        :return: Returns 0 if the user was successfully changed, 1 if user wasn't found, 2 if RIOT API call failed,
            3 if data service failed to change the user.
        """
        result = self.model.settings.switch_user(name=name, tagline=tagline)
        if result == 0:
            self.frame.user_var.set(f'{name}#{tagline}')
            logging.info(f'SettingsController: User set to {name}#{tagline}.')
        self.check_settings()
        return result

    @utils.logged_func
    def _set_riot_api_key(self, *args, riot_api_key: str, **kwargs) -> bool:
        """
        Handles setting of new API key to be used for communication with RIOT.
        :param riot_api_key: The API key to be set.
        :return: Returns 0 if the API key was successfully changed, 1 if the key was incorrect, 2 if it was changed but
            key might not be correct, 3 if data service failed to change it.
        """
        result = self.model.settings.switch_riot_api_key(riot_api_key=riot_api_key)
        if result == 0 or result == 2:
            self.frame.riot_api_key_var.set(f'{riot_api_key}')
            logging.info(f'SettingsController: RIOT API key set to {riot_api_key}.')
        self.check_settings()
        return result

    @utils.logged_func
    def init_load(self, *args, **kwargs) -> None:
        """
        Makes model load all settings and passes them to view to display.
        """
        self.model.settings.init_load()

        user = self.model.settings.get_setting('user')
        self.frame.user_var.set(f'{user.name}#{user.tagline}' if user else '')
        riot_api_key = self.model.settings.get_setting("riot_api_key")
        self.frame.riot_api_key_var.set(f'{riot_api_key}' if riot_api_key else '')
        ddragon_version = self.model.settings.get_setting("ddragon_version")
        self.frame.ddragon_version_var.set(f'{ddragon_version}' if ddragon_version else '')

    @utils.logged_func
    def _repair_data(self, *args, **kwargs) -> None:
        """
        Handles repairing of ddragon data.
        """
        ddragon_result = self.loading_process(loading_object=self.frame, force_download=True)
        ddragon_version = self.model.settings.get_setting("ddragon_version")
        self.frame.ddragon_version_var.set(f'{ddragon_version}' if ddragon_version else '')
        match ddragon_result:
            case 0:
                self.frame.hide_progress()
            case 1:
                self.frame.update_progress(1,
                                           f'Loading failed. Version {self.frame.ddragon_version_var.get()} kept.',
                                           'orange')
            case 2:
                self.frame.update_progress(1,
                                           'ERROR! Unable to download new data, app not usable right now! '
                                           'Try repairing again!',
                                           'red')
        self.check_settings()

    @utils.logged_func
    def check_settings(self, *args, **kwargs) -> bool:
        """
        Checks if all settings have value and enables/disables leaving the settings frame accordingly.
        :return: True if all settings are set. False if any is missing.
        """
        check = self.model.settings.check_all_settings()
        self.view.root.main_menu.can_leave_settings(check)
        return check

    def loading_process(self, loading_object: utils.TrackingLoadingProgress, force_download: bool) -> int:
        """
        Handles the process of loading data and assets.
        :param loading_object: The parent object that initiated the current download.
        :param force_download: If True new data is downloaded regardless of the current version. Used for data repair.
        :return: Returns 0 if newest version was successfully downloaded, 1 if version wasn't changed but the old one
            is usable, 2 if download failed and the data are in unusable state.
        """
        result = 1
        try:
            logging.info('Start of SettingsController.loading_process')
            logging.debug(loading_object)
            version = None
            if force_download:
                loading_object.update_progress(.1, f'Forcing download...')
                current_version = ''
                utils.LazyChampions.reset()
                utils.LazyRunes.reset()
                utils.LazySummoners.reset()
                utils.LazyItems.reset()
            else:
                loading_object.update_progress(.1, f'Checking ddragon version...')
                current_version = self.model.settings.get_setting('ddragon_version')

            r = requests.get(url='https://ddragon.leagueoflegends.com/api/versions.json')
            if not r:
                current_version = self.model.settings.get_setting('ddragon_version')
                logging.error(f'Failed to acquire newest ddragon version, keeping {current_version}. Some assets might '
                              f'be missing!')
            else:
                version = r.json()[0]

            if version == current_version:
                logging.info(f'Ddragon version up to date: {version}.')
                loading_object.update_progress(.75, f'Ddragon version up to date: {version}.')
                result = 0
            else:
                logging.info(f'Current ddragon version is {current_version}, newest available is {version}')
                loading_object.update_progress(.15, f'Downloading ddragon version {version} ...')
                if ddragon_updater.download_ddragon_version(version):
                    try:
                        loading_object.update_progress(.35, f'Clearing folder...')
                        ddragon_updater.clear_ddragon_folder()
                        loading_object.update_progress(.45, f'Unpacking {version}.tgz ...')
                        ddragon_updater.unpack_file(version)
                        if force_download:
                            raise NotImplementedError
                        result = 0
                    except Exception as e:
                        logging.error(f'Error starting with new ddragon data, please try downloading again!')
                        logging.error(e, exc_info=True)
                        current_version = None
                        self.model.settings.switch_ddragon_version(ddragon_version=current_version)
                        loading_object.update_progress(.99, f'ERROR! Ending download process...')
                        result = 2
                else:
                    logging.warning(f'Keeping ddragon version {current_version}. Some assets might be missing!')
                    loading_object.update_progress(.8, f'Initializing layzreaders...')

            if result < 2:
                loading_object.update_progress(.8, f'Initializing layzreaders...')
                self.view.version = version
                self.view.init_lazyreaders()

                if force_download:
                    loading_object.update_progress(.98, f'Restarting...')
                else:
                    loading_object.update_progress(.98, f'Starting app...')
                self.model.settings.switch_ddragon_version(ddragon_version=version)
                self.frame.ddragon_version_var.set(f'{version}')
                logging.info(f'Successfully started with version {version}')

            time.sleep(2)
            loading_object.update_progress(1, f'All done!')
        except Exception as e:
            logging.error(f'Error during ddragon downloading: {e}', exc_info=True)

        return result
