class RiotAPIException(Exception):
    """
    Raised when Riot API returns status code suggesting an error.
    """

    def __init__(self, status_code: int) -> None:
        super().__init__('Unexpected status code returned by Riot API.')
        self.status_code = status_code


class UnexpectedQueryParamException(Exception):
    """
    Raised when API handler gets unexpected query param.
    """

    def __init__(self, handler: str, params: set) -> None:
        super().__init__(f'Unexpected query param {params} given to {handler}.')


class UnexpectedQueryParamCombinationException(Exception):
    """
    Raised when API handler gets unexpected query param.
    """

    def __init__(self, handler: str, params: set) -> None:
        super().__init__(f'Unexpected query params combination {params} given to {handler}.')


class UIIncorrectDataReceivedException(Exception):
    """
    Raised when UI element receives incorrect data.
    """

    def __init__(self, name: str, problem: str) -> None:
        super().__init__(f'UI element {name} encountered incorrect data: {problem}.')
