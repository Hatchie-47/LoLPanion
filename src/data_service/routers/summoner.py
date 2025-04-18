import common.data_models as data_models
import common.db_utils as db_utils
import logging
import datetime
from fastapi import APIRouter, Request, Response, status, HTTPException

router = APIRouter()


@router.get('/by-puuid/{puu_id}', status_code=200, response_model=data_models.Summoner)
async def root(puu_id: str, request: Request, response: Response) -> object:
    """
    Returns summoner details based on puu id.
    """
    logging.debug('Received GET /summoner/by-puuid')

    r = request.app.account_info_handler.try_request(headers={'X-Riot-Token': request.app.riot_api_key},
                                                     url_params={'puu_id': puu_id})

    r2 = request.app.player_info_handler.try_request(headers={'X-Riot-Token': request.app.riot_api_key},
                                                     url_params={'puu_id': puu_id})

    if r is None or r2 is None:
        logging.error('Unexpected error during processing of GET /summoner/by-puu_id')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=500)

    status_code = max(r.status_code, r2.status_code)

    if status_code == 200:
        summoner = data_models.Summoner(
            puu_id=r.json()['puuid'],
            name=r.json()['gameName'],
            tagline=r.json()['tagLine'],
            server=request.app.SERVER,
            profile_icon=r2.json()['profileIconId'],
            revision_date=datetime.datetime.fromtimestamp(r2.json()['revisionDate'] / 1000),
            summoner_level=r2.json()['summonerLevel']
        )

        try:
            summoner = db_utils.enhance_summoner(summoner)
        except Exception as e:
            logging.error(f'Error during adding tags to participant {summoner.name}#{summoner.tagline} : {e}',
                          exc_info=True)
    elif r.status_code == 403:
        logging.warning(f'Incorrect RIOT API key.')
        response.status_code = status.HTTP_403_FORBIDDEN
        raise HTTPException(status_code=403)
    elif r.status_code == 404:
        logging.warning(f'RIOT did not confirm existence of summoner with puu id: {puu_id}')
        response.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=404)
    elif r.status_code == 503:
        logging.warning(f'RIOT service was unavailable!.')
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        raise HTTPException(status_code=503)
    else:
        logging.error(f'Unexpected return code from RIOT API: {r.status_code}')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=500)

    return summoner


@router.get('/match_history/{puu_id}', status_code=200)
async def root(puu_id: str, request: Request, response: Response) -> object:
    """
    Returns match history for given summoner.
    """
    logging.debug('Received GET /summoner/match_history')

    r = request.app.match_handler.try_request(headers={'X-Riot-Token': request.app.riot_api_key},
                                              url_params={'puu_id': puu_id, 'type': 'ranked'})

    if r is None:
        logging.error('Unexpected error during processing of GET /config/summoner')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=500)

    if r.status_code == 200:
        matches = r.json()
    else:
        logging.error(f'Unexpected return code from RIOT API: {r.status_code}')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=500)

    return matches
