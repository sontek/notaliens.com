from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig

import os

here = os.path.dirname(__file__)

def setup_includes(config):
    config.include('notaliens.cache')
    config.include('notaliens.log')
    config.include('notaliens.core')
    config.include('notaliens.search')
    config.include('notaliens.people', route_prefix='/people')
    config.include('notaliens.sites', route_prefix='/sites')
    config.include('notaliens.jobs', route_prefix='/jobs')
    config.include('notaliens.identity', route_prefix='/identity')
    config.include('notaliens.sites', route_prefix='/sites')
    config.include('notaliens.geoip')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')

    config = Configurator(
        settings=settings,
        session_factory=session_factory
    )

    config.registry['phantomjs_path'] = os.path.join(
        here,
        '../../bin/phantomjs'
    )

    config.registry['phantomjs_script'] = os.path.join(
        here,
        '../screenshot.js'
    )

    config.registry['screenshots_folder'] = os.path.join(
        here,
        'static/screenshots'
    )

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('static_deform', 'deform:static')
    config.add_static_view('static_deform_bootstrap',
        'deform_bootstrap:static')


    setup_includes(config)

    config.scan()

    return config.make_wsgi_app()
