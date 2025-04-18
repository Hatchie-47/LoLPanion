from utils import Observable
import common.data_models as data_models
import logging
import requests

ROLES_MAPPING = {
    'TOP': 0,
    'JUNGLE': 1,
    'MID': 2,
    'BOT': 3,
    'SUPPORT': 4,
}


class ActiveMatchModel(Observable):
    """
    Model keeping all the data regarding currently detailed match.
    """

    def __init__(self):
        """
        Inits ActiveMatchModel.
        """
        super().__init__()

        self._match = None
        self._participants = {}
        self._match_histories = {}
        # Positions being team color (blue/red), underscore and number 1-5. Examples: blue_1, red_3
        self._participants_positions = {}
        self.got_detail = False
        self.got_timeline = False
        self._updated = []

    def check_is_life(self) -> None:
        """
        Checks the active_match endpoint and reacts accordingly by starting a new mach or ending match
        """
        r = requests.get(url='http://data_service:4701/match/active_match')
        if r.status_code == 200:
            if self._match is None:
                self._new_match(data_models.Match(**r.json()))
            else:
                if r.json()['match_id'] == self._match.match_id:
                    logging.info('Match still in progress.')
                    self._find_additional_data()
                else:
                    logging.info('There is already a different match in progress.')
                    self._new_match(data_models.Match(**r.json()))
        elif r.status_code == 204:
            if self._match:
                logging.info('Match ended.')
                self._end_match_lifecycle()
            else:
                logging.info('No match started yet.')
        else:
            logging.error(f'Unexpected return code from data_service: {r.status_code}.')

    def get_participant(self, puu_id: str) -> tuple[str, data_models.Participant]:
        """
        Gets participant data and their position.
        :param puu_id: Puu id of a participant.
        :return: Tuple containing position of the participant and the Participant object.
        """
        return self._participants_positions[puu_id], self._participants[puu_id]

    def get_all_participants(self) -> dict[str: data_models.Participant]:
        """
        Gets all participants and their positions.
        :return: Dictionary with key being position and value the Participant object.
        """
        return {v: self._participants[k] for k, v in self._participants_positions.items()}

    def add_tag(self, puu_id: str, tag: data_models.Tag, severity: data_models.Severity, note: str) -> None:
        """
        Handles adding tag to a participant.
        :param puu_id: Puu id of a participant.
        :param tag: Tag from enum to add.
        :param severity: Severity from enum to add.
        :param note: Text of the note.
        """
        r = requests.post(url='http://data_service:4701/tag/add_tag',
                          params={
                              'puu_id': puu_id,
                              'match_id': self._match.match_id,
                              'tag': tag,
                              'severity': severity,
                              'note': note
                          })
        if r.status_code == 200:
            logging.info(f'Tag successfully added to {self._participants[puu_id].summoner.name}#'
                         f'{self._participants[puu_id].summoner.name}.')
            self._load_participant_detail(puu_id)
            self.trigger_event('participants_updated', participants_list=[puu_id])
        else:
            logging.warning('Something went wrong adding a tag!.')

    def _new_match(self, match: data_models.Match) -> None:
        """
        Handles processing of new match.
        :param match: Match object.
        """
        if match.match_type == 'CLASSIC':
            logging.info(f'New match found: {match.match_id}!')
            self._match = match
            self._participants = {p.summoner.puu_id: p for p in match.participants}
            self._match_histories = {p.summoner.puu_id: None for p in match.participants}
            self.got_detail = False
            self.got_timeline = False

            for participant in self._participants.values():
                self._load_participant_detail(participant.summoner.puu_id)

            self._map_participants_positions()
            self._process_match_histories()

            for participant in self._participants.values():
                logging.debug(f'Final version of participant: {participant}')

            self.trigger_event('new_match_found', match_id=self._match.match_id)
        else:
            logging.debug('Invalid match type!')

    def _end_match_lifecycle(self) -> None:
        """
        Handles ending of a match.
        """
        if self.got_detail:
            logging.info('Already got match detail')
        else:
            logging.info('Getting match detail...')
            self.got_detail = True if self._load_match_detail() else False
            if self.got_detail:
                self.trigger_event('match_ended', participants_list=self._participants.keys())

        if self.got_timeline:
            logging.info('Already got match timeline')
        else:
            if self.got_detail:
                logging.info('Getting match timeline...')
                self.got_timeline = True if self._load_match_timeline() else False
            else:
                logging.info('Detail is missing, not getting timeline yet.')

        if self.got_detail and self.got_timeline:
            logging.info(f'Match {self._match.match_id} ended.')
        else:
            logging.info(f'Match {self._match.match_id} still missing some data, will retry.')

    def _find_additional_data(self) -> None:
        """
        Handles finding additional data and notifying observers.
        """
        self._updated = []
        self._process_match_histories()

        self.trigger_event('participants_updated', participants_list=self._updated)

    def _load_participant_detail(self, participant_puu_id: str) -> bool:
        """
        Loads detailed information about a participant.
        :param participant_puu_id: Puu id of the participant.
        :return: True if everything was successfully loaded, False otherwise.
        """
        logging.debug('ActiveMatchModel._get_participant_detail')
        participant = self._participants[participant_puu_id]
        participant.alerts = []
        participant.has_history = False
        r = requests.get(url=f'http://data_service:4701/summoner/by-puuid/{participant.summoner.puu_id}')
        if r.status_code == 200:
            participant.summoner.profile_icon = r.json()['profile_icon']
            participant.summoner.revision_date = r.json()['revision_date']
            participant.summoner.tags = [data_models.AssignedTag(**tag) for tag in r.json()['tags']]
            self._add_alerts_from_tags(participant_puu_id)
            return True
        else:
            logging.error(f'Unexpected return code from data_service: {r.status_code}.')
            return False

    def _load_match_detail(self) -> bool:
        """
        Loads detailed information about current match.
        :return: True if everything was successfully loaded, False otherwise.
        """
        logging.debug('ActiveMatchModel._load_match_detail')
        r = requests.get(url=f'http://data_service:4701/match/match_detail/{self._match.match_id}')
        if r.status_code == 200:
            self._match = data_models.Match(**r.json())
            for participant in self._match.participants:
                self._participants[participant.summoner.puu_id] = participant
                self._load_participant_detail(participant.summoner.puu_id)
                self._add_alerts_from_results_history(participant.summoner.puu_id)
            self._map_participants_positions()

            for participant in self._participants.values():
                logging.debug(f'Final version of participant after _load_match_detail: {participant}')
            return True
        else:
            logging.error(f'Unexpected return code from data_service: {r.status_code}.')
            return False

    def _load_match_timeline(self) -> bool:
        """
        Loads timeline data of the current match.
        :return: True if everything was successfully loaded, False otherwise.
        """
        logging.debug('ActiveMatchModel._get_match_timeline')
        r = requests.get(url=f'http://data_service:4701/match/match_timeline/{self._match.match_id}')
        if r.status_code == 200:
            self._match.match_detail.match_timeline = r.json()
            return True
        else:
            logging.error(f'Unexpected return code from data_service: {r.status_code}.')
            return False

    def _process_match_histories(self) -> None:
        """
        Handles the entire process of getting history for every participant in the match and extracting all the usefull
        data out of it.
        """
        for puu_id, history in self._match_histories.items():
            if history is None:
                logging.info(f'Finding match history for summoner with puu_id {puu_id}.')

                r = requests.get(url=f'http://data_service:4701/summoner/match_history/{puu_id}')
                if r.status_code == 200:
                    history = []
                    match_history_ids = r.json()

                    for match_id in match_history_ids:
                        r = requests.get(url=f'http://data_service:4701/match/match_detail/{match_id.split("_")[1]}')
                        if r.status_code == 200:
                            match_detail = data_models.Match(**r.json())
                            our_player = None
                            for match_participant in match_detail.participants:
                                if match_participant.summoner.puu_id == puu_id:
                                    our_player = match_participant
                                    break

                            match_detail.participants = [our_player]

                            history.append(match_detail)
                        else:
                            logging.error(f'Unexpected return code from data_service when getting match '
                                          f'{match_id.split("_")[1]}: {r.status_code}.')

                    if len(history) == len(match_history_ids):
                        logging.info(f'History for summoner with puu_id {puu_id} found.')
                        logging.debug(history)
                        self._match_histories[puu_id] = history
                        self._add_alerts_from_results_history(puu_id)
                        self._updated.append(puu_id)
                    else:
                        logging.info(f'History for summoner with puu_id {puu_id} not found! Will be attempted later.')

                else:
                    logging.error(f'Unexpected return code from data_service when getting match history for summoner '
                                  f'with puu_id {puu_id}: {r.status_code}.')

    def _add_alerts_from_tags(self, participant_puu_id: str) -> bool:
        """
        Adds alerts to participant from existing tags.
        :param participant_puu_id: Puu id of the participant processed.
        :return:  True if everything was successfully loaded, False otherwise.
        """
        logging.debug('ActiveMatchModel._add_alerts_from_tags')
        severity_priority = {
            data_models.Severity.LOW: 10,
            data_models.Severity.MEDIUM: 11,
            data_models.Severity.HIGH: 12
        }

        participant = self._participants[participant_puu_id]
        alerts = []

        for tag in participant.summoner.tags:
            alerts.append(data_models.Alert(name=tag.tag[:3],
                                            detail=f'{tag.added}: {tag.note}',
                                            priority=severity_priority[tag.severity],
                                            color='red'))

        participant.alerts.extend(alerts)

        return True

    def _add_alerts_from_results_history(self, participant_puu_id: str) -> bool:
        """
        Adds alerts to participant from matches history.
        :param participant_puu_id: Puu id of the participant processed.
        :return:  True if everything was successfully loaded, False otherwise.
        """
        logging.debug('ActiveMatchModel._add_alerts_from_results_history')
        alerts = []
        history = self._match_histories[participant_puu_id]
        participant = self._participants[participant_puu_id]

        if history:
            logging.debug(f'For summoner {participant.summoner.name} history has {len(history)} records.')
            results = []
            for h in history:
                if h.match_detail.winning_team_red is not None:
                    results.append(h.participants[0].team_red == h.match_detail.winning_team_red)

            if len(results) == 0:
                logging.debug(f'No valid result!')
            else:
                logging.debug(f'History results vector: {results}')
                wins_count = results.count(True)

                logging.debug(f'WR for summoner {participant.summoner.name} > {(wins_count / len(history)):%}')

                if wins_count > (len(results) * .55):
                    alerts.append(data_models.Alert(name='WR',
                                                    detail=f'{(wins_count / len(results)):.0%} WR from last '
                                                           f'{len(history)} ranked games',
                                                    priority=1,
                                                    color='green'))
                if wins_count < (len(results) * .45):
                    alerts.append(data_models.Alert(name='WR',
                                                    detail=f'{(wins_count / len(results)):.0%} WR from last '
                                                           f'{len(history)} ranked games',
                                                    priority=1,
                                                    color='red'))

                logging.debug(f'Results: {results}')
                streak_length = 1
                streak_type = results[0]
                for match in results[1:]:
                    if match != streak_type:
                        break
                    else:
                        streak_length += 1

                if streak_length > 2:
                    alerts.append(data_models.Alert(name='STR',
                                                    detail=f'{streak_length} ranked games streak of '
                                                           f'{"wins" if streak_type else "loses"}.',
                                                    priority=2,
                                                    color='green' if streak_type else 'red'))

        else:
            logging.debug(f'Summoner {participant.summoner.name} has no history.')

        participant.alerts.extend(alerts)
        participant.has_history = True

        return participant

    def _map_participants_positions(self) -> None:
        """
        Maps participants to positions in teams. Based by roles first and order if roles are not known.
        """
        logging.debug('ActiveMatchModel._map_participants_positions')
        positions = {
            'red_team': {
                'matched': [None, None, None, None, None],
                'unmatched': []
            },
            'blue_team': {
                'matched': [None, None, None, None, None],
                'unmatched': []
            }
        }

        # Put all participants to their place on team and role or unmatched list if unknown role
        for participant in self._participants.values():
            team = 'red_team' if participant.team_red else 'blue_team'
            role = participant.role.name if participant.role else None
            position = ROLES_MAPPING.get(role, None)

            if position and positions[team]['matched'][position] is None:
                positions[team]['matched'][position] = participant.summoner.puu_id
            else:
                positions[team]['unmatched'].append(participant.summoner.puu_id)

        # Putting the unmatched participants in first empty spot
        for team in positions:
            for participant in positions[team]['unmatched']:
                for i, place in enumerate(positions[team]['matched']):
                    if place is None:
                        positions[team]['matched'][i] = participant
                        break

        # Turn positions to self._participants_positions
        self._participants_positions = {}

        for team in positions:
            for i, participant in enumerate(positions[team]['matched']):
                self._participants_positions[participant] = team.split('_')[0] + '_' + str(i + 1)

        logging.debug(f'Final positions mapping: {positions}')
