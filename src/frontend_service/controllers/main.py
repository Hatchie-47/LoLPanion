from .active_match import ActiveMatchController
from .settings import SettingsController
from models.main import Model
from views.main import View
import utils
import logging


class Controller:
    """
    Main controller of the application.
    """

    def __init__(self, model: Model, view: View) -> None:
        """
        Inits main Controller.
        :param model: The main model.
        :param view: The main view.
        """
        self.view = view
        self.model = model

        self.active_match = ActiveMatchController(model, view)
        self.settings = SettingsController(model, view)
        self._bind()

    def _bind(self) -> None:
        """
        Binds all necessary events.
        """
        self.view.add_event_listener('startup_process', self._startup_process)
        self.view.root.main_menu.active_match_button.configure(command=self._switch_activematch)
        self.view.root.main_menu.settings_button.configure(command=self._switch_settings)

    @utils.logged_func
    def _switch_activematch(self, *args, **kwargs) -> None:
        """
        Switches to active match frame.
        """
        self.view.switch('active_match')
        self.view.frames['active_match'].set_run_check(True)

    @utils.logged_func
    def _switch_settings(self, *args, **kwargs) -> None:
        """
        Switches to settings frame.
        """
        self.view.switch('settings')
        self.view.frames['active_match'].set_run_check(False)

    def start(self) -> None:
        """
        Calls the view to start the tkinter mainloop.
        """
        self.view.start_mainloop()

    @utils.logged_func
    def _startup_process(self, *args, **kwargs) -> None:
        """
        Handles the startup of application up to opening the main window.
        """
        logging.info('Controller._startup_process starting.')
        self.settings.init_load()
        ddragon_result = self.settings.loading_process(loading_object=self.view.loading, force_download=False)
        logging.debug(f'Controller._startup_process ddragon result: {ddragon_result}')
        # If ddragon data end up in unusable state end the application, otherwise start it.
        if ddragon_result < 2:
            self.view.root.deiconify()
            self.view.loading.destroy()
        else:
            self.view.root.destroy()

        settings = self.settings.check_settings()
        logging.info(f'Controller._startup_process settings: {settings}')
        if settings:
            self._switch_activematch()
        else:
            self._switch_settings()
