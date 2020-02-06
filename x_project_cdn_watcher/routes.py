from .views import ApiFileStorageView


def setup_routes(app):
    app.router.add_route('*', '/{tail:.*}', ApiFileStorageView)
