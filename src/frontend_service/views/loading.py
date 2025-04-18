import customtkinter as ctk
from PIL import Image
import os
import utils


class LoadingView(utils.Observable, ctk.CTkToplevel):
    """
    Loading window before the main root is shown.
    """

    def __init__(self, parent_view, *args, **kwargs):
        """
        Inits LoadingView.
        :param parent_view: The parent view of this view.
        """
        super().__init__(*args, **kwargs)

        self.parent_view = parent_view
        self.title('LoLpanion data download')
        self.geometry('480x400')

        self.rowconfigure(0, weight=18)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(self)
        self.progress.grid(row=2, column=0, padx=(10, 10), sticky='NSEW')

        self.label = ctk.CTkLabel(self,
                                  text=f'',
                                  fg_color='transparent',
                                  anchor='w',
                                  width=114,
                                  height=20)
        self.label.grid(row=1, column=0, padx=(10, 10), sticky='NSEW')

        self.img = ctk.CTkImage(size=(480, 360),
                                light_image=Image.open(
                                    os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                 'assets', 'loading.gif')))

        self.loading = ctk.CTkLabel(self,
                                    image=self.img,
                                    text='')
        self.loading.grid(row=0, column=0, sticky='NSEW')

        self.update_progress(0, 'Waiting to start...')

        self.update_idletasks()

    def update_progress(self, progress: float, label: str) -> None:
        """
        Updates progress elements on the view.
        :param progress:
        :param label:
        """
        self.progress.set(progress)
        self.label.configure(text=label)
        self.update_idletasks()
