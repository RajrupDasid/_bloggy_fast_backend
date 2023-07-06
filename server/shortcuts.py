from server import config
from cassandra.cqlengine.query import (DoesNotExist, MultipleObjectsReturned)
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

settings = config.get_settings()


def get_object_or_404(KlassName, **kwargs):
    obj = None
    try:
        obj = KlassName.objects.get(**kwargs)
    except DoesNotExist:
        raise StarletteHTTPException(status_code=404)
    except MultipleObjectsReturned:
        raise StarletteHTTPException(status_code=400)
    except:
        raise StarletteHTTPException(status_code=500)
    return obj


def redirect(path, cookies:dict={}, remove_session=False):
    response = RedirectResponse(path, status_code=302)
    for k, v in cookies.items():
        response.set_cookie(key=k, value=v, httponly=True)
    if remove_session:
        response.set_cookie(key='session_ended', value=1, httponly=True)
        response.delete_cookie('session_id')
    return response


