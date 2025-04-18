from views.main import View
from models.main import Model
import common.data_models as data_models
import utils
import logging


class ActiveMatchController:
    """
    Controller responsible for checking currently displayed match.
    """

    def __init__(self, model: Model, view: View) -> None:
        """
        Inits ActiveMatchController.
        :param model: The main model.
        :param view: The main view.
        """
        self.model = model
        self.view = view
        self.frame = self.view.frames['active_match']
        # puu_id: frame! Create it on new_match!
        self.mapping = {}
        self._bind()
        self._match_id = None
        self._participants = []
        self._position = 0

    def _bind(self) -> None:
        """
        Binds all necessary events.
        """
        self.frame.add_event_listener('check_active_match', self._check_active_match)
        self.model.active_match.add_event_listener('participants_updated', self._update_participant_frames)
        self.model.active_match.add_event_listener('new_match_found', self._new_match)
        self.model.active_match.add_event_listener('match_ended', self._match_ended)
        self.frame.bind_champframes_events('participant_picked', self._update_infoframe)
        self.frame.bind_champframes_events('add_tag', self._add_tag)

    @utils.logged_func
    def _check_active_match(self, *args, **kwargs) -> None:
        """
        Checks if there are any changes to currently played match.
        """
        self.model.active_match.check_is_life()

        # Showing information about next participant
        if self._participants:
            if self._position == len(self._participants):
                self._position = 0

            self._update_infoframe(
                participant=self.model.active_match.get_participant(self._participants[self._position])[1])

            self._position += 1

    @utils.logged_func
    def _new_match(self, *args, match_id: int, **kwargs) -> None:
        """
        Switches displayed match. Changes the settings of background task to active match.
        :param match_id: Id of the current match.
        """
        logging.debug(f'ActiveMatchController._new_match with id {match_id}.')
        self._match_id = match_id
        participants_dict = self.model.active_match.get_all_participants()
        self._participants = [value.summoner.puu_id for value in participants_dict.values()]
        self.frame.update_champ_frames(update_dict=participants_dict, new_participant=True)
        self._update_infoframe(participant=self.model.active_match.get_participant(self._participants[0])[1])
        self._position = 1
        self.frame.set_check_after(60000)

    @utils.logged_func
    def _match_ended(self, *args, participants_list: list[str], **kwargs) -> None:
        """
        Sends complete data after match ends to view. Changes the settings of background task to waiting for match.
        :param participants_list: List of participant puu ids.
        """
        logging.debug(f'ActiveMatchController._match_ended with id {self._match_id}.')
        self._update_participant_frames(participants_list=participants_list, new_participant=True)
        self.frame.set_check_after(10000)

    @utils.logged_func
    def _update_participant_frames(self,
                                   *args,
                                   participants_list: list[str],
                                   new_participant: bool = False,
                                   **kwargs) -> None:
        """
        Updates frames for all listed participants.
        :param participants_list: List of puu ids of participants to be updated.
        """
        # Turn list of puu ids to dictionary of puu id: Participant object
        participants_dict = {}
        for participant in participants_list:
            k, v = self.model.active_match.get_participant(participant)
            participants_dict[k] = v

        self.frame.update_champ_frames(update_dict=participants_dict, new_participant=new_participant)

    @utils.logged_func
    def _update_infoframe(self, *args, participant: data_models.Participant, **kwargs) -> None:
        """
        Updates data displayed on the infoframe.
        :param participant: Participant to be displayed in the infoframe.
        """
        logging.debug(f'ActiveMatchController showing {participant.summoner.name}#{participant.summoner.tagline} '
                      f'in the infoframe.')
        self.frame.infoframe.show_data(participant)

    @utils.logged_func
    def _add_tag(self,
                 *args,
                 puu_id: str,
                 tag: data_models.Tag,
                 severity: data_models.Severity,
                 note: str,
                 **kwargs) -> None:
        """
        Adds tag to a participant.
        :param puu_id: Puu id of a participant.
        :param tag: Tag from enum to add.
        :param severity: Severity from enum to add.
        :param note: Text of the note.
        """
        self.model.active_match.add_tag(puu_id, tag, severity, note)
