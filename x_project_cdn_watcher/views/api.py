from aiohttp import web
import asynqp


class ApiView(web.View):
    async def get(self):
        # If you pass in a dict it will be automatically converted to JSON
        msg = asynqp.Message({'hello': 'world'})
        self.request.app.exchange.publish(msg, 'routing.key')
        return web.json_response({})

    async def post(self):
        return web.json_response({})

    async def put(self):
        return web.json_response({})

    async def delete(self):
        return web.json_response({})
