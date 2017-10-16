import argparse
import uvloop
import asyncio
import asynqp
import os
import sys

from aiohttp import web
from trafaret_config import commandline

from x_project_cdn_watcher.logger import logger, exception_message
from x_project_cdn_watcher.db import init_db
from x_project_cdn_watcher.middlewares import setup_middlewares
from x_project_cdn_watcher.routes import setup_routes
from x_project_cdn_watcher.utils import TRAFARET_CONF

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def ms(received_message):
    print(received_message.json())  # get JSON from incoming messages easily

    # Acknowledge a delivered message
    received_message.ack()

async def hello_world(app):
    """
    Sends a 'hello world' message and then reads it from the queue.
    """
    # connect to the RabbitMQ broker
    connection = await asynqp.connect('srv-4.yottos.com', 5672, username='old_worker', password='old_worker',
                                      virtual_host='/', loop=app.loop)

    # Open a communications channel
    channel = await connection.open_channel()

    # Create a queue and an exchange on the broker
    exchange = await channel.declare_exchange('test.exchange', 'direct')
    app.exchange = exchange
    queue = await channel.declare_queue('test.queue')

    # Bind the queue to the exchange, so the queue will get messages published to the exchange
    await queue.bind(exchange, 'routing.key')
    await queue.consume(ms)

    # Synchronously get a message from the queue
    #
    # await channel.close()
    # await connection.close()


async def start_background_listener(app):
    app['listener'] = app.loop.create_task(hello_world(app))


def init(loop, argv):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    ap = argparse.ArgumentParser(description='Great Description To Be Here')
    ap.add_argument('-s', "--socket", action='store', dest='socket', help='unix socket')
    commandline.standard_argparse_options(ap.add_argument_group('configuration'),
                                          default_config=dir_path + '/../conf.yaml')

    options = ap.parse_args(argv)
    config = commandline.config_from_options(options, TRAFARET_CONF)
    config['socket'] = options.socket
    app = web.Application(loop=loop)
    app['config'] = config
    app.on_startup.append(init_db)
    app.on_startup.append(start_background_listener)
    setup_routes(app)
    setup_middlewares(app)

    return app


def main(argv):
    loop = asyncio.get_event_loop()
    app = init(loop, argv)
    app['log'] = logger
    if app['config']['socket']:
        web.run_app(app, path=app['config']['socket'], backlog=1024, access_log=None)
    else:
        web.run_app(app, host=app['config']['host'], port=app['config']['port'], backlog=1024, access_log=None)


if __name__ == '__main__':
    main(sys.argv[1:])
