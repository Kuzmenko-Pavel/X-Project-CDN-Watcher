from aiohttp import web
import gridfs
import mimetypes
import datetime


class ApiView(web.View):
    async def get(self):
        # If you pass in a dict it will be automatically converted to JSON
        # msg = asynqp.Message({'hello': 'world'})
        # self.request.app.exchange.publish(msg, 'routing.key')
        file_id = self.request.match_info['tail']
        try:
            grid_out = await self.request.app.fs.open_download_stream_by_name(file_id)
        except gridfs.NoFile:
            raise web.HTTPNotFound(text=self.request.path)
        else:
            resp = web.StreamResponse()
            self._set_standard_headers(self.request.path, resp, grid_out)
            ims_value = self.request.if_modified_since
            if ims_value is not None:
                # If our MotorClient is tz-aware, assume the naive ims_value is in
                # its time zone.
                if_since = ims_value.replace(tzinfo=grid_out.upload_date.tzinfo)
                modified = grid_out.upload_date.replace(microsecond=0)
                if if_since >= modified:
                    resp.set_status(304)
                    return resp

            # Same for Etag
            etag = self.request.headers.get("If-None-Match")
            if etag is not None and etag.strip('"') == grid_out.md5:
                resp.set_status(304)
                return resp

            resp.content_length = grid_out.length
            await resp.prepare(self.request)
            resp.set_tcp_cork(True)
            try:
                written = 0
                while written < grid_out.length:
                    # Reading chunk_size at a time minimizes buffering.
                    chunk = await grid_out.read(grid_out.chunk_size)
                    resp.write(chunk)
                    await resp.drain()
                    written += len(chunk)
            finally:
                resp.set_tcp_nodelay(True)

            return resp

    async def head(self):
        # If you pass in a dict it will be automatically converted to JSON
        # msg = asynqp.Message({'hello': 'world'})
        # self.request.app.exchange.publish(msg, 'routing.key')
        return web.json_response(text="Hello, {}".format(self.request.match_info['tail']))

    async def post(self):
        data = await self.request.post()
        file = data.get('file')
        file_id = None
        if file is not None:
            file_id = await self.request.app.fs.upload_from_stream(
                self.request.match_info['tail'],
                file.file,
                metadata={"contentType": file.content_type})
        return web.json_response(text="{}".format(file_id))

    async def put(self):
        data = await self.request.post()
        file = data.get('file')
        return web.json_response(text="Hello, {}".format(self.request.match_info['tail']))

    async def delete(self):
        data = await self.request.post()
        print(data)
        return web.json_response(text="Hello, {}".format(self.request.match_info['tail']))

    def _set_standard_headers(self, path, resp, gridout):
        resp.last_modified = gridout.upload_date
        content_type = gridout.content_type
        if content_type is None:
            content_type, encoding = mimetypes.guess_type(path)

        if content_type:
            resp.content_type = content_type

        # MD5 is calculated on the MongoDB server when GridFS file is created.
        resp.headers["Etag"] = '"%s"' % gridout.md5

        # Overridable method get_cache_time.
        cache_time = self._get_cache_time(path,
                                          gridout.upload_date,
                                          gridout.content_type)

        if cache_time > 0:
            resp.headers["Expires"] = (
                datetime.datetime.utcnow() +
                datetime.timedelta(seconds=cache_time)
            ).strftime("%a, %d %b %Y %H:%M:%S GMT")

            resp.headers["Cache-Control"] = "max-age=" + str(cache_time)
        else:
            resp.headers["Cache-Control"] = "public"

    def _get_cache_time(self, filename, modified, mime_type):
        """Override to customize cache control behavior.
    
        Return a positive number of seconds to trigger aggressive caching or 0
        to mark resource as cacheable, only. 0 is the default.
    
        For example, to allow image caching::
    
            def image_cache_time(filename, modified, mime_type):
                if mime_type.startswith('image/'):
                    return 3600
    
                return 0
    
            client = AsyncIOMotorClient()
            gridfs_handler = AIOHTTPGridFS(client.my_database,
                                           get_cache_time=image_cache_time)
    
        :Parameters:
          - `filename`: A string, the URL portion matching {filename} in the URL
            pattern
          - `modified`: A datetime, when the matching GridFS file was created
          - `mime_type`: The file's type, a string like "application/octet-stream"
        """
        return 0