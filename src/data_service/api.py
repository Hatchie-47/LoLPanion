import common.data_models as data_models
import common.logging_objects
import os
import uvicorn
import handlers
import logging
import common.db as db
from routers import match, config, summoner, tag
from fastapi import FastAPI

app = FastAPI()

app.include_router(match.router, prefix='/match')
app.include_router(config.router, prefix='/config')
app.include_router(summoner.router, prefix='/summoner')
app.include_router(tag.router, prefix='/tag')

app.riot_api_key = db.get_setting('riot_api_key')
app.ddragon_version = db.get_setting('ddragon_version')
app.SERVER = data_models.Server(id=1, cluster='europe', server='euw1')
app.ROLE = {
    'TOP': data_models.Role(id=1, name='TOP'),
    'JUNGLE': data_models.Role(id=2, name='JUNGLE'),
    'MIDDLE': data_models.Role(id=3, name='MID'),
    'BOTTOM': data_models.Role(id=4, name='BOT'),
    'UTILITY': data_models.Role(id=5, name='SUPPORT'),
    'Invalid': data_models.Role(id=6, name='UNKNOWN')
}

app.account_info_handler = handlers.RIOTAccountHandler(server=app.SERVER)
app.player_info_handler = handlers.RIOTPlayerHandler(server=app.SERVER)
app.active_match_handler = handlers.RIOTActiveMatchHandler(server=app.SERVER)
app.match_handler = handlers.RIOTMatchHandler(server=app.SERVER)
app.mastery_handler = handlers.RIOTMasteryHandler(server=app.SERVER)
app.rotation_handler = handlers.RIOTChampionRotation(server=app.SERVER)

# app.my_server = None
app.my_summoner = db.get_user()
app.active_match = data_models.Match(
    server=app.SERVER
)


@app.get('/healthcheck', status_code=200)
async def healthcheck():
    """
    Used for checking health of service.
    """
    logging.info('Responding to GET /healthcheck')
    return 1


def main() -> None:
    """
    Starts the FastAPI server.
    """
    uvicorn.run('api:app', host='0.0.0.0', port=4701, log_config=os.path.join(os.path.dirname(
        os.path.abspath(common.logging_objects.__file__)), 'logging.yml'), reload=False)
