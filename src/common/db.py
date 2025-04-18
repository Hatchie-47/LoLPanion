import common.data_models as data_models
import os
import psycopg
import logging
from typing import Callable, Any
from datetime import datetime

connstring = f'postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@' \
             f'postgres:5432/{os.getenv("POSTGRES_DB")}'


def get_conn() -> psycopg.Connection:
    """
    Generates connection to db.
    :return: Connection object.
    """
    return psycopg.connect(conninfo=connstring)


def db_func(func: Callable) -> Callable:
    """
    Decorator for db function that catches errors and returns None in case any occurred.
    :param func: The function to be decorated.
    :return: Decorated function.
    """
    def result(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except psycopg.Error as e:
            logging.error(f'Database encountered an error: {e}', exc_info=True)
            return None

    return result


@db_func
def set_user(name: str,
             tagline: str,
             riot_puu_id: str,
             id_server: int) -> bool:
    """
    Sets current users summoner.
    :param name: Name of the summoner.
    :param tagline: Tagline of the summoner.
    :param riot_puu_id: Puu id of the summoner.
    :param id_server: Id of the server.
    :return: Bool representing success.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT general.set_user(%s, %s, %s, %s)',
                        (name,
                         tagline,
                         riot_puu_id,
                         id_server))

            return cur.fetchone()


@db_func
def get_user() -> data_models.Summoner:
    """
    Gets current users summoner.
    :return: Summoner object.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT general.get_user()',
                        ())

            user = cur.fetchone()

    return data_models.Summoner(
        server=data_models.Server(id=1, cluster='europe', server='euw1'),
        name=user[0][0],
        tagline=user[0][1],
        puu_id=user[0][2]
    )


@db_func
def upsert_match(riot_match_id: int,
                 id_server: int,
                 match_start: datetime,
                 match_end: datetime,
                 winning_team_red: bool,
                 match_creation: datetime,
                 game_version: str) -> int:
    """
    Upserts information about match.
    :param riot_match_id: Match id.
    :param id_server: Id of the server.
    :param match_start: Timestamp of match start.
    :param match_end: Timestamp of match end.
    :param winning_team_red: True = red team won, False = blue team won, None = no winner yet.
    :param match_creation: Timestamp of match creation.
    :param game_version: Patch on which the match was played.
    :return: Match id.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT data.upsert_match(%s, %s, %s, %s, %s, %s, %s)',
                        (riot_match_id,
                         id_server,
                         match_start,
                         match_end,
                         winning_team_red,
                         match_creation,
                         game_version))

            fetch = cur.fetchone()[0]
            return fetch


@db_func
def upsert_participant(riot_puu_id: str,
                       id_match: int,
                       team_red: bool,
                       id_role: int,
                       summ_spell1: int,
                       summ_spell2: int,
                       champion: int,
                       mastery_points: int,
                       bot: bool,
                       primary_runes: int,
                       secondary_runes: int,
                       runes: list[int],
                       small_runes: list[int],
                       kills: int,
                       deaths: int,
                       assists: int,
                       items: list[int],
                       total_gold: int,
                       cs: int) -> (int, int):
    """
    Upserts information about participant.
    :param riot_puu_id: Summoners puu id.
    :param id_match: match id.
    :param team_red: True = on red side, False = on blue side.
    :param id_role: Id of the role.
    :param summ_spell1: Id of D summoner spell.
    :param summ_spell2: Id of F summoner spell.
    :param champion: Id of picked champion.
    :param mastery_points: Mastery points on picked champion.
    :param bot: True = is bot, False = is player.
    :param primary_runes: Id of primary runes tree.
    :param secondary_runes: Id of secondary runes tree.
    :param runes: List of runes.
    :param small_runes: List of stats runes.
    :param kills: Number of kills.
    :param deaths: Number of deaths.
    :param assists: Number of assists.
    :param items: List of items ids.
    :param total_gold: Total earned gold.
    :param cs: number of CS.
    :return: Id of match, id of summoner.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT data.upsert_participant(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,'
                        '%s, %s, %s, %s)',
                        (riot_puu_id,
                         id_match,
                         team_red,
                         id_role,
                         summ_spell1,
                         summ_spell2,
                         champion,
                         mastery_points,
                         bot,
                         primary_runes,
                         secondary_runes,
                         runes,
                         small_runes,
                         kills,
                         deaths,
                         assists,
                         items,
                         total_gold,
                         cs))

            return cur.fetchone()


@db_func
def upsert_summoner(name: str,
                    tagline: str,
                    riot_puu_id: str,
                    id_server: int,
                    summoner_level: int,
                    profile_icon: int,
                    revision_date: datetime) -> int:
    """
    Upserts information about summoner.
    :param name: Summoner name.
    :param tagline: Summoner tagline.
    :param riot_puu_id: Puu id of summoner.
    :param id_server: Id of the server.
    :param summoner_level: Summoner account level.
    :param profile_icon: Id of profile icon.
    :param revision_date: Timestamp of last data validity.
    :return: Summoner id.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT data.upsert_summoner(%s, %s, %s, %s, %s, %s, %s)',
                        (name,
                         tagline,
                         riot_puu_id,
                         id_server,
                         summoner_level,
                         profile_icon,
                         revision_date))

            return cur.fetchone()


@db_func
def insert_tag(riot_match_id: int,
               id_server: int,
               riot_puu_id: str,
               tag_id: int,
               severity_id: int,
               note: str) -> bool:
    """
    Inserts new tag.
    :param riot_match_id: Match id.
    :param id_server: Id of teh server.
    :param riot_puu_id: Puu id of the summoner.
    :param tag_id: Id of tag type.
    :param severity_id: Id of tag severity.
    :param note: Note about the tag.
    :return: Bool representing success.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT data.insert_tag(%s, %s, %s, %s, %s, %s)',
                        (riot_match_id,
                         id_server,
                         riot_puu_id,
                         tag_id,
                         severity_id,
                         note))

            return cur.fetchone()


@db_func
def get_tags(riot_puu_id: str) -> list[(int, int, datetime, int, int, str)]:
    """
    Gets all tags for a summoner.
    :param riot_puu_id: Puu id of the summoner.
    :return: List of tags.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT data.select_summoner_tags(%s)',
                        (riot_puu_id,))

            return cur.fetchall()


@db_func
def get_setting(setting: str) -> str:
    """
    Gets value of a setting.
    :param setting: Name of the setting.
    :return: Value of a setting.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT general.get_setting(%s)',
                        (setting,))

            return cur.fetchone()[0]


@db_func
def set_setting(setting: str, value: str) -> bool:
    """
    Changes value of a setting.
    :param setting: Name of the setting.
    :param value: New value of the setting.
    :return: Bool representing success.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT general.set_setting(%s, %s)',
                        (setting, value))

            return cur.fetchone()
