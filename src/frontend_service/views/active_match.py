from .shared import TagFrame, ParticipantStatsFrame, AlertFrame
import customtkinter as ctk
import common.data_models as data_models
from typing import Callable
from PIL import Image
from CTkToolTip import *
import logging
import utils
import os


class ParticipantAlertsBar(ctk.CTkScrollableFrame):
    """
    The horizontal bar under Participant that shows alerts.
    """

    def __init__(self, container: ctk.CTkFrame, participant: data_models.Participant, *args, **kwargs):
        """
        Inits ParticipantAlertsBar.
        :param container: Parent container.
        :param participant: The participant object.
        """
        super().__init__(container,
                         height=28,
                         width=288,
                         orientation='horizontal',
                         scrollbar_button_color=None if participant.has_history else 'red',
                         *args,
                         **kwargs)

        self._obj_list = []
        alerts = []

        if participant.alerts:
            alerts = sorted(participant.alerts, key=lambda x: x.priority, reverse=False)

        logging.debug(f'Alerts to display for summoner {participant.summoner.name}: {alerts}')

        for i, alert in enumerate(alerts):
            alertlabel = ctk.CTkLabel(self,
                                      text=f'{alert.name}',
                                      text_color='white',
                                      fg_color=alert.color,
                                      font=('Tahoma', 16),
                                      width=40,
                                      height=20)
            alertlabel.grid(row=0, column=i, padx=(5, 5), sticky='NSEW')

            detail_tooltip = CTkToolTip(alertlabel, delay=.5, message=alert.detail)

            self._obj_list.append(alertlabel)


class AddTagWindow(utils.Observable, ctk.CTkToplevel):
    """
    Window for adding new tag to a participant.
    """

    def __init__(self, container: ctk.CTkFrame, participant: data_models.Participant, *args, **kwargs):
        """
        Inits AddTagWindow.
        :param container: Parent container.
        :param participant: The participant object.
        """
        super().__init__(container, *args, **kwargs)

        self.geometry('420x256+1001+602')
        self.title(f'Add tag to {participant.summoner.name}#{participant.summoner.tagline}')
        self.resizable(False, False)
        self.attributes('-topmost', 1)
        self.participant = participant

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.lazychampions = utils.LazyChampions(None)

        self.champ_icon = ctk.CTkLabel(self,
                                       image=self.lazychampions.get_icon_image(str(participant.champion)),
                                       text='')
        self.champ_icon.grid(row=0, sticky='nw', pady=(20, 20), padx=(40, 40))

        self.tag_options = ctk.CTkOptionMenu(self,
                                             values=[val for val in data_models.Tag],
                                             width=160,
                                             fg_color='red' if participant.team_red else 'blue',
                                             button_hover_color='red' if participant.team_red else 'blue',
                                             button_color='dark red' if participant.team_red else 'dark blue')
        self.tag_options.grid(row=0, sticky='nw', pady=(160, 20), padx=(20, 20))

        self.severity_options = ctk.CTkOptionMenu(self,
                                                  values=[val for val in data_models.Severity],
                                                  width=160,
                                                  fg_color='red' if participant.team_red else 'blue',
                                                  button_hover_color='red' if participant.team_red else 'blue',
                                                  button_color='dark red' if participant.team_red else 'dark blue')
        self.severity_options.grid(row=0, sticky='nw', pady=(208, 20), padx=(20, 20))

        self.note_text = ctk.CTkTextbox(self,
                                        width=200,
                                        height=168,
                                        wrap='word')
        self.note_text.grid(row=0, sticky='nw', pady=(20, 20), padx=(200, 20))

        self.add_button = ctk.CTkButton(self,
                                        text='ADD TAG',
                                        border_width=0,
                                        font=('Tahoma', 16),
                                        width=200,
                                        fg_color='red' if participant.team_red else 'blue',
                                        hover_color='dark red' if participant.team_red else 'dark blue')
        self.add_button.configure(command=self.add_tag)
        self.add_button.grid(row=0, sticky='nw', pady=(208, 20), padx=(200, 20))

    @utils.logged_func
    def add_tag(self, *args, **kwargs):
        """
        Calls method add_tag of the parent containter, passes data.
        """
        self.add_button.configure(state='disabled')
        self.master.add_tag(tag=self.tag_options.get(),
                            severity=self.severity_options.get(),
                            note=self.note_text.get(1.0, 'end-1c'))
        self.destroy()


class ChampFrame(utils.Observable, ctk.CTkFrame):
    """
    A frame showing all the information about given participant.
    """

    def __init__(self,
                 container: ctk.CTkFrame,
                 position: str,
                 *args,
                 **kwargs):
        """
        Inits ChampFrame.
        :param container: Parent container.
        :param participant: The participant object.
        """
        super().__init__(container, height=588, width=308, *args, **kwargs)

        self.summ2_frame = None
        self.summ1_frame = None
        self.summ_button = None
        self.rowconfigure(0, weight=20)
        self.rowconfigure(1, weight=1)
        self.lazychampions = None
        self.lazyrunes = None
        self.lazysummoners = None

        self._participant = None
        self._obj_list = []

        self.init_image = ctk.CTkImage(Image.open(os.path.join(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'),
            'assets', f'{position}.png')),
            size=(256, 256))
        self.champ_frame = ctk.CTkLabel(self,
                                        image=self.init_image,
                                        text='')
        self.champ_frame.grid(row=0)

    @utils.logged_func
    def show_new_participant(self, participant: data_models.Participant) -> None:
        """
        Show data for a new participant.
        :param participant: The Participant object.
        """
        self._get_lazyreaders()

        logging.debug(f'Showing new participant {participant.summoner.name}#{participant.summoner.tagline}')
        self._participant = participant

        self.champ_frame = ctk.CTkLabel(self,
                                        image=self.lazychampions.get_image(str(self._participant.champion)),
                                        text='')
        self.champ_frame.grid(row=0)

        self.summ_button = ctk.CTkButton(self.champ_frame,
                                         text=self._participant.summoner.name,
                                         fg_color='red' if self._participant.team_red else 'blue',
                                         hover_color='dark red' if self._participant.team_red else 'dark blue',
                                         border_width=0,
                                         font=('Tahoma', 16))
        self.summ_button.configure(command=lambda: self.select_participant(self._participant))
        self.summ_button.grid(row=0, column=0, sticky='s', pady=(20, 20))

        self.summ1_frame = ctk.CTkLabel(self.champ_frame,
                                        image=self.lazysummoners.get_image(str(self._participant.summ_spell1)),
                                        text='')
        self.summ1_frame.grid(row=0, column=0, sticky='sw', pady=(63, 63), padx=(5, 5))

        self.summ2_frame = ctk.CTkLabel(self.champ_frame,
                                        image=self.lazysummoners.get_image(str(self._participant.summ_spell2)),
                                        text='')
        self.summ2_frame.grid(row=0, column=0, sticky='sw', pady=(63, 63), padx=(75, 75))

        for i, rune in enumerate(self._participant.runes[:4]):
            runeframe = ctk.CTkLabel(self,
                                     image=self.lazyrunes.get_image(str(rune)),
                                     text='')
            runeframe.grid(row=0, column=0, sticky='se', pady=(128, 128), padx=(0, 5 + 40 * i))

        for i, rune in enumerate(self._participant.runes[4:6]):
            runeframe = ctk.CTkLabel(self,
                                     image=self.lazyrunes.get_image(str(rune)),
                                     text='')
            runeframe.grid(row=0, column=0, sticky='se', pady=(88, 88), padx=(0, 45 + 40 * i))

        self.update_mutable_objects()

    @utils.logged_func
    def update_mutable_objects(self, participant: data_models.Participant = None) -> None:
        """
        Updates the objects that change during lifecycle of a match.
        :param participant: The Participant object.
        """

        for obj in self._obj_list:
            obj.destroy()

        if participant:
            self._participant = participant
            logging.debug(f'Updating displayed objects for {participant.summoner.name}#{participant.summoner.tagline}')

        if self._participant.stats:
            stats_label = ctk.CTkLabel(self.champ_frame,
                                       text=f'{self._participant.stats.kills}/'
                                            f'{self._participant.stats.deaths}/'
                                            f'{self._participant.stats.assists}',
                                       bg_color='red' if self._participant.team_red else 'blue',
                                       text_color='white',
                                       font=('Tahoma', 16))
            stats_label.grid(row=0, column=0, sticky='n', pady=(20, 20))
            self._obj_list.append(stats_label)

            tag_button = ctk.CTkButton(self,
                                       text='ADD TAG',
                                       fg_color='red' if self._participant.team_red else 'blue',
                                       hover_color='dark red' if self._participant.team_red else 'dark blue',
                                       border_width=0,
                                       font=('Tahoma', 16))
            tag_button.configure(command=lambda participant=self._participant,
                                                parent=self: AddTagWindow(parent, participant))
            tag_button.grid(row=1, column=0, sticky='NSEW', padx=(10, 10))
            self._obj_list.append(tag_button)
        else:
            mastery_label = ctk.CTkLabel(self.champ_frame,
                                         text=f'{self._participant.mastery_points:,}',
                                         bg_color='red' if self._participant.team_red else 'blue',
                                         text_color='white',
                                         font=('Tahoma', 16))
            mastery_label.grid(row=0, column=0, sticky='n', pady=(20, 20))
            self._obj_list.append(mastery_label)

            alertbar = ParticipantAlertsBar(self, self._participant)
            alertbar.grid(row=1, column=0, sticky='NSEW')
            self._obj_list.append(alertbar)

    @utils.logged_func
    def select_participant(self, participant: data_models.Participant):
        """
        Triggers an event showing participants nameplate was clicked - showing user wants to display additional
        info about this participant.
        :param participant: The Participant object.
        """
        self.trigger_event('participant_picked', participant=participant)

    @utils.logged_func
    def add_tag(self, tag: data_models.Tag, severity: data_models.Severity, note: str) -> None:
        """
        Trigger an event showing a tag is to be added to a participant.
        :param tag: Tag from enum to add.
        :param severity: Severity from enum to add.
        :param note: Text of the note.
        """
        logging.debug(f'Adding tag for {self._participant.summoner.name}#{self._participant.summoner.tagline}')
        self.trigger_event('add_tag',
                           puu_id=self._participant.summoner.puu_id,
                           tag=tag,
                           severity=severity,
                           note=note)

    @utils.logged_func
    def _get_lazyreaders(self) -> None:
        """
        Gets the instances of lazy readers.
        """
        if self.lazychampions is None:
            self.lazychampions = utils.LazyChampions(None)
        if self.lazyrunes is None:
            self.lazyrunes = utils.LazyRunes(None)
        if self.lazysummoners is None:
            self.lazysummoners = utils.LazySummoners(None)


class ParticipantInfoFrame(ctk.CTkScrollableFrame):
    """
    Frame showing additional info about a selected participant.
    """

    def __init__(self, *args, **kwargs):
        """
        Inits ParticipantInfoFrame.
        """
        super().__init__(*args, height=1176, width=438, **kwargs)

        self.lazychampions = None
        self._obj_list = []

    @utils.logged_func
    def show_data(self, participant: data_models.Participant) -> None:
        """
        Show data about provided participant.
        :param participant: The Participant object.
        """
        logging.debug(f'show_data participant: {participant}')

        for obj in self._obj_list:
            obj.destroy()

        nameframe = ctk.CTkFrame(self,
                                 height=130,
                                 width=418,
                                 fg_color='red' if participant.team_red else 'blue'
                                 )
        nameframe.grid(row=0, column=0, pady=(10, 10), padx=(10, 10), sticky='w')

        self.lazychampions = utils.LazyChampions(None)

        champ_icon = ctk.CTkLabel(nameframe,
                                  image=self.lazychampions.get_icon_image(str(participant.champion)),
                                  text='')
        champ_icon.grid(row=0, sticky='nw', pady=(5, 5), padx=(10, 10))

        namelabel = ctk.CTkLabel(nameframe,
                                 text=f'Information about: {participant.summoner.name}#'
                                      f'{participant.summoner.tagline}',
                                 text_color='white',
                                 fg_color='red' if participant.team_red else 'blue',
                                 width=278,
                                 height=21
                                 )
        namelabel.grid(row=0, sticky='ns', pady=(5, 5), padx=(140, 10))
        self._obj_list.append(nameframe)

        if participant.stats:
            statsframe = ParticipantStatsFrame(self,
                                               participant,
                                               border_color='goldenrod',
                                               border_width=1)
            statsframe.grid(row=1, column=0, pady=(10, 10), padx=(10, 10))
            self._obj_list.append(statsframe)

        if participant.summoner.tags:
            for i, tag in enumerate(participant.summoner.tags):
                logging.debug(f'tag: {tag}')
                tagframe = TagFrame(self, tag)
                tagframe.grid(row=10 + i, column=0, pady=(10, 10), padx=(10, 10), sticky='w')
                self._obj_list.append(tagframe)

        if participant.alerts:
            already_there = len(self._obj_list)
            for i, alert in enumerate(participant.alerts):
                if alert.priority < 10:
                    alertframe = AlertFrame(self, alert)
                    alertframe.grid(row=10 + i + already_there, column=0, pady=(10, 10), padx=(10, 10), sticky='w')
                    self._obj_list.append(alertframe)


class ActiveMatchView(utils.Observable, ctk.CTkFrame):
    """
    The Frame showing information about match currently played by the user, or the most recently finished one.
    """

    def __init__(self, *args, **kwargs):
        """
        Inits ActiveMatchView.
        """
        super().__init__(*args, height=1176, width=2002, **kwargs)

        self._run_check = False
        self._check_after = 10000

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=2)
        self.columnconfigure(3, weight=2)
        self.columnconfigure(4, weight=2)
        self.columnconfigure(5, weight=3)

        self._champ_frames = dict()

        self._champ_frames['blue_1'] = ChampFrame(self, 'top')
        self._champ_frames['blue_1'].grid(column=0, row=0)
        self._champ_frames['blue_2'] = ChampFrame(self, 'jungle')
        self._champ_frames['blue_2'].grid(column=1, row=0)
        self._champ_frames['blue_3'] = ChampFrame(self, 'mid')
        self._champ_frames['blue_3'].grid(column=2, row=0)
        self._champ_frames['blue_4'] = ChampFrame(self, 'bot')
        self._champ_frames['blue_4'].grid(column=3, row=0)
        self._champ_frames['blue_5'] = ChampFrame(self, 'support')
        self._champ_frames['blue_5'].grid(column=4, row=0)

        self._champ_frames['red_1'] = ChampFrame(self, 'top')
        self._champ_frames['red_1'].grid(column=0, row=1)
        self._champ_frames['red_2'] = ChampFrame(self, 'jungle')
        self._champ_frames['red_2'].grid(column=1, row=1)
        self._champ_frames['red_3'] = ChampFrame(self, 'mid')
        self._champ_frames['red_3'].grid(column=2, row=1)
        self._champ_frames['red_4'] = ChampFrame(self, 'bot')
        self._champ_frames['red_4'].grid(column=3, row=1)
        self._champ_frames['red_5'] = ChampFrame(self, 'support')
        self._champ_frames['red_5'].grid(column=4, row=1)

        self.infoframe = ParticipantInfoFrame(self)
        self.infoframe.grid(column=5, row=0, rowspan=2, sticky='NSEW')

        self.after(5000, self.background_task)

    @utils.logged_func
    def update_champ_frames(self, update_dict: dict[str: data_models.Participant], new_participant: bool) -> None:
        """
        Updates all provided champ frames.
        :param update_dict: Dictionary with champframe position as key and Participant object as value.
        :param new_participant: True if the Participant objects are entirely different, False if it's just updated.
        """
        for k, v in update_dict.items():
            logging.debug(f'ActiveMatchView.update_champ_frames tries to update frame for frame {k}')
            if new_participant:
                self._champ_frames[k].show_new_participant(v)
            else:
                self._champ_frames[k].update_mutable_objects(v)

    def bind_champframes_events(self, event: str, fn: Callable) -> None:
        """
        Binds provided events for all champ_frames.
        :param event: Event to be binded.
        :param fn: Callback function.
        """
        for champ_frame in self._champ_frames.values():
            champ_frame.add_event_listener(event, fn)

    def background_task(self) -> None:
        """
        Task running in the background. Next trigger will be after self._check_after delay.
        """
        if self._run_check:
            self.trigger_event('check_active_match')
        self.after(self._check_after, self.background_task)

    def set_run_check(self, run_check: bool) -> None:
        """
        Sets variable controlling if background task should check for state of users active match.
        :param run_check: True if background task should check, False if not.
        """
        self._run_check = run_check

    def set_check_after(self, check_after: int) -> None:
        """
        Sets the delay between runs of background task.
        :param check_after: Delay in milliseconds.
        """
        self._check_after = check_after
