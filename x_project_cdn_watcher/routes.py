from .views import ApiFileStorageView


def setup_routes(app):
    app.router.add_static('/test_static', './static', show_index=True)
    # app.router.add_route('GET', '/{tail:.*}', ApiView)
    # app.router.add_route('HEAD', '/{tail:.*}', ApiView)
    # app.router.add_route('POST', '/{tail:.*}', ApiView)
    # app.router.add_route('PUT', '/{tail:.*}', ApiView)
    # app.router.add_route('DELETE', '/{tail:.*}', ApiView)
    app.router.add_route('POST', '/{tail:.*}', ApiFileStorageView)
