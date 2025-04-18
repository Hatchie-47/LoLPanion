import common.data_models as data_models
import common.db as db
import common.db_utils as db_utils
import common.data_transformation as data_transformations
import logging
import datetime
from fastapi import APIRouter, Request, Response, status, HTTPException

router = APIRouter()


def save_match_to_db(match: data_models.Match) -> bool:
    """
    Saves entire match object to database, including all related objects.
    :param match: Match to be saved into db.
    :return: True if successfull, False if not.
    """
    error = False

    match_id = db.upsert_match(
        riot_match_id=match.match_id,
        id_server=match.server.id,
        match_start=match.match_start,
        match_end=match.match_detail.match_end if match.match_detail else None,
        winning_team_red=match.match_detail.winning_team_red if match.match_detail else None,
        match_creation=match.match_detail.match_creation if match.match_detail else None,
        game_version=match.match_detail.game_version if match.match_detail else None)
    if match_id:
        for participant in match.participants:
            summoner_id = None
            summoner_id = db.upsert_summoner(name=participant.summoner.name,
                                             tagline=participant.summoner.tagline,
                                             riot_puu_id=participant.summoner.puu_id,
                                             id_server=participant.summoner.server.id,
                                             summoner_level=participant.summoner.summoner_level,
                                             profile_icon=participant.summoner.profile_icon,
                                             revision_date=participant.summoner.revision_date)

            if summoner_id:
                participant_ids = None
                participant_ids = db.upsert_participant(
                    riot_puu_id=participant.summoner.puu_id,
                    id_match=match_id,
                    team_red=participant.team_red,
                    id_role=participant.role.id if participant.role else None,
                    summ_spell1=participant.summ_spell1,
                    summ_spell2=participant.summ_spell2,
                    champion=participant.champion,
                    mastery_points=participant.mastery_points,
                    bot=participant.bot,
                    primary_runes=participant.primary_runes,
                    secondary_runes=participant.secondary_runes,
                    runes=participant.runes,
                    small_runes=participant.small_runes,
                    kills=participant.stats.kills if participant.stats else None,
                    deaths=participant.stats.deaths if participant.stats else None,
                    assists=participant.stats.assists if participant.stats else None,
                    items=[participant.stats.item0 if participant.stats else None,
                           participant.stats.item1 if participant.stats else None,
                           participant.stats.item2 if participant.stats else None,
                           participant.stats.item3 if participant.stats else None,
                           participant.stats.item4 if participant.stats else None,
                           participant.stats.item5 if participant.stats else None,
                           participant.stats.item6 if participant.stats else None],
                    total_gold=participant.stats.total_gold if participant.stats else None,
                    cs=participant.stats.cs if participant.stats else None)
                if not participant_ids:
                    error = True
            else:
                error = True
    else:
        error = True

    if error:
        logging.debug(f'save_match_to_db encountered an error while saving match {match.match_id}')
        return False

    logging.debug(f'save_match_to_db successfully saved match {match.match_id}')
    return True


@router.get('/active_match', status_code=200, response_model=data_models.Match)
async def root(request: Request, response: Response) -> object:
    """
    Returns data about active match, or 204 in case no match is in progress.
    """
    logging.debug('Received GET /match/active_match')

    if not request.app.my_summoner:
        logging.info('Users summoner not set.')
        response.status_code = status.HTTP_412_PRECONDITION_FAILED
        raise HTTPException(status_code=412)

    r = request.app.active_match_handler.try_request(headers={'X-Riot-Token': request.app.riot_api_key},
                                                     url_params={'': request.app.my_summoner.puu_id})

    if r is None:
        logging.error('Unexpected error during processing of GET /match/active_match!')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=500)

    if r.status_code == 200:
        if r.json()['gameQueueConfigId'] not in [420, 440]:
            logging.info('Not a ranked match, skipping!')
            raise HTTPException(status_code=204)
        else:
            if r.json()['gameId'] == request.app.active_match.match_id:
                logging.info(f'Match {request.app.active_match.match_id} still in progress:')
                if request.app.active_match.match_start is None and r.json()['gameStartTime'] != 0:
                    request.app.active_match.match_start = datetime.datetime.fromtimestamp(
                        r.json()['gameStartTime'] / 1000)
                    if db.upsert_match(r.json()['gameId'],
                                       request.app.active_match.match_start,
                                       None,
                                       None,
                                       None,
                                       None,
                                       None):
                        logging.info(f'Start time saved for match {r.json()["gameId"]} to '
                                     f'{request.app.active_match.match_start}.')
            else:
                logging.info(f'New gameId found: {r.json()["gameId"]}')
                request.app.active_match = data_transformations.response_to_active_match(request, r)

                for participant in request.app.active_match.participants:
                    r2 = request.app.mastery_handler.try_request(headers={'X-Riot-Token': request.app.riot_api_key},
                                                                 url_params={'': participant.summoner.puu_id,
                                                                             'championId': participant.champion})

                    if r2 and r2.status_code == 200:
                        participant.mastery_points = r2.json()['championPoints']
                    else:
                        participant.mastery_points = 0
                        logging.warning(f'Unexpected response while calling RIOT mastery endpoint '
                                        f'"{participant.summoner.name}#{participant.summoner.tagline} - '
                                        f'{participant.champion}".')

                    try:
                        participant = db_utils.enhance_participant(participant, request.app.active_match.match_id)
                    except Exception as e:
                        logging.error(f'Error during adding tags to participant {participant.summoner.name}#'
                                      f'{participant.summoner.tagline} : {e}', exc_info=True)

                if save_match_to_db(request.app.active_match):
                    logging.info('Entire match succesfully saved to db.')
                else:
                    logging.warning(f'Something went wrong with saving to db.')
                    request.app.active_match.match_id = None
    elif r.status_code == 404:
        logging.info(f'No active match.')
        raise HTTPException(status_code=204)
    else:
        logging.error(f'Unexpected return code from RIOT API: {r.status_code}')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=500)

    logging.info(f'Returning active match: {request.app.active_match.model_dump_json()}')
    return request.app.active_match


@router.get('/match_detail/{match_id}', status_code=200, response_model=data_models.Match)
async def root(match_id: int, request: Request, response: Response) -> object:
    """
    Returns detail of the match, needs to store everything interesting in the database.
    """
    logging.debug('Received GET /match/match_detail')

    r = request.app.match_handler.try_request(headers={'X-Riot-Token': request.app.riot_api_key},
                                              url_params={'': match_id})
    if r is None:
        logging.error('Unexpected error during processing of GET /match/active_match!')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=500)

    if r.status_code == 200:
        save = False
        match = data_transformations.response_to_match_detail(request, r)
        for participant in match.participants:
            try:
                if participant.summoner.puu_id == request.app.my_summoner.puu_id:
                    save = True
                participant = db_utils.enhance_participant(participant,
                                                           r.json()['metadata']['matchId'].split('_')[1])
            except Exception as e:
                logging.error(f'Error during adding tags to participant {participant.summoner.name}#'
                              f'{participant.summoner.tagline} : {e}', exc_info=True)
        if save:
            if save_match_to_db(match):
                logging.info('Entire match succesfully saved to db')
            else:
                logging.warning('Something went wrong with db save.')

        logging.debug(f'Returning detail: {match.model_dump_json()}')
        return match
    else:
        logging.error(f'Unexpected return code from RIOT API: {r.status_code}')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=500)


@router.get('/match_timeline/{match_id}', status_code=200)
async def root(match_id: int, request: Request, response: Response) -> object:
    """
    Saves timeline to database.
    """
    logging.debug('Received GET /match/match_timeline')

    r = request.app.match_handler.try_request(headers={'X-Riot-Token': request.app.riot_api_key},
                                              url_params={'': match_id,
                                                          'timeline': True})
    if r is None:
        logging.error('Unexpected error during processing of GET /match/active_match!')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=500)

    if r.status_code == 200:
        logging.info('Timeline successfully aquired.')
    else:
        logging.error(f'Unexpected return code from RIOT API: {r.status_code}')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=500)

    return r.json()
