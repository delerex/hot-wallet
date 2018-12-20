import functools
import json
import logging

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from models.errors import RequestError

RESPONSE_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Accept,Authorization,Cache-Control,Content-Type,DNT,If-Modified-Since,"
                                    "Keep-Alive,Origin,User-Agent,X-Requested-With"
}


app_log = logging.getLogger(__name__)


async def error_handling_middleware(app, handler):
    @functools.wraps(handler)
    async def middleware(request, *args, **kwargs):
        try:
            response = await handler(request, *args, **kwargs)
            if isinstance(response, dict):
                return web.json_response(response, headers=RESPONSE_HEADERS)
            return response
        except RequestError as ex:
            return web.json_response({
                "error": ex.message,
                "result": None,
            })
        except web.HTTPException as ex:
            return web.json_response({
                "error": {
                    "code": str(ex.status),
                    "message": "",
                    "data": {}
                }
            }, headers=RESPONSE_HEADERS, status=ex.status_code)
        except Exception as ex:
            app_log.exception("UnexpectedError: {}".format(ex), exc_info=True, extra={
                "tags": {
                    "module": handler.__module__,
                    "url": request.url
                }
            })
            return web.json_response({
                "error": {
                    "code": "API_UnexpectedError",
                    "message": "Something went wrong",
                    "data": {}
                }
            }, headers=RESPONSE_HEADERS, status=500)

    return middleware


async def cors_middleware(app, handler):
    @functools.wraps(handler)
    async def middleware(request: Request, *args, **kwargs):
        if request.method == 'OPTIONS':
            return Response(status=200, headers=RESPONSE_HEADERS)
        return await handler(request, *args, **kwargs)

    return middleware


async def request_and_auth_data_middleware(app, handler):
    @functools.wraps(handler)
    async def middleware(request, *args, **kwargs):
        request.all_data = {k: request.rel_url.query.getone(k) for k in request.rel_url.query.keys()}

        request.body_text = None
        if request.can_read_body:
            try:
                request.body_text = await request.text()
                try:
                    body = json.loads(request.body_text)
                    request.all_data.update(body)
                except Exception:
                    print("Invalid body: {}".format(request.body_text))
            except:
                pass

        request.all_data.update(request.match_info)
        request.all_data.update(request.headers)

        request.is_authenticated = False
        request.user = None

        return await handler(request, *args, **kwargs)

    return middleware
