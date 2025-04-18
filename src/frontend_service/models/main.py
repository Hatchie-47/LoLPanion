from .active_match import ActiveMatchModel
from .settings import SettingsModel


class Model:
    """
    Main controller of the application.
    """

    def __init__(self) -> None:
        """
        Inits main Model.
        """
        self.active_match = ActiveMatchModel()
        self.settings = SettingsModel()
