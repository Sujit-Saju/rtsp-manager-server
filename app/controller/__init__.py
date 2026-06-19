from app.controller.stream_controller import StreamController


def register_all(app):
    """Register every controller blueprint onto the Quart app."""
    for ctrl_cls in [
        StreamController,
    ]:
        app.register_blueprint(ctrl_cls.blueprint())
