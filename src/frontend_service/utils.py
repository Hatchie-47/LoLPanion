import os
import json
import logging
from PIL import Image
from abc import ABC, abstractmethod
import customtkinter as ctk
from typing import Callable, Any, Protocol
from abc import abstractmethod


class TrackingLoadingProgress(Protocol):
    """
    Protocol for views that track update of loading process.
    """

    @abstractmethod
    def update_progress(self, progress: float, label: str) -> None:
        """
        Updates loading tracking elements.
        :param progress: Float between 0 and 1 showing percentage of progress to be shown on progressbar.
        :param label: Text to be displayed as a progress message.
        """
        raise NotImplementedError


class Observable:
    """
    Meant to be inherited from. Makes object Observable.
    """

    def __init__(self, *args, **kwargs):
        """
        Inits Observable.
        """
        self._event_listeners = {}
        super().__init__(*args, **kwargs)

    def add_event_listener(self, event: str, fn: Callable) -> Callable:
        """
        Adds a function to be called when event is triggered.
        :param event: The event to be listened to.
        :param fn: Function to be called when event is triggered.
        :return: Self.
        """
        try:
            self._event_listeners[event].append(fn)
        except KeyError:
            self._event_listeners[event] = [fn]

        logging.debug(f'Subscribed to event {event} on {self.__class__.__name__} with function {fn}.')

        return lambda: self._event_listeners[event].remove(fn)

    def trigger_event(self, event: str, *args, **kwargs) -> None:
        """
        Triggeres an event and calls all the listeners.
        :param event: Event triggered.
        """
        logging.debug(f'{self.__class__.__name__} triggering event {event} with data {args}, {kwargs}.')
        if event not in self._event_listeners.keys():
            return

        for func in self._event_listeners[event]:
            logging.debug(f'{self.__class__.__name__} triggers event {event} with function {func}')
            if kwargs:
                func(self, *args, **kwargs)
            else:
                func(self)


def logged_func(func: Callable) -> Callable:
    """
    Decorator that logs any exception during the functions run as error. Meant to use for tkinter as it otherwise
    silently ignores the errors.
    :param func: Function to be decorated.
    :return: Decorated function.
    """
    def result(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f'UI encountered an error: {e}', exc_info=True)

    return result


class LazyReader(ABC):
    """
    Abstract singleton lazy reader for often reused images to load these only once.
    """
    _instance = None

    def __new__(cls, version: str | None):
        """
        Ensures this class is singleton.
        :param version: Version of the data.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self, version: str | None):
        """
        Inits LazyReader.
        :param version: Version of the data.
        """
        if self.__initialized:
            return

        self.images = {}
        self.version = version
        self.load_list()
        self.__initialized = True

    @classmethod
    def reset(cls) -> None:
        """
        Throws away the instance, resulting in new one being created on next call.
        """
        cls._instance = None

    @abstractmethod
    def load_list(self):
        """
        Abstract method loading the list of images from data file.
        """
        pass

    @abstractmethod
    def get_image(self, id: str) -> ctk.CTkImage:
        """
        Abstract method loading the image if it wasn't loaded already, otherwise returning it.
        :param id: Id of the image.
        :return: Image.
        """
        pass


class LazySummoners(LazyReader):
    """
    Lazy reads summoner spell images.
    """

    def __init__(self, version: str | None):
        """
        Inits LazySummoners.
        :param version: Version of the data.
        """
        super().__init__(version)

    def load_list(self):
        """
        Load list of summoner spells.
        """
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'ddragon', self.version, 'data', 'en_US', 'summoner.json')) as f:
            data = json.load(f)
            for spell in data['data'].items():
                self.images[spell[1]['key']] = {'name': spell[1]['image']['full'],
                                                'ctkimage': None}

    def get_image(self, id: str) -> ctk.CTkImage:
        """
        Loading the summoner spell image if it wasn't loaded already, otherwise returning it.
        :param id: Id of the summoner spell.
        :return: Image.
        """
        if self.images[id]['ctkimage']:
            pass
        else:
            self.images[id]['ctkimage'] = ctk.CTkImage(Image.open(
                os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'ddragon', self.version, 'img', 'spell', self.images[id]["name"])),
                size=(64, 64))
        return self.images[id]['ctkimage']


class LazyRunes(LazyReader):
    """
    Lazy reads runes images.
    """

    def __init__(self, version: str | None):
        """
        Inits LazyRunes.
        :param version: Version of the data.
        """
        super().__init__(version)

    def load_list(self):
        """
        Load list of runes.
        """
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'ddragon', self.version, 'data', 'en_US', 'runesReforged.json')) as f:
            data = json.load(f)
            for tree in data:
                self.images[str(tree['id'])] = {'name': tree['icon'],
                                                'ctkimage': None}
                for slot in tree['slots']:
                    for rune in slot['runes']:
                        self.images[str(rune['id'])] = {'name': rune['icon'],
                                                        'ctkimage': None}

    def get_image(self, id: str) -> ctk.CTkImage:
        """
        Loading the rune image if it wasn't loaded already, otherwise returning it.
        :param id: Id of the rune.
        :return: Image.
        """
        if self.images[id]['ctkimage']:
            pass
        else:
            self.images[id]['ctkimage'] = ctk.CTkImage(Image.open(
                os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'ddragon', 'img', self.images[id]["name"])),
                size=(32, 32))
        return self.images[id]['ctkimage']


class LazyChampions(LazyReader):
    """
    Lazy reads champions images.
    """

    def __init__(self, version: str | None):
        """
        Inits LazyChampions.
        :param version: Version of the data.
        """
        super().__init__(version)

    def load_list(self):
        """
        Load list of champions.
        """
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'ddragon', self.version, 'data', 'en_US', 'champion.json')) as f:
            data = json.load(f)
            for champ in data['data'].items():
                self.images[champ[1]['key']] = {'name': champ[1]['id'],
                                                'ctkimage': None,
                                                'iconimage': None}

    def get_image(self, id: str) -> ctk.CTkImage:
        """
        Loading the champion image if it wasn't loaded already, otherwise returning it.
        :param id: Id of the champion.
        :return: Image.
        """
        if self.images[id]['ctkimage']:
            pass
        else:
            self.images[id]['ctkimage'] = ctk.CTkImage(Image.open(
                os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'ddragon', 'img', 'champion', 'loading', f'{self.images[id]["name"]}_0.jpg')),
                size=(308, 560))
        return self.images[id]['ctkimage']

    def get_icon_image(self, id: str) -> ctk.CTkImage:
        """
        Loading the champion icon image if it wasn't loaded already, otherwise returning it.
        :param id: Id of the champion.
        :return: Image of the icon.
        """
        if self.images[id]['iconimage']:
            pass
        else:
            self.images[id]['iconimage'] = ctk.CTkImage(Image.open(
                os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'ddragon', self.version, 'img', 'champion', f'{self.images[id]["name"]}.png')),
                size=(120, 120))
        return self.images[id]['iconimage']


class LazyItems(LazyReader):
    """
    Lazy reads items images.
    """

    def __init__(self, version: str | None):
        """
        Inits LazyItems.
        :param version: Version of the data.
        """
        super().__init__(version)

    def load_list(self):
        """
        Load list of items.
        """
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'ddragon', self.version, 'data', 'en_US', 'item.json')) as f:
            data = json.load(f)
            for item in data['data'].keys():
                self.images[item] = {'name': item,
                                     'ctkimage': None}

    def get_image(self, id: str) -> ctk.CTkImage:
        """
        Loading the item image if it wasn't loaded already, otherwise returning it.
        :param id: Id of the item.
        :return: Image.
        """
        id = '7050' if id == '0' else id
        if self.images[id]['ctkimage']:
            pass
        else:
            self.images[id]['ctkimage'] = ctk.CTkImage(Image.open(
                os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'ddragon', self.version, 'img', 'item', f'{self.images[id]["name"]}.png')),
                size=(64, 64))
        return self.images[id]['ctkimage']
