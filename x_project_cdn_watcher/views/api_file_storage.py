from aiohttp import web
import os
import mimetypes
import datetime


class ApiFileStorageView(web.View):

    async def file_create(self, path, file):
        size = 0
        with open(path, 'wb') as f:
            while True:
                chunk = await file.read_chunk()  # 8192 bytes by default.
                if not chunk:
                    break
                size += len(chunk)
                f.write(chunk)
        return size

    async def get(self):
        return web.json_response()

    async def head(self):
        return web.json_response()

    async def post(self):
        store_directory = self.request.app['config']['store_directory']
        tail = self.request.match_info['tail']
        reader = await self.request.multipart()
        file = await reader.next()
        path = os.path.join(store_directory, tail)
        path_name = os.path.basename(path)
        directory = os.path.dirname(path)
        size = 0
        if not self.request.app['ls'].get(directory, False):
            os.makedirs(directory, exist_ok=True)
            self.request.app['ls'][directory] = True
        try:
            size = await self.file_create(path, file)
        except IOError as e:
            os.makedirs(directory, exist_ok=True)
            size = await self.file_create(path, file)
        if size > 0:
            return web.Response(text='{} sized of {} successfully stored'
                                     ''.format(path_name, size), status=200)
        else:
            return web.Response(text='{} sized of {} fail stored'
                                     ''.format(path_name, size), status=500)

    async def put(self):
        return await self.post()

    async def delete(self):
        store_directory = self.request.app['config']['store_directory']
        tail = self.request.match_info['tail']
        path = os.path.join(store_directory, tail)
        path_name = os.path.basename(path)
        try:
            os.remove(path)
        except IOError:
            pass
        return web.json_response(text='{} successfully deleted'.format(path_name))