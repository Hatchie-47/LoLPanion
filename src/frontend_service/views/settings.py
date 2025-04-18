import customtkinter as ctk
import logging
import utils


class SettingsView(utils.Observable, ctk.CTkFrame):
    """
    The Frame showing varios app settings.
    """

    def __init__(self, *args, **kwargs):
        """
        Inits SettingsView.
        """
        super().__init__(*args, height=1176, width=2002, **kwargs)

        self.user_var = ctk.StringVar()
        self.riot_api_key_var = ctk.StringVar()
        self.ddragon_version_var = ctk.StringVar()

        self.columnconfigure(0, weight=1, uniform='lol')
        self.columnconfigure(1, weight=1, uniform='lol')
        self.columnconfigure(2, weight=1, uniform='lol')
        self.columnconfigure(3, weight=1, uniform='lol')

        self.riot_api_key_label = ctk.CTkLabel(self,
                                               text=f'RIOT API key:',
                                               text_color='white',
                                               font=('Tahoma', 16))
        self.riot_api_key_label.grid(row=0, column=0, sticky='E', pady=(50, 10), padx=(10, 10))

        self.riot_api_key_entry = ctk.CTkEntry(self,
                                               textvariable=self.riot_api_key_var,
                                               state='disabled')
        self.riot_api_key_entry.grid(row=0, column=1, columnspan=2, sticky='NSEW', pady=(50, 10), padx=(10, 10))

        self.riot_api_key_button = ctk.CTkButton(self,
                                                 text='CHANGE',
                                                 border_width=0,
                                                 width=200,
                                                 font=('Tahoma', 16))
        self.riot_api_key_button.grid(row=0, column=3, sticky='W', pady=(50, 10), padx=(10, 10))

        self.user_label = ctk.CTkLabel(self,
                                       text=f'Current summoner:',
                                       text_color='white',
                                       font=('Tahoma', 16))
        self.user_label.grid(row=1, column=0, sticky='E', pady=(10, 10), padx=(10, 10))

        self.user_entry = ctk.CTkEntry(self,
                                       textvariable=self.user_var,
                                       state='disabled')
        self.user_entry.grid(row=1, column=1, columnspan=2, sticky='NSEW', pady=(10, 10), padx=(10, 10))

        self.user_button = ctk.CTkButton(self,
                                         text='CHANGE',
                                         border_width=0,
                                         width=200,
                                         font=('Tahoma', 16))
        self.user_button.grid(row=1, column=3, sticky='W', pady=(10, 10), padx=(10, 10))

        self.ddragon_version_label = ctk.CTkLabel(self,
                                                  text=f'Assets version:',
                                                  text_color='white',
                                                  font=('Tahoma', 16))
        self.ddragon_version_label.grid(row=2, column=0, sticky='E', pady=(50, 5), padx=(10, 10))

        self.ddragon_version_entry = ctk.CTkEntry(self,
                                                  textvariable=self.ddragon_version_var,
                                                  state='disabled')
        self.ddragon_version_entry.grid(row=2, column=1, columnspan=2, sticky='NSEW', pady=(50, 5), padx=(10, 10))

        self.repair_data_button = ctk.CTkButton(self,
                                                text='REPAIR DATA',
                                                width=200,
                                                font=('Tahoma', 16))
        self.repair_data_button.grid(row=2, column=3, sticky='W', pady=(50, 5), padx=(10, 10))

        self.progress_label = ctk.CTkLabel(self,
                                           text=f'',
                                           height=20)
        self.progress_label.grid(row=3, column=1, pady=(5, 5), padx=(10, 10), sticky='WS')

        self.progress = ctk.CTkProgressBar(self)
        self.progress.grid(row=4, column=1, columnspan=2, pady=(5, 5), padx=(10, 10), sticky='EW')

        self.orig_progress = self.progress.cget('progress_color')
        self.orig_label = self.progress_label.cget('text_color')

        self.user_var.trace_add('write',
                                lambda *_,
                                       label=self.user_label: label.configure(
                                    text_color='red' if self.user_var.get() == '' else self.orig_label))
        self.riot_api_key_var.trace_add('write',
                                lambda *_,
                                       label=self.riot_api_key_label: label.configure(
                                    text_color='red' if self.riot_api_key_var.get() == '' else self.orig_label))
        self.ddragon_version_var.trace_add('write',
                                lambda *_,
                                       label=self.ddragon_version_label: label.configure(
                                    text_color='red' if self.ddragon_version_var.get() == '' else self.orig_label))

        self.progress.grid_forget()
        self.progress_label.grid_forget()

    def update_progress(self, progress: float, label: str, color: str = None) -> None:
        """
        Updates loading tracking elements.
        :param progress: Float between 0 and 1 showing percentage of progress to be shown on progressbar.
        :param label: Text to be displayed as a progress message.
        :param color: Color of the progress bar.
        """
        if not self.progress_label.winfo_ismapped():
            self.progress_label.grid(row=3, column=1, pady=(5, 5), padx=(10, 10), sticky='WS')

        if not self.progress.winfo_ismapped():
            self.progress.grid(row=4, column=1, columnspan=2, pady=(5, 5), padx=(10, 10), sticky='EW')

        if progress:
            self.progress.set(progress)

        self.progress_label.configure(text=label)
        if color:
            self.progress.configure(progress_color=color)
            self.progress_label.configure(text_color=color)
        else:
            self.progress.configure(progress_color=self.orig_progress)
            self.progress_label.configure(text_color=self.orig_label)

        self.update_idletasks()

    def hide_progress(self) -> None:
        """
        Hide all the progress tracking elements.
        """
        self.progress.grid_forget()
        self.progress_label.grid_forget()
