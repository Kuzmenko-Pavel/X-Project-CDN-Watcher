from motor import motor_asyncio as ma


def init_db(app):
    conf = app['config']['mongo']
    app.client = ma.AsyncIOMotorClient(conf['uri'])
    app.db = app.client[conf['db']]
    app.block = app.db[conf['collection']['block']]
    app.offer = app.db[conf['collection']['offer']]
