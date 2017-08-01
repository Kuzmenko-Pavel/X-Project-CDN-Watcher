from .views import ApiView


def setup_routes(app):
    app.router.add_route('GET', '/', ApiView)
    app.router.add_route('POST', '/', ApiView)
    app.router.add_route('PUT', '/', ApiView)
    app.router.add_route('DELETE', '/', ApiView)
