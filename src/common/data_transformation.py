import common.data_models as data_models
import datetime
from requests import Response
from fastapi import Request


def response_to_match_detail(request: Request, r: Response) -> data_models.Match:
    """
    Transforms response from RIOT about finished match to data model Match.
    :param request: Request object from FatsAPI.
    :param r: Response from RIOT.
    :return: Match object.
    """
    match_detail = data_models.MatchDetail(
        match_creation=datetime.datetime.fromtimestamp(r.json().get('info', {}).get('gameCreation', 0) / 1000),
        match_end=datetime.datetime.fromtimestamp(r.json().get('info', {}).get('gameEndTimestamp', 0) / 1000),
        game_version=r.json().get('info', {}).get('gameVersion'),
        winning_team_red=next(iter([result['win'] for result in r.json()['info']['teams'] if result['teamId'] == 200]),
                              None),
        match_duration=datetime.timedelta(seconds=r.json().get('info', {}).get('gameDuration', None))
    )
    match = data_models.Match(
        server=request.app.SERVER,
        match_id=r.json()['metadata']['matchId'].split('_')[1],
        match_type=r.json()['info']['gameMode'],
        match_start=datetime.datetime.fromtimestamp(
            r.json().get('info', {}).get('gameStartTimestamp', 0) / 1000),
        participants=[data_models.Participant(
            summoner=data_models.Summoner(
                summoner_id=participant['summonerId'],
                puu_id=participant['puuid'],
                name=participant['riotIdGameName'],
                tagline=participant['riotIdTagline'],
                server=request.app.SERVER,
                profile_icon=participant['profileIcon'],
                summoner_level=participant['summonerLevel']
            ),
            team_red=True if participant['teamId'] == 200 else False,
            role=request.app.ROLE[participant['individualPosition']],
            summ_spell1=participant['summoner1Id'],
            summ_spell2=participant['summoner2Id'],
            champion=participant['championId'],
            primary_runes=participant.get('perks', {}).get('styles', {None})[0].get('style', None),
            secondary_runes=participant.get('perks', {}).get('styles', {None, None})[1]['style'],
            runes=[participant.get('perks', {}).get('styles',
                                                    {None})[0].get('selections', {None})[0].get('perk', None),
                   participant.get('perks', {}).get('styles',
                                                    {None})[0].get('selections', {None, None})[1].get('perk', None),
                   participant.get('perks', {}).get('styles',
                                                    {None})[0].get('selections',
                                                                   {None, None, None})[2].get('perk', None),
                   participant.get('perks', {}).get('styles',
                                                    {None})[0].get('selections',
                                                                   {None, None, None, None})[3].get('perk', None),
                   participant.get('perks', {}).get('styles',
                                                    {None, None})[1].get('selections', {None})[0].get('perk', None),
                   participant.get('perks', {}).get('styles',
                                                    {None, None})[1].get('selections',
                                                                         {None, None})[1].get('perk', None)],
            small_runes=[participant.get('perks', {}).get('statPerks', {}).get('defense', None),
                         participant.get('perks', {}).get('statPerks', {}).get('flex', None),
                         participant.get('perks', {}).get('statPerks', {}).get('offense', None)],
            stats=data_models.ParticipantStats(
                kills=participant['kills'],
                deaths=participant['deaths'],
                assists=participant['assists'],
                item0=participant['item0'],
                item1=participant['item1'],
                item2=participant['item2'],
                item3=participant['item3'],
                item4=participant['item4'],
                item5=participant['item5'],
                item6=participant['item6'],
                total_gold=participant['goldEarned'],
                cs=participant['totalMinionsKilled'],
            )
        ) for participant in r.json()['info']['participants']],
        match_detail=match_detail
    )

    if r.json()['info']['gameDuration'] < 900:
        match.match_detail.winning_team_red = None

    return match


def response_to_active_match(request: Request, r: Response) -> data_models.Match:
    """
    Transforms response from RIOT about match in progress to data model Match.
    :param request: Request object from FatsAPI.
    :param r: Response from RIOT.
    :return: Match object.
    """
    match = data_models.Match(
        server=request.app.SERVER,
        match_id=r.json()['gameId'],
        match_type=r.json()['gameMode'],
        match_start=datetime.datetime.fromtimestamp(
            r.json()['gameStartTime'] / 1000) if r.json()['gameStartTime'] != 0 else None,
        participants=[data_models.Participant(
            summoner=data_models.Summoner(
                server=request.app.SERVER,
                summoner_id=participant['summonerId'],
                puu_id=participant['puuid'],
                name=participant['riotId'].split('#')[0],
                tagline=participant['riotId'].split('#')[1]
            ),
            team_red=True if participant['teamId'] == 200 else False,
            summ_spell1=participant['spell1Id'],
            summ_spell2=participant['spell2Id'],
            champion=participant['championId'],
            bot=participant['bot'],
            primary_runes=participant.get('perks', {}).get('perkStyle', None),
            secondary_runes=participant.get('perks', {}).get('perkSubStyle', None),
            runes=participant.get('perks', {}).get('perkIds', None),
        ) for participant in r.json()['participants']]
    )

    return match
