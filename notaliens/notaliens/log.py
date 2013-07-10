import inspect
import logging
import operator
import threading

from collections import Mapping
from functools import (
    partial,
    update_wrapper
)
from itertools import cycle
try:
    # Python 2
    from itertools import izip
except ImportError:  # pragma: no cover
    # Python 3
    izip = zip

from time import time
from uuid import uuid4

from pyramid.path import DottedNameResolver
from pyramid.settings import asbool
from pyramid.static import static_view

from colorama import init as colorama_init
from colorama import Fore

logger = logging.getLogger(__name__)

colorama_init()

log_namespace = __name__


def iterargs(*args, **kwargs):
    """
    Generator that yields given args and kwargs as strings.

    """
    for arg in args:
        yield "%r" % (arg, )

    for key, value in kwargs.items():
        yield "%s=%r" % (key, value)


def perflog(log_level='INFO'):
    """
    A decorator that logs the number of milliseconds it took for the underlying
    function to return. The default log level is INFO.

    """
    def decorator(func):  # pylint:disable=C0111
        def method_wrapper(*args, **kwargs):  # pylint:disable=C0111
            chrono = time()
            output = func(*args, **kwargs)
            chrono = time() - chrono

            # Make a nice formatting
            args_str = ", ".join(iterargs(*args, **kwargs))
            log(
                {
                    "chrono": chrono * 1000,
                    "module": func.__module__,
                    "class": args[0].__class__.__name__,
                    "func": func.__name__,
                    "args": args_str
                }
            )
            return output

        def function_wrapper(*args, **kwargs):  # pylint:disable=C0111
            chrono = time()
            output = func(*args, **kwargs)
            chrono = time() - chrono

            # Make a nice formatting
            args_str = ", ".join(iterargs(*args, **kwargs))
            log(
                {
                    "chrono": chrono * 1000,
                    "module": func.__module__,
                    "func": func.__name__,
                    "args": args_str
                }
            )
            return output

        func_args = inspect.getargspec(func)
        is_method = func_args[0] and func_args[0][0] in ('self', 'cls')

        log = getattr(logger, log_level.lower())
        if is_method:
            fmt = "ms=%(chrono)d func=%(module)s.%(class)s.%(func)s(%(args)s)"
            template = fmt
            log = partial(log, template)
            return update_wrapper(method_wrapper, func)

        template = "ms=%(chrono)d func=%(module)s.%(func)s(%(args)s)"
        log = partial(log, template)
        return update_wrapper(function_wrapper, func)

    return decorator


def log_request(request):
    final_time = time() - request.start_time

    def ms_logger(request):
        return "%d" % (final_time * 1000)

    loggers = {
        'ms': ms_logger,
    }

    registered_loggers = request.registry[get_key("registered_loggers")]
    log_order = request.registry[get_key("order")]
    log_separator = request.registry[get_key("separator")]

    loggers.update(registered_loggers)
    log_values = []
    templates = []  # E.g.: ['ms=%(ms)s', 'view=%(view)s', ...]

    # If a dict is returned by the callable, it will expand into multiple keys
    # and will be larger than `log_keys`.
    final_keys = []

    introspector = request.registry.introspector
    route_name = request.matched_route.name
    route_intr = introspector.get('routes', route_name)

    if not route_intr:
        return

    should_log_static = asbool(
        request.registry.settings.get(get_key('log_static'), False)
    )

#    import pdb; pdb.Pdb(nosigint=True).set_trace()
    view_log = None

    for related in introspector.related(route_intr):
        if related.category_name == 'views':
            view_func = related['callable']
            is_static_view = isinstance(view_func, static_view)

            if is_static_view and should_log_static:
                # lets log the path if it is a static view
                view_log = request.path
            elif not is_static_view:
                view_log = "%s.%s" % (
                    view_func.__module__,
                    view_func.__name__,
                )

    def view_logger(request):
        return view_log

    if view_log:
        loggers['view'] = view_logger
        log_keys = ['ms', 'view'] + log_order
    else:
        # if we don't find a view to log, this means we are on a static view
        # and dont want to log this request
        return

    for log_key in log_keys:
        log_func = loggers[log_key]

        log_value = log_func(request)

        # they returned a dict, generate K:V for the templates
        if isinstance(log_value, Mapping):
            for key, value in sorted(log_value.items()):
                # `log_key` is used as the prefix for dicts
                key = log_key + key
                final_keys.append(key)
                log_values.append(value)
                templates.append("%s=%%(%s)s" % (key, key))

        else:
            final_keys.append(log_key)
            log_values.append(log_value)
            templates.append("%s=%%(%s)s" % (log_key, log_key))

    log_template = log_separator.join(templates)
    template_params = dict(izip(final_keys, log_values))
    logger.info(log_template, template_params)


def log_request_factory(handler, registry):
    """
    This is a function that should tlog how long each view takes.

    It can be used by doing the following::

        config.add_tween('smlib.log.log_request_factory')

    Note that the above will be done automatically for you if you do::

        config.include('smlib.log')

    You can also register extra data to be logged by registering a function
    that returns a dict with extra data to be logged::

        def request_body(request):
            return request.body

        config.add_logging("body", request_body)

    or using inline lambda::

        config.add_logging("body", lambda req: req.body)

    or via Python dotted notation::

        config.add_logging("body", "myapp.lib.get_request_body")

    You may also return a dictionary of values:

        config.add_logging("body", lambda req: {
                'body': req.body, 'method': req.method
        })

    By default, logging components are space-separated: " ". If you want to
    change the separator, it can be done by changing it as followed::

        config.logging_separator(", ")

    """
    def logging_tween(request):
        request.start_time = time()

        try:
            response = handler(request)
            return response
        finally:
            if request.matched_route is not None:
                log_request(request)

    return logging_tween


def add_logging(config, log_key, log_func=None):
    resolver = DottedNameResolver()
    if log_func is None:
        log_func = operator.attrgetter(log_key)
    log_func = resolver.maybe_resolve(log_func)

    config.registry[get_key("registered_loggers")][log_key] = log_func
    config.registry[get_key("order")].append(log_key)


def set_logging_separator(config, separator):
    config.registry[get_key("separator")] = separator


COLOR_CODES = cycle((
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.CYAN,
))
END_COLOR_CODE = Fore.RESET


def colorize_text(text):
    return '%s%s%s' % (next(COLOR_CODES), text, END_COLOR_CODE)


def get_key(key, ns=log_namespace):
    key = '%s.%s' % (log_namespace, key)
    return key


def log_request_id_in_threadname(event):
    """
        This will attach `request.id` to the current
        threadname so that all log statements within this thread will
        get the request id
    """
    current_thread = threading.current_thread()
    original_name = current_thread.name

    # Hack the thread's name to inject a UUID
    registry = event.request.registry
    colored_logs = asbool(registry.settings.get(get_key('color'), False))

    request_id = event.request.id

    if colored_logs:
        request_id = colorize_text(request_id)

    current_thread.name = "%s][request=%s" % (
        original_name,
        request_id,
    )

    def unhack_thread_name(request):
        # Restore the thread's original name
        current_thread.name = original_name

    event.request.add_finished_callback(unhack_thread_name)


def includeme(config):
    config.add_request_method(
        callable=lambda req: str(uuid4()),
        name="id",
        property=True,
        reify=True
    )

    config.add_subscriber(
        log_request_id_in_threadname,
        'pyramid.events.NewRequest'
    )

    config.add_tween(get_key('log_request_factory'))

    config.registry[get_key('registered_loggers')] = {}
    config.registry[get_key('order')] = []
    config.registry[get_key('separator')] = " "

    config.add_directive('add_logging', add_logging)
    config.add_directive('logging_separator', set_logging_separator)


__all__ = ('perflog')
