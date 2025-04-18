import customtkinter as ctk
from .main_menu import MainMenuView

class RootView(ctk.CTk):
    """
    The root view, main window fo the application.
    """

    def __init__(self, *args, **kwargs):
        """
        Inits RootView.
        """
        super().__init__(*args, **kwargs)

        self.title('LoLpanion')
        # self.state('zoomed')
        self.geometry('2002x1204')
        self.resizable(False, False)

        self.withdraw()

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=42)

        self.columnconfigure(0, weight=1)

        self.main_menu = MainMenuView(self)
        self.main_menu.grid(column=0, row=0, sticky='NSEW')
