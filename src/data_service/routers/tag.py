import common.data_models as data_models
import common.db_utils as db_utils
import common.db as db
import logging
from fastapi import APIRouter, Request, Response, status, HTTPException

router = APIRouter()


@router.post('/add_tag', status_code=200, response_model=data_models.AssignedTag)
async def root(puu_id: str,
               match_id: str,
               tag: data_models.Tag,
               severity: data_models.Severity,
               note: str,
               request: Request,
               response: Response) -> object:
    """
    Adds tag to a participant of a match.
    """
    logging.debug(f'Received POST on /tag/add_tag.')

    if db.insert_tag(match_id,
                     request.app.SERVER.id,
                     puu_id,
                     db_utils.TAG[tag],
                     db_utils.SEVERITY[severity],
                     note):
        logging.info('Entire match successfully saved to db')
        return data_models.AssignedTag(tag=tag,
                                       severity=severity,
                                       note=note)
    else:
        logging.error('Something went wrong with db save.')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=500)
