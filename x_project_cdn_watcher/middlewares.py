from aiohttp import hdrs, web
from aiohttp.web import middleware
import gridfs
import time
from datetime import datetime, timedelta

from x_project_cdn_watcher.logger import logger, exception_message


async def handle_404(request, response):
    return web.HTTPNotFound(text='')


async def handle_405(request, response):
    return web.Response(text='')


async def handle_500(request, response):
    return web.Response(text='')


def error_pages(overrides):
    async def middleware(app, handler):
        async def middleware_handler(request):
            try:
                try:
                    response = await handler(request)
                    override = overrides.get(response.status)
                    if override is None:
                        return response
                    else:
                        return await override(request, response)
                except gridfs.NoFile:
                    raise web.HTTPNotFound()
            except web.HTTPException as ex:
                if ex.status != 404:
                    logger.error(exception_message(exc=str(ex), request=str(request._message)))
                override = overrides.get(ex.status)
                if override is None:
                    raise
                else:
                    return await override(request, ex)

        return middleware_handler

    return middleware


@middleware
async def authentication_middlewares(request, handler):
    headers = request.headers
    token = request.app['config']['token']
    access_token = headers.get('X-Authentication', '')
    if token != access_token and request.method in ['POST', 'DELETE', 'PUT']:
        raise web.HTTPForbidden()
    if request.content_type != 'multipart/form-data' and request.method in ['POST', 'PUT']:
        raise web.HTTPForbidden()
    response = await handler(request)
    return response


def setup_middlewares(app):
    error_middleware = error_pages({404: handle_404,
                                    405: handle_405,
                                    500: handle_500})
    app.middlewares.append(authentication_middlewares)
    app.middlewares.append(error_middleware)
