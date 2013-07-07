from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig


def setup_includes(config):
    config.include('notaliens.cache')
    config.include('notaliens.log')
    config.include('notaliens.core')
    config.include('notaliens.search')
    config.include('notaliens.people', route_prefix='/people')
    config.include('notaliens.identity', route_prefix='/identity')

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')

    config = Configurator(
        settings=settings
        , session_factory=session_factory
    )

    config.add_static_view('static', 'static', cache_max_age=3600)

    setup_includes(config)

    config.scan()

    return config.make_wsgi_app()
