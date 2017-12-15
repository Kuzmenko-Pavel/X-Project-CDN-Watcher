import asynqp


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