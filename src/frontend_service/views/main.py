from .root import RootView
from .loading import LoadingView
from .active_match import ActiveMatchView
from .settings import SettingsView
import customtkinter as ctk
import utils
import logging


class View (utils.Observable):
    """
    Main view object.
    """

    def __init__(self):
        """
        Inits View.
        """
        super().__init__()

        self.root = RootView()
        self.frames = {}

        self.loading = LoadingView(parent_view=self.root)
        self._add_frame(ActiveMatchView, 'active_match')
        self._add_frame(SettingsView, 'settings')

        self.version = None

        self.lazyitems = None
        self.lazyrunes = None
        self.lazychampions = None
        self.lazysummoners = None

    @utils.logged_func
    def _add_frame(self, frame: ctk.CTkFrame, name: str):
        """
        Adds a new frame to main view.
        :param frame: The frame to be added
        :param name: Name of the frame.
        """
        self.frames[name] = frame(self.root)
        self.frames[name].grid(column=0, row=1, sticky='NSEW')

    @utils.logged_func
    def switch(self, name: str) -> None:
        """
        Switch to a different frame.
        :param name: Name of the frame to be switched to.
        """
        frame = self.frames[name]
        frame.tkraise()

    @utils.logged_func
    def init_lazyreaders(self, *args, **kwargs) -> None:
        """
        Inits lazy readers with current data version.
        """
        logging.debug(f'init_lazyreaders')
        self.lazychampions = utils.LazyChampions(self.version)
        self.lazysummoners = utils.LazySummoners(self.version)
        self.lazyrunes = utils.LazyRunes(self.version)
        self.lazyitems = utils.LazyItems(self.version)
        logging.info(f'Lazyreaders initialized with version {self.version}')

    @utils.logged_func
    def _startup_process(self) -> None:
        """
        Triggers the startup event.
        """
        self.trigger_event('startup_process')

    def start_mainloop(self) -> None:
        """
        Starts mainloop on the root view.
        """
        self.root.after(100, self._startup_process)
        self.root.mainloop()



