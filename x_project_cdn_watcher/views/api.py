from aiohttp import web
import asynqp


class ApiView(web.View):
    async def get(self):
        # If you pass in a dict it will be automatically converted to JSON
        # msg = asynqp.Message({'hello': 'world'})
        # self.request.app.exchange.publish(msg, 'routing.key')
        data = await self.request.post()
        file = data.get('file')
        print(file)
        if file is not None:
                print(file.file.read())
        return web.json_response(text="Hello, {}".format(self.request.match_info['tail']))

    async def head(self):
        # If you pass in a dict it will be automatically converted to JSON
        # msg = asynqp.Message({'hello': 'world'})
        # self.request.app.exchange.publish(msg, 'routing.key')
        data = await self.request.post()
        file = data.get('file')
        print(file)
        if file is not None:
                print(file.file.read())
        return web.json_response(text="Hello, {}".format(self.request.match_info['tail']))

    async def post(self):
        data = await self.request.post()
        file = data.get('file')
        print(file)
        if file is not None:
                print(file.file.read())
        return web.json_response(text="Hello, {}".format(self.request.match_info['tail']))

    async def put(self):
        data = await self.request.post()
        file = data.get('file')
        print(file)
        if file is not None:
                print(file.file.read())
        return web.json_response(text="Hello, {}".format(self.request.match_info['tail']))

    async def delete(self):
        data = await self.request.post()
        file = data.get('file')
        print(file)
        if file is not None:
                print(file.file.read())
        return web.json_response(text="Hello, {}".format(self.request.match_info['tail']))
