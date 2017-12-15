from aiohttp import web
import mimetypes
import datetime


class ApiView(web.View):
    async def get(self):
        # If you pass in a dict it will be automatically converted to JSON
        # msg = asynqp.Message({'hello': 'world'})
        # self.request.app.exchange.publish(msg, 'routing.key')
        grid_out, resp = await self._head()
        if resp.status == 304:
            return resp
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

    async def _head(self):
        file_id = self.request.match_info['tail']
        grid_out = await self.request.app.fs.open_download_stream_by_name(file_id)
        resp = web.StreamResponse()
        self._set_standard_headers(self.request.path, resp, grid_out)
        self._set_info_headers(resp, grid_out)
        ims_value = self.request.if_modified_since
        if ims_value is not None:
            # If our MotorClient is tz-aware, assume the naive ims_value is in
            # its time zone.
            if_since = ims_value.replace(tzinfo=grid_out.upload_date.tzinfo)
            modified = grid_out.upload_date.replace(microsecond=0)
            if if_since >= modified:
                resp.set_status(304)
                return grid_out, resp

        # Same for Etag
        etag = self.request.headers.get("If-None-Match")
        if etag is not None and etag.strip('"') == grid_out.md5:
            resp.set_status(304)
            return grid_out, resp

        resp.content_length = grid_out.length
        await resp.prepare(self.request)
        return grid_out, resp

    async def head(self):
        _, resp = await self._head()
        return resp

    async def post(self):
        data = await self.request.post()
        file = data.get('file')
        file_id = None
        if file is not None:
            file_id = await self.request.app.fs.upload_from_stream(
                self.request.match_info['tail'],
                file.file,
                metadata={"content_type": file.content_type})
        return web.json_response(text="{}".format(file_id))

    async def put(self):
        data = await self.request.post()
        file = data.get('file')
        return web.json_response(text="Hello, {}".format(self.request.match_info['tail']))

    async def delete(self):
        data = await self.request.post()
        print(data)
        return web.json_response(text="Hello, {}".format(self.request.match_info['tail']))

    def _set_standard_headers(self, path, resp, grid_out):
        upload_date = grid_out.upload_date
        content_type = grid_out.metadata.get('content_type')
        cache_time = grid_out.metadata.get('cache_time')
        md5 = grid_out.md5
        resp.last_modified = upload_date
        if content_type is None:
            content_type, encoding = mimetypes.guess_type(path)

        if content_type:
            resp.content_type = content_type

        resp.headers["Etag"] = '"%s"' % md5
        if not isinstance(cache_time, int):
            cache_time = self._get_cache_time(path,
                                              upload_date,
                                              content_type)

        if cache_time > 0:
            resp.headers["Expires"] = (
                datetime.datetime.utcnow() +
                datetime.timedelta(seconds=cache_time)
            ).strftime("%a, %d %b %Y %H:%M:%S GMT")

            resp.headers["Cache-Control"] = "max-age=%s public" % cache_time
        else:
            resp.headers["Expires"] = (
                datetime.datetime.utcnow() +
                datetime.timedelta(seconds=315360000)
            ).strftime("%a, %d %b %Y %H:%M:%S GMT")
            resp.headers["Cache-Control"] = "max-age=315360000 public"

    def _set_info_headers(self, resp, grid_out):
        pass

    def _get_cache_time(self, filename, modified, mime_type):
        if mime_type.startswith('image'):
            return 3600
        return 0
