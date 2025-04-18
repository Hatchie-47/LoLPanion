import common.data_models as data_models
import common.exceptions
import requests
import logging
from abc import ABC
from requests import Response


class RIOTAPIHandler(ABC):
    """
    Abstract class for all Riot API endpoints.
    """

    def __init__(self, server: data_models.Server, endpoint: str, expected_statuses: dict,
                 query_params: list = None) -> None:
        """
        Inits the RIOTAPIHandler.
        :param server: Server to which the handler connects to.
        :param endpoint: The endpoint this handler calls.
        :param expected_statuses: Dictionary of expected statuses of response and their meaning.
        :param query_params: List of expected query parameters.
        """
        self._server = server
        self._endpoint = endpoint
        self._expected_statuses = expected_statuses
        self._query_params = query_params if query_params else ['']

    def try_request(self, headers: dict = None, params: dict = None, url_params: dict = None) -> Response | None:
        """
        Handles the sending of request to RIOT API and processing the response.
        :param headers: Header parameters of the request.
        :param params: URL parameters of the request to be added as they are.
        :param url_params: URL parameters of the request that require some more work.
        :return: Response from RIOT API.
        """
        logging.debug(f'Handling request in handler {self.__class__.__name__}')
        try:
            full_url = self._construct_url(url_params)
            logging.debug(f'Calling RIOT API with full url: {full_url}')
            r = self._handle_call(url=full_url,
                                  headers=headers,
                                  params=params)
            logging.info(f'Request in handler {self.__class__.__name__} successfully finished.')
            if len(r.content) < 10000:
                logging.debug(r.json())
            else:
                logging.debug('Message too big to log.')
            return r
        except common.exceptions.RiotAPIException as e:
            logging.error(f'Unexpected error sending request in {self.__class__.__name__} with status code: '
                          f'{e.status_code}')
            return None

    def _handle_call(self, url: str, headers: dict, params: dict) -> Response | None:
        """
        Send the request to RIOT API.
        :param url: URL of the request including the processed parameters.
        :param headers: Header parameters of the request.
        :param params: URL parameters of the request.
        :return: Response if successfull or expected status is returned. Raises RiotAPIException if unexpected status
            is returned.
        """
        r = requests.get(url=url, headers=headers, params=params)
        if r.status_code in self._expected_statuses:
            logging.debug(self._expected_statuses[r.status_code])
            return r
        else:
            raise common.exceptions.RiotAPIException(r.status_code)

    def _construct_url(self, url_params: dict = None) -> str:
        """
        Modifies the URL based on given parameters.
        :param url_params: Parameters to modify the URL.
        :return: Modified URL.
        """
        url = f'https://{self._server.server}.api.riotgames.com/lol/{self._endpoint}'
        if not url_params:
            return url
        if not set(url_params.keys()) <= set(self._query_params):
            raise common.exceptions.UnexpectedQueryParamException(self.__class__.__name__,
                                                                  set(url_params.keys()) - set(self._query_params))
        return f"{url}/{url_params['']}"


class RIOTActiveMatchHandler(RIOTAPIHandler):
    """
    Class handling checking for active match.
    """

    def __init__(self, server: data_models.Server) -> None:
        """
        Inits the RIOTActiveMatchHandler.
        :param server: Server to which the handler connects to.
        """
        endpoint = 'spectator/v5/active-games/by-summoner'
        expected_statuses = {200: 'Active game found.',
                             404: 'No game in progress.'}
        super().__init__(server, endpoint, expected_statuses, None)


class RIOTPlayerHandler(RIOTAPIHandler):
    """
    Class handling player information.
    """

    def __init__(self, server: data_models.Server) -> None:
        """
        Inits the RIOTPlayerHandler.
        :param server: Server to which the handler connects to.
        """
        endpoint = 'summoner/v4/summoners'
        expected_statuses = {200: 'Player found.',
                             404: 'Player does not exist.'}
        query_params = ['puu_id', 'account_id', 'summoner_id', 'name']
        super().__init__(server, endpoint, expected_statuses, query_params)

    def _construct_url(self, url_params: dict = None) -> str:
        """
        Modifies the URL based on given parameters.
        :param url_params: Parameters to modify the URL.
        :return: Modified URL.
        """
        url = f'https://{self._server.server}.api.riotgames.com/lol/{self._endpoint}'
        if not url_params:
            return url
        if not set(url_params.keys()) <= set(self._query_params):
            raise common.exceptions.UnexpectedQueryParamException(self.__class__.__name__,
                                                                  set(url_params.keys()) - set(self._query_params))
        if len(url_params) > 1:
            raise common.exceptions.UnexpectedQueryParamCombinationException(self.__class__.__name__,
                                                                             set(url_params.keys()))
        return (f"{url}/{url_params['summoner_id'] if 'summoner_id' in url_params else ''}"
                f"{'by-account/' + url_params['account_id'] if 'account_id' in url_params else ''}"
                f"{'by-puuid/' + url_params['puu_id'] if 'puu_id' in url_params else ''}"
                f"{'by-name/' + url_params['name'] if 'name' in url_params else ''}")


class RIOTMatchHandler(RIOTAPIHandler):
    """
    Class handling matches information.
    """

    def __init__(self, server: data_models.Server) -> None:
        """
        Inits the RIOTMatchHandler.
        :param server: Server to which the handler connects to.
        """
        endpoint = 'match/v5/matches'
        expected_statuses = {200: 'Match found.',
                             404: 'Match does not exist.'}
        query_params = ['', 'timeline', 'puu_id', 'type']
        super().__init__(server, endpoint, expected_statuses, query_params)

    def _construct_url(self, url_params: dict = None) -> str:
        """
        Modifies the URL based on given parameters.
        :param url_params: Parameters to modify the URL.
        :return: Modified URL.
        """
        url = f'https://{self._server.cluster}.api.riotgames.com/lol/{self._endpoint}'
        if not url_params:
            return url
        if not set(url_params.keys()) <= set(self._query_params):
            raise common.exceptions.UnexpectedQueryParamException(self.__class__.__name__,
                                                                  set(url_params.keys()) - set(self._query_params))
        if 'type' in url_params.keys() and 'puu_id' not in url_params.keys():
            raise common.exceptions.UnexpectedQueryParamException(self.__class__.__name__,
                                                                  set(url_params.keys()) - set(self._query_params))
        if 'puu_id' in url_params.keys():
            return f"{url}/by-puuid/{url_params['puu_id']}/ids?count=10" \
                   f"{'&type=' + url_params['type'] if 'type' in url_params else ''}"
        else:
            return f"{url}/{self._server.server.upper()}_{url_params['']}" \
                   f"{'/timeline' if 'timeline' in url_params else ''}"


class RIOTMasteryHandler(RIOTAPIHandler):
    """
    Class handling checking of player mastery information.
    """

    def __init__(self, server: data_models.Server) -> None:
        """
        Inits the RIOTMasteryHandler.
        :param server: Server to which the handler connects to.
        """
        endpoint = 'champion-mastery/v4/champion-masteries'
        expected_statuses = {200: 'Game found.',
                             404: 'Game does not exist.'}
        query_params = ['', 'top', 'championId']
        super().__init__(server, endpoint, expected_statuses, query_params)

    def _construct_url(self, url_params: dict = None) -> str:
        """
        Modifies the URL based on given parameters.
        :param url_params: Parameters to modify the URL.
        :return: Modified URL.
        """
        url = f'https://{self._server.server}.api.riotgames.com/lol/{self._endpoint}'
        if not url_params:
            return url
        if not set(url_params.keys()) <= set(self._query_params):
            raise common.exceptions.UnexpectedQueryParamException(self.__class__.__name__,
                                                                  set(url_params.keys()) - set(self._query_params))
        if 'championId' in url_params.keys() and 'top' in url_params.keys():
            raise common.exceptions.UnexpectedQueryParamCombinationException(self.__class__.__name__,
                                                                             set(url_params.keys()))
        return (f"{url}/by-puuid/{url_params['']}{'/top?count=' + url_params['top'] if 'top' in url_params else ''}"
                f"{'/by-champion/' + str(url_params['championId']) if 'championId' in url_params else ''}")


class RIOTAccountHandler(RIOTAPIHandler):
    """
    Class handling player information in newer endpoint.
    """

    def __init__(self, server: data_models.Server) -> None:
        """
        Inits the RIOTAccountHandler.
        :param server: Server to which the handler connects to.
        """
        endpoint = 'account/v1/accounts'
        expected_statuses = {200: 'Player found.',
                             403: 'Incorrect RIOT API key.',
                             404: 'Player does not exist.',
                             503: 'Service unavailable.'}
        query_params = ['puu_id', 'gamename', 'tagline']
        super().__init__(server, endpoint, expected_statuses, query_params)

    def _construct_url(self, url_params: dict = None) -> str:
        """
        Modifies the URL based on given parameters.
        :param url_params: Parameters to modify the URL.
        :return: Modified URL.
        """
        url = f'https://{self._server.cluster}.api.riotgames.com/riot/{self._endpoint}'
        if not url_params:
            return url
        if not set(url_params.keys()) <= set(self._query_params):
            raise common.exceptions.UnexpectedQueryParamException(self.__class__.__name__,
                                                                  set(url_params.keys()) - set(self._query_params))
        if not (set(url_params.keys()) == set(('puu_id',)) or set(url_params.keys()) == set(('gamename', 'tagline'))):
            raise common.exceptions.UnexpectedQueryParamCombinationException(self.__class__.__name__,
                                                                             set(url_params.keys()))
        return (f"{url}/{'by-puuid/' + url_params['puu_id'] if 'puu_id' in url_params else ''}"
                f"{'by-riot-id/' + url_params['gamename'] if 'gamename' in url_params else ''}"
                f"{'/' + url_params['tagline'] if 'tagline' in url_params else ''}")


class RIOTChampionRotation(RIOTAPIHandler):
    """
    Class handling checking free champions rotation.
    """

    def __init__(self, server: data_models.Server) -> None:
        """
        Inits the RIOTChampionRotation.
        :param server: Server to which the handler connects to.
        """
        endpoint = 'platform/v3/champion-rotations'
        expected_statuses = {200: 'Active game found.',
                             403: 'Incorrect RIOT API key.',
                             503: 'Service unavailable.'}
        super().__init__(server, endpoint, expected_statuses, None)
