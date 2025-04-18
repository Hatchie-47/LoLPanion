import customtkinter as ctk
from tkinter import messagebox
import common.data_models as data_models
import utils
import logging
from typing import Callable


@utils.logged_func
def enable_button(*args, button: ctk.CTkButton, **kwargs) -> None:
    """
    For variable number of entry arguments, enables button if all entries are not empty strings. Otherwise disables it.
    :param args: Variable number of entries.
    :param button: Button to be enabled or disabled based on entries.
    """
    filled = True
    for entry in args:
        if entry.get() == '':
            filled = False

    if filled:
        button.configure(state='enabled')
    else:
        button.configure(state='disabled')


class TagFrame(ctk.CTkFrame):
    """
    Frame showing all the information about a tag.
    """

    def __init__(self, container: ctk.CTkFrame, tag: data_models.AssignedTag, *args, **kwargs):
        """
        Inits TagFrame.
        :param container: Parent container.
        :param tag: Tag to be displayed.
        """
        self.INNER_COLOR = {
            tag.severity.LOW: 'salmon',
            tag.severity.MEDIUM: 'indian red',
            tag.severity.HIGH: 'red3'
        }

        self.OUTER_COLOR = {
            tag.tag.INTER: 'firebrick4',
            tag.tag.TILTER: 'purple4',
            tag.tag.FLAMER: 'orange red',
            tag.tag.UNDERPERFORMER: 'DodgerBlue4',
            tag.tag.OVERPERFORMER: 'dark green',
            tag.tag.ONETRICK: 'goldenrod1'
        }

        super().__init__(container, height=130, width=418, fg_color=self.OUTER_COLOR[tag.tag], *args, **kwargs)

        self.grid_propagate(False)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        self.datetimelabel = ctk.CTkLabel(self,
                                          text=f'{tag.added.strftime("%d.%m.%Y")}\n'
                                               f'{tag.added.strftime("%H:%M:%S")}',
                                          text_color='white',
                                          fg_color=self.INNER_COLOR[tag.severity],
                                          width=114,
                                          height=41)
        self.datetimelabel.grid(row=0, column=0, pady=(2, 2), padx=(2, 2), sticky='NSEW')

        self.taglabel = ctk.CTkLabel(self,
                                     text=f'{tag.tag}',
                                     text_color='white',
                                     fg_color=self.INNER_COLOR[tag.severity],
                                     width=114,
                                     height=41)
        self.taglabel.grid(row=1, column=0, pady=(2, 2), padx=(2, 2), sticky='NSEW')

        self.severitylabel = ctk.CTkLabel(self,
                                          text=f'{tag.severity}',
                                          text_color='white',
                                          fg_color=self.INNER_COLOR[tag.severity],
                                          width=114,
                                          height=41)
        self.severitylabel.grid(row=2, column=0, pady=(2, 2), padx=(2, 2), sticky='NSEW')

        self.note_text = ctk.CTkTextbox(self,
                                        text_color='white',
                                        wrap='word',
                                        fg_color=self.INNER_COLOR[tag.severity],
                                        width=280,
                                        height=128)
        self.note_text.grid(row=0, column=1, rowspan=3, pady=(2, 2), padx=(2, 2), sticky='NSEW')
        self.note_text.grid_propagate(False)
        self.note_text.insert(index="0.0", text=f'{tag.note}')
        self.note_text.configure(state='disabled')


class AlertFrame(ctk.CTkFrame):
    """
    Frame showing all the information about an alert.
    """

    def __init__(self, container: ctk.CTkFrame, alert: data_models.Alert, *args, **kwargs):
        """
        Inits AlertFrame.
        :param container: Parent container.
        :param alert: Alert to be displayed.
        """
        super().__init__(container, height=130, width=418, fg_color=alert.color, *args, **kwargs)

        self.grid_propagate(False)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.columnconfigure(0, weight=1)

        self.alertlabel = ctk.CTkLabel(self,
                                       text=f'{alert.name}',
                                       text_color='white',
                                       fg_color=alert.color,
                                       width=114,
                                       height=41)
        self.alertlabel.grid(row=0, column=0, pady=(2, 2), padx=(2, 2), sticky='NSEW')

        self.note_text = ctk.CTkTextbox(self,
                                        text_color='white',
                                        wrap='word',
                                        fg_color=alert.color,
                                        width=260,
                                        height=128)
        self.note_text.grid(row=1, column=0, rowspan=2, pady=(2, 2), padx=(2, 2), sticky='NSEW')
        self.note_text.grid_propagate(False)
        self.note_text.insert(index="0.0", text=f'{alert.detail}')
        self.note_text.configure(state='disabled')


class ItemsFrame(ctk.CTkFrame):
    """
    Frame showing all items built in game by a participant.
    """

    def __init__(self, container: ctk.CTkFrame, items: list, *args, **kwargs):
        """
        Inits ItemsFrame.
        :param container: Parent container.
        :param items: List of items built.
        """
        super().__init__(container, height=128, width=256, *args, **kwargs)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        self.lazyitems = utils.LazyItems('')

        for i, item in enumerate(items[:3]):
            itemframe = ctk.CTkLabel(self,
                                     image=self.lazyitems.get_image(str(item)),
                                     text='')
            itemframe.grid(row=0, column=i, pady=(1, 1), padx=(1, 1))

        for i, item in enumerate(items[3:6]):
            itemframe = ctk.CTkLabel(self,
                                     image=self.lazyitems.get_image(str(item)),
                                     text='')
            itemframe.grid(row=1, column=i, pady=(1, 1), padx=(1, 1))

        itemframe = ctk.CTkLabel(self,
                                 image=self.lazyitems.get_image(str(items[6])),
                                 text='')
        itemframe.grid(row=0, column=4, rowspan=2, pady=(1, 1), padx=(1, 1))


class ParticipantStatsFrame(ctk.CTkFrame):
    """
    Frame showing all information about a participant.
    """

    def __init__(self, container: ctk.CTkScrollableFrame, participant: data_models.Participant, *args, **kwargs):
        """
        Inits ParticipantStatsFrame.
        :param container: Parent container.
        :param participant: The participant.
        """
        super().__init__(container, height=131, width=418, *args, **kwargs)

        self.rowconfigure(0, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.items = ItemsFrame(self,
                                [participant.stats.item0, participant.stats.item1, participant.stats.item2,
                                 participant.stats.item3, participant.stats.item4, participant.stats.item5,
                                 participant.stats.item6],
                                border_color='goldenrod',
                                border_width=1)
        self.items.grid(row=0, column=0, pady=(0, 0), padx=(0, 0))

        self.additional_frame = ctk.CTkFrame(self,
                                             height=64,
                                             width=155,
                                             border_color='goldenrod',
                                             border_width=1)
        self.additional_frame.grid(row=0, column=1, pady=(0, 0), padx=(0, 0), sticky='nswe')
        self.additional_frame.grid_propagate(False)

        self.additional_frame.rowconfigure(0, weight=1)
        self.additional_frame.rowconfigure(1, weight=1)
        self.additional_frame.rowconfigure(2, weight=1)
        self.additional_frame.rowconfigure(3, weight=1)
        self.additional_frame.rowconfigure(4, weight=1)
        self.additional_frame.columnconfigure(0, weight=1)

        self.goldlabel = ctk.CTkLabel(self.additional_frame,
                                      text=f'{participant.stats.total_gold} GOLD',
                                      text_color='yellow')
        self.goldlabel.grid(row=2, column=0, pady=(1, 1), padx=(1, 1), sticky='nswe')

        self.cslabel = ctk.CTkLabel(self.additional_frame,
                                    text=f'{participant.stats.cs} CS',
                                    text_color='yellow')
        self.cslabel.grid(row=3, column=0, pady=(1, 1), padx=(1, 1), sticky='nswe')

        self.kdalabel = ctk.CTkLabel(self.additional_frame,
                                     text=f'{participant.stats.kills}/'
                                          f'{participant.stats.deaths}/'
                                          f'{participant.stats.assists} KDA',
                                     text_color='yellow')
        self.kdalabel.grid(row=1, column=0, pady=(1, 1), padx=(1, 1), sticky='nswe')


class ChangeUserWindow(ctk.CTkToplevel):
    """
    Window to change user setting.
    """

    def __init__(self, container: ctk.CTkFrame, button_callback: Callable, *args, **kwargs):
        """
        Inits ChangeUserWindow.
        :param container: Parent container.
        :param button_callback: Callable to called upon clicking the send button.
        """
        super().__init__(container, *args, **kwargs)

        self.geometry('420x100+1001+602')
        self.title(f'Change user')
        self.resizable(False, False)
        self.attributes('-topmost', 1)
        self.button_callback = button_callback

        self.rowconfigure(0)
        self.rowconfigure(1)
        self.rowconfigure(2)
        self.columnconfigure(0)
        self.columnconfigure(1, weight=2)

        self.name_label = ctk.CTkLabel(self,
                                       text='Name:',
                                       text_color='white',
                                       width=140,
                                       font=('Tahoma', 16))
        self.name_label.grid(row=0, column=0, sticky='NSEW', padx=2, pady=2)

        self.name_var = ctk.StringVar(self)
        self.name_entry = ctk.CTkEntry(self,
                                       textvariable=self.name_var,
                                       width=280)
        self.name_entry.grid(row=0, column=1, sticky='NSEW', padx=2, pady=2)

        self.tagline_label = ctk.CTkLabel(self,
                                          text='Tagline:',
                                          text_color='white',
                                          width=140,
                                          font=('Tahoma', 16))
        self.tagline_label.grid(row=1, column=0, sticky='NSEW', padx=2, pady=2)

        self.tagline_var = ctk.StringVar(self)
        self.tagline_entry = ctk.CTkEntry(self,
                                          textvariable=self.tagline_var,
                                          width=280)
        self.tagline_entry.grid(row=1, column=1, sticky='NSEW', padx=2, pady=2)

        self.send_button = ctk.CTkButton(self,
                                         text='CHANGE USER',
                                         border_width=0,
                                         state='disabled',
                                         font=('Tahoma', 16))
        self.send_button.configure(command=self._change_user)
        self.send_button.grid(row=2, column=0, columnspan=2, sticky='NSEW', padx=105, pady=2)

        self.name_var.trace('w', lambda *_,
                                        button=self.send_button,
                                        entry1=self.name_var,
                                        entry2=self.tagline_var: enable_button(entry1, entry2, button=button))
        self.tagline_var.trace('w', lambda *_,
                                           button=self.send_button,
                                           entry1=self.name_var,
                                           entry2=self.tagline_var: enable_button(entry1, entry2, button=button))

    @utils.logged_func
    def _change_user(self, *args, **kwargs) -> None:
        """
        Function called once the send button is clicked.
        """
        result = self.button_callback(name=self.name_entry.get(), tagline=self.tagline_entry.get())

        if result == 0:
            self.destroy()
        elif result == 1:
            messagebox.showerror(f'User not found!',
                                 f'User {self.name_entry.get()}#{self.tagline_entry.get()} does not exist!')
        elif result == 2:
            messagebox.showerror('RIOT Error', 'RIOT API could not be reached!')
            self.destroy()
        else:
            messagebox.showerror('Data service Error', 'User wasn\'t changed!')
            self.destroy()


class ChangeRiotApiKeyWindow(ctk.CTkToplevel):
    """
    Window to change RIOT API key.
    """

    def __init__(self, container: ctk.CTkFrame, button_callback: Callable, *args, **kwargs):
        """
        Inits ChangeRiotApiKeyWindow.
        :param container: Parent container.
        :param button_callback: Callable to called upon clicking the send button.
        """
        super().__init__(container, *args, **kwargs)

        self.geometry('420x70+1001+602')
        self.title(f'Change RIOT API key')
        self.resizable(False, False)
        self.attributes('-topmost', 1)
        self.button_callback = button_callback

        self.rowconfigure(0)
        self.rowconfigure(1)
        self.columnconfigure(0)
        self.columnconfigure(1, weight=2)

        self.riot_api_key_label = ctk.CTkLabel(self,
                                               text='RIOT API key:',
                                               text_color='white',
                                               width=140,
                                               font=('Tahoma', 16))
        self.riot_api_key_label.grid(row=0, column=0, sticky='NSEW', padx=2, pady=2)

        self.riot_api_key_var = ctk.StringVar(self)
        self.riot_api_key_entry = ctk.CTkEntry(self,
                                               textvariable=self.riot_api_key_var,
                                               width=280)
        self.riot_api_key_entry.grid(row=0, column=1, sticky='NSEW', padx=2, pady=2)

        self.send_button = ctk.CTkButton(self,
                                         text='CHANGE RIOT API KEY',
                                         border_width=0,
                                         state='disabled',
                                         font=('Tahoma', 16))
        self.send_button.configure(command=self._change_riot_api_key)
        self.send_button.grid(row=2, column=0, columnspan=2, sticky='NSEW', padx=105, pady=2)

        self.riot_api_key_var.trace('w', lambda *_,
                                                entry1=self.riot_api_key_var,
                                                button=self.send_button: enable_button(entry1, button=button))

    @utils.logged_func
    def _change_riot_api_key(self, *args, **kwargs) -> None:
        """
        Function called once the send button is clicked.
        """
        result = self.button_callback(riot_api_key=self.riot_api_key_entry.get())

        if result == 0:
            self.destroy()
        elif result == 1:
            messagebox.showerror('Incorrect API key!', 'The key you provided is not correct!')
        elif result == 2:
            if messagebox.askokcancel('RIOT Error', 'RIOT API could not be reached! Are you sure the key is correct?'):
                self.destroy()
        else:
            messagebox.showerror('Data service Error', 'RIOT API key wasn\'t changed!')
            self.destroy()
