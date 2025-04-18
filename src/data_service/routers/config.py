import common.data_models as data_models
import common.db as db
import logging
import time
from fastapi import APIRouter, Request, Response, status, HTTPException

router = APIRouter()


@router.get('/summoner', status_code=200, response_model=data_models.Summoner)
async def root(request: Request) -> object:
    """
    Returns the current user summoner.
    """
    logging.debug('Received GET /config/summoner')
    return request.app.my_summoner


@router.post('/summoner', status_code=200, response_model=data_models.Summoner)
async def root(request: Request, response: Response, name: str, tagline: str = 'EUW') -> object:
    """
    Changes current users summoner.
    """
    logging.debug(f'Received POST on /config/summoner with summoner "{name}#{tagline}".')
    r = request.app.account_info_handler.try_request(headers={'X-Riot-Token': request.app.riot_api_key},
                                                     url_params={'gamename': name,
                                                                 'tagline': tagline})
    if r is None:
        logging.error('Unexpected error during processing of GET /config/summoner')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=500)

    if r.status_code == 200:
        if db.set_user(r.json()['gameName'],
                       r.json()['tagLine'],
                       r.json()['puuid'],
                       request.app.SERVER.id):

            request.app.my_summoner = db.get_user()
            logging.info(f'Users summoner successfully set to {request.app.my_summoner.name}#'
                         f'{request.app.my_summoner.tagline}.')
        else:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            raise HTTPException(status_code=500)
    elif r.status_code == 403:
        logging.warning(f'Incorrect RIOT API key.')
        response.status_code = status.HTTP_403_FORBIDDEN
        raise HTTPException(status_code=403)
    elif r.status_code == 404:
        logging.warning(f'RIOT did not confirm existence of summoner "{name}#{tagline}".')
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

    return request.app.my_summoner


@router.get('/riot_api_key', status_code=200)
async def root(request: Request) -> object:
    """
    Returns the RIOT API key the app uses.
    """
    logging.debug('Received GET /config/riot_api_key')
    return {'riot_api_key': request.app.riot_api_key}


@router.post('/riot_api_key', status_code=200)
async def root(request: Request, response: Response, riot_api_key: str) -> object:
    """
    Changes the RIOT API key the app uses.
    """
    logging.debug(f'Received POST on /config/riot_api_key with api_key: {riot_api_key}.')

    r = request.app.rotation_handler.try_request(headers={'X-Riot-Token': riot_api_key})
    if r is None:
        logging.error('Unexpected error during processing of GET /config/riot_api_key')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=500)

    if r.status_code == 200:
        try:
            db.set_setting('riot_api_key', riot_api_key)
            request.app.riot_api_key = riot_api_key
            logging.info(f'RIOT API key successfully set to {request.app.riot_api_key}.')
        except Exception as e:
            logging.error(f'Error during saving of RIOT API key: {e}', exc_info=True)
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            raise HTTPException(status_code=500)
    elif r.status_code == 403:
        logging.warning(f'Incorrect RIOT API key.')
        response.status_code = status.HTTP_403_FORBIDDEN
        raise HTTPException(status_code=403)
    elif r.status_code == 503:
        logging.warning(f'RIOT service was unavailable!.')
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        raise HTTPException(status_code=503)
    else:
        logging.error(f'Unexpected return code from RIOT API: {r.status_code}')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=500)

    return request.app.riot_api_key


@router.get('/ddragon_version', status_code=200)
async def root(request: Request) -> object:
    """
    Returns version of the ddragon data.
    """
    logging.debug('Received GET /config/ddragon_version')
    return {'ddragon_version': request.app.ddragon_version}


@router.post('/ddragon_version', status_code=200)
async def root(request: Request, response: Response, ddragon_version: str) -> object:
    """
    Changes the version of ddragon version data saved.
    """
    logging.debug(f'Received POST on /config/ddragon_version with ddragon_version: {ddragon_version}.')

    attempts = 0
    while attempts < 5:
        if db.set_setting('ddragon_version', ddragon_version):
            request.app.ddragon_version = ddragon_version
            logging.info(f'Ddragon version successfully set to {request.app.ddragon_version}.')
            return request.app.ddragon_version
        else:
            attempts += 1
            logging.warning(f'Attempt number {attempts} to change ddragon version failed...')
            time.sleep(5)

    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    logging.error(f'Ddragon version {ddragon_version} wasn\'t saved, kept version {request.app.ddragon_version}')
    raise HTTPException(status_code=500)
