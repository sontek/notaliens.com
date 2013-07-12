from pyramid.events import BeforeRender


def includeme(config):
    config.include('notaliens.sites.routes')

    config.add_subscriber(
        'notaliens.sites.events.add_renderers',
        BeforeRender
    )
