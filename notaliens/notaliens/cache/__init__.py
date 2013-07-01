from dogpile.cache import CacheRegion
from dogpile.cache.api import NO_VALUE
from pyramid.settings import asbool
from datetime import datetime
from functools import wraps
from hashlib import sha1
from uuid import uuid4

import inspect
import json
import logging
import hashlib

logger = logging.getLogger(__name__)


class SafeCacheRegion(CacheRegion):
    """ This is a cache region that will be very good about not crashing
    even if the cache service has completely went away
    """
    enabled = False

    def __init__(self, *args, **kwargs):

        self.ignore_exceptions = kwargs.pop('ignore_exceptions', True)

        super(SafeCacheRegion, self).__init__(*args, **kwargs)

    def get(self, *args, **kwargs):
        if not self.enabled:
            return NO_VALUE

        try:
            return super(SafeCacheRegion, self).get(*args, **kwargs)
        except Exception:
            if not self.ignore_exceptions:
                raise

            logger.exception("%s.get() failed, ignoring" %
                             self.__class__.__name__)

            return NO_VALUE

    def set(self, *args, **kwargs):
        if not self.enabled:
            return

        try:
            return super(SafeCacheRegion, self).set(*args, **kwargs)
        except Exception:
            if not self.ignore_exceptions:
                raise
            logger.exception("%s.set() failed, ignoring" %
                             self.__class__.__name__)

    def delete(self, *args, **kwargs):
        if not self.enabled:
            return

        try:
            return super(SafeCacheRegion, self).delete(*args, **kwargs)
        except Exception:
            if not self.ignore_exceptions:
                raise
            logger.exception("%s.delete() failed, ignoring" %
                             self.__class__.__name__)

    def get_or_create(self, *args, **kwargs):
        creator = args[1]

        if not self.enabled:
            return creator()

        try:
            return super(SafeCacheRegion, self).get_or_create(*args, **kwargs)
        except Exception:
            if not self.ignore_exceptions:
                raise

            logger.exception("%s.get_or_create() failed, ignoring" %
                             self.__class__.__name__)
            return creator()

    def is_alive(self):
        if self.enabled:
            super(SafeCacheRegion, self).set('__app_status_ping', 1)

            return True

        return False
    

def md5_key_mangler(key):
    """Receive cache keys as long concatenated strings;
    distill them into an md5 hash.

    """
    d = hashlib.md5(key.encode('utf-8'))
    return d.hexdigest()


# create the cache region before importing from models, they will need it.
cache_region = SafeCacheRegion()
sql_cache_region = SafeCacheRegion(key_mangler=md5_key_mangler)

regions = {
    "default": cache_region
    , "sql": sql_cache_region
}


def get_cache_settings(request, prefix='cache.'):
    """
    This will construct a dictionary of cache settings from an ini
    file and convert them to their proper type (bool, int, etc)
    """
    settings = request.registry.settings

    options = dict(
        (key[len(prefix):], settings[key])
        for key in settings if key.startswith(prefix)
    )

    config_mappings = [
        (asbool, ['enabled']),
        (int, ['expiration_time'])
    ]

    for converter, keys in config_mappings:
        for key in keys:
            if key in options:
                options[key] = converter(options[key])

    return options


def invalidate_group(group_key):
    """ This will invalidate a whole group of cache keys
    """
    logger.debug("invalidate cache_group=%s", group_key)

    group_key_value = cache_region.get(group_key)

    if group_key_value is not NO_VALUE:
        cache_region.set(group_key, str(uuid4()))


def cacheable(cache_group=None, namespace=None, expiration_time=None,
        should_cache_fn=None):
    """
    Return the decorated function's cached data. If the function's data is not
    cached, cache it after having called the decorated function.
    """

    cache_group_is_callable = callable(cache_group)
    expiration_time_is_callable = callable(expiration_time)

    def decorator(func):
        # Check if we're decorating a method (on a class) or a plain function.
        func_args = inspect.getargspec(func)
        has_self = func_args[0] and func_args[0][0] in ('self', 'cls')
        if has_self:
            # remove self/cls, like ``some_list[1:]``
            args_slice = slice(1, None)
        else:
            # like ``some_list[:]``
            args_slice = slice(None, None)

        def json_obj_handler(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()

        @wraps(func)
        def cacher(*args, **kwargs):
            if cache_group:
                if cache_group_is_callable:
                    cgroup = cache_group(*args, **kwargs)
                else:
                    cgroup = cache_group
            else:
                cgroup = None

            timeout = expiration_time() if expiration_time_is_callable \
                                        else expiration_time

            args_keys = json.dumps(
                args[args_slice],
                sort_keys=True,
                default=json_obj_handler
            )

            kwargs_keys = json.dumps(
                kwargs,
                sort_keys=True,
                default=json_obj_handler
            )

            arg_hash = sha1(args_keys.encode('ascii'))
            arg_hash.update(kwargs_keys.encode('ascii'))

            if has_self:
                func_key = "%(module)s.%(class)s.%(method)s(%(arg_hash)s)" % {
                    "module": func.__module__,
                    "class": args[0].__class__.__name__,
                    "method": func.__name__,
                    "arg_hash": arg_hash.hexdigest()
                }
            else:
                func_key = "%(module)s.%(func)s(%(arg_hash)s)" % {
                    "module": func.__module__,
                    "func": func.__name__,
                    "arg_hash": arg_hash.hexdigest()
                }

            if namespace:
                func_key = "%s_%s" % (func_key, namespace)

            @wraps(func)
            def call_function():
                logger.debug("generate cache for key=%s", func_key)
                return func(*args, **kwargs)

            if cgroup:
                group_key_value = cache_region.get(cgroup)

                if group_key_value is NO_VALUE:
                    group_key_value = str(uuid4())

                func_key = "%s_group_%s" % (func_key, group_key_value)

                # The set gets pickled, better than JSON because set are not
                # JSON serializable.
                logger.debug(
                    "cache store key=%s under cache_group=%s",
                    func_key,
                    cgroup
                )

                # we want to set group key after the func_key cache
                # so that the group key will be expired AFTER the func_key
                output = cache_region.get_or_create(
                    func_key
                    , call_function
                    , timeout
                    , should_cache_fn
                )

                cache_region.set(cache_group, group_key_value)
            else:
                output = cache_region.get_or_create(
                    func_key
                    , call_function
                    , timeout
                    , should_cache_fn
                )

            return output

        return cacher

    return decorator


def includeme(config):
    if cache_region.enabled:
        return

    settings = config.registry.settings

    cache_enabled = asbool(settings.get('cache.enabled', False))
    logger.info('dogpile_cache_enabled=%s' % cache_enabled)


    # Enable caching?
    if not cache_enabled:
        config.add_request_method(
            lambda request: {'enabled': False}, 'cache_settings', reify=True
        )
        return

    for key, region in regions.items():
        region.enabled = cache_enabled
        region.configure_from_config(settings, 'cache.')

    # Create a request.cache_settings object that views can use to inspect
    # what is going on with the cache
    config.add_request_method(get_cache_settings, 'cache_settings', reify=True)
