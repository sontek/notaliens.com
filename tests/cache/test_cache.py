from datetime import datetime
import unittest

import mock
from pyramid import testing
from webtest import TestApp

try:
    from imp import reload
except ImportError:
    pass


# We're going to monkey patch this into dogpile.cache.CacheRegion
class CacheRegion(object):
    def __init__(self, *args, **kwargs):
        self.cache = {}

    def get(self, key):
        if key in self.cache:
            return self.cache[key]

    def set(self, key, value):
        self.cache[key] = value

    def get_or_create(self, key, creator, *kwargs):
        val = self.get(key)

        if not val:
            val = creator()
            self.cache[key] = val

            return val

        return val

    def configure_from_config(self, settings, prefix):
        pass


class TestCacheableDecorator(unittest.TestCase):
    def setUp(self):
        import sys
        from dogpile.cache import api

        def view_func(request):
            return request.cache_settings

        config = testing.setUp()
        config.registry.settings['cache.enabled'] = True

        self.dogpile_cache_module = mock.Mock()
        self.dogpile_cache_module.api = api
        self.dogpile_cache_module.CacheRegion = CacheRegion
        sys.modules['dogpile.cache'] = self.dogpile_cache_module

        # Force reload of notaliens.cache so that it picks up mocked
        # dogpile.cache
        import notaliens.cache
        reload(notaliens.cache)

        config.include("notaliens.cache")

        config.add_route('view', '/view')
        config.add_view(view_func, route_name='view', renderer='json')
        app = config.make_wsgi_app()
        self.app = TestApp(app)

        from notaliens.cache import cacheable, invalidate_group
        self.invalidate_group = invalidate_group

        class SomeClass(object):
            # `self.counter` exists to detect side effects of `func` being
            # called
            def __init__(self):
                self.counter = 0

            @cacheable('group1')
            def func(self, x, y):
                self.counter += 1
                return self.counter

        self.SomeClass = SomeClass

        counter_dict = {'counter': 0}

        @cacheable()
        def func(x, y):
            counter_dict['counter'] += 1
            return counter_dict['counter']

        self.func = func

    def test_cacheable_method_enabled_cache_group(self):
        obj = self.SomeClass()

        #
        # First time we call obj.func, we simulate nothing in cache yet so
        # creator_func gets called
        #

        ret = obj.func(3, 5)
        self.assertEquals(ret, 1)

        ret = obj.func(3, 5)
        self.assertEquals(ret, 1)

        self.assertEquals(obj.counter, 1)

        #
        # Then simulate invalidating a cache group
        #

        self.invalidate_group('group1')

        ret = obj.func(3, 5)
        self.assertEquals(ret, 2)

    def test_cacheable_function(self):
        ret = self.func(3, datetime(year=2013, month=5, day=10))
        self.assertEquals(ret, 1)

    def test_get_cache_settings(self):
        ret = self.app.get('/view')
        self.assertEqual(ret.json_body['enabled'], True)

    def test_include_cache_not_enabled(self):
        config = testing.setUp()
        config.registry.settings['cache.enable'] = False

        with mock.patch('notaliens.cache.cache_region') as mock_cache_region:
            mock_cache_region.enabled = False
            config.include('notaliens.cache')

    def test_include_twice(self):
        config = testing.setUp()
        config.include('notaliens.cache')
        config.include('notaliens.cache')
