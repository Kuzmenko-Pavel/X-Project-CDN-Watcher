from aiohttp import web
import os
import mimetypes
import datetime


class ApiFileStorageView(web.View):

    async def post(self):
        store_directory = self.request.app['config']['store_directory']
        tail = self.request.match_info['tail']
        path = os.path.join(store_directory, tail)
        path_name = os.path.basename(path)
        directory = os.path.dirname(path)
        reader = await self.request.multipart()
        file = await reader.next()
        size = 0
        if not self.request.app['ls'].get(directory, False):
            os.makedirs(directory, exist_ok=True)
            self.request.app['ls'][directory] = True
        with open(path, 'wb') as f:
            while True:
                chunk = await file.read_chunk()  # 8192 bytes by default.
                if not chunk:
                    break
                size += len(chunk)
                f.write(chunk)

            return web.Response(text='{} sized of {} successfully stored'
                                     ''.format(path_name, size))