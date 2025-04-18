import customtkinter as ctk
import utils


class MainMenuView(utils.Observable, ctk.CTkFrame):
    """
    The main menu bar on top of view.
    """

    def __init__(self, *args, **kwargs):
        """
        Inits MainMenuView.
        """
        super().__init__(height=28, width=2002, *args, **kwargs)

        self.active_match_button = ctk.CTkButton(self,
                                                 text='Active match',
                                                 border_width=0,
                                                 font=('Tahoma', 16))
        self.active_match_button.configure(command=lambda: self.trigger_event('frame_picked', frame='active_match'))
        self.active_match_button.grid(row=0, column=0, sticky='NSEW', padx=(10, 10))

        self.settings_button = ctk.CTkButton(self,
                                             text='Settings',
                                             border_width=0,
                                             font=('Tahoma', 16))
        self.settings_button.configure(command=lambda: self.trigger_event('frame_picked', frame='settings'))
        self.settings_button.grid(row=0, column=1, sticky='NSEW', padx=(10, 10))

    @utils.logged_func
    def can_leave_settings(self, can: bool) -> None:
        """
        Toggles whether all settings are set up correctly so this menu can be used.
        :param can: True means menu can be used, False it can't.
        """
        if can:
            self.active_match_button.configure(state='normal')
        else:
            self.active_match_button.configure(state='disabled')
            self.trigger_event('frame_picked', frame='settings')
