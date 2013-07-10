import logging
from pyramid.settings import asbool
from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import InvalidJsonResponseError
from requests.exceptions import ConnectionError


logger = logging.getLogger(__name__)


class SafeEs(object):
    def __init__(self, es):
        self.es = es

    def create_index(self, index, descriptor, body, **kwargs):
        try:
            self.es.index(index, descriptor, body, **kwargs)
        except (InvalidJsonResponseError, ConnectionError):
            logger.exception("Couldn't index data to ElasticSearch")

    def delete_index(self, index):
        try:
            self.es.delete_index(index)
        except (InvalidJsonResponseError, ConnectionError):
            logger.exception("Couldn't delete index from ElasticSearch")

    def search(self, query, fallback=None, **kwargs):
        try:
            return self.es.search(query, **kwargs)
        except (InvalidJsonResponseError, ConnectionError):
            if fallback:
                logger.exception("Couldn't search from ElasticSearch")
                return fallback(query, **kwargs)
            else:
                logger.warn("No fallback registered")
                raise


def _get_search_settings(settings, prefix='search.'):
    options = dict(
        (key[len(prefix):], settings[key])
        for key in settings if key.startswith(prefix)
    )

    config_mappings = [
        (asbool, ['enabled']),
        (int, ['port'])
    ]

    for converter, keys in config_mappings:
        for key in keys:
            if key in options:
                options[key] = converter(options[key])

    return options


def get_search_settings(request, prefix='search.'):
    """
    This will construct a dictionary of cache settings from an ini
    file and convert them to their proper type (bool, int, etc)
    """
    settings = request.registry.settings

    return _get_search_settings(settings, prefix)


# we are making this global to take advantage of connection pooling
# in pyelasticsearch
_es_client = None


def includeme(config):
    settings = config.registry.settings

    search_enabled = asbool(settings.get('search.enabled', False))
    logger.info('elastic_search_enabled=%s' % search_enabled)

    # Enable searching?
    if not search_enabled:
        config.add_request_method(
            lambda request: {'enabled': False}, 'search_settings', reify=True
        )
        return

    search_settings = _get_search_settings(settings)

    global _es_client

    if _es_client is None:
        _es_client = ElasticSearch(
            'http://%(host)s:%(port)s/' % search_settings
        )

    config.add_request_method(
        get_search_settings,
        'search_settings',
        reify=True
    )

    config.add_request_method(
        lambda request: SafeEs(_es_client),
        'es',
        reify=True
    )
