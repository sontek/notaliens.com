import inspect
import logging
import threading

from functools import (
    partial,
    update_wrapper
)
from itertools import cycle
from time import time
from uuid import uuid4

from pyramid.path import DottedNameResolver
from pyramid.settings import asbool
from pyramid.static import static_view

from colorama import init as colorama_init
from colorama import Fore

logger = logging.getLogger(__name__)

colorama_init()


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
            log({
                "chrono": chrono * 1000,
                "module": func.__module__,
                "class": args[0].__class__.__name__,
                "func": func.__name__,
                "args": args_str
            })
            return output

        def function_wrapper(*args, **kwargs):  # pylint:disable=C0111
            chrono = time()
            output = func(*args, **kwargs)
            chrono = time() - chrono

            # Make a nice formatting
            args_str = ", ".join(iterargs(*args, **kwargs))
            log({
                "chrono": chrono * 1000,
                "module": func.__module__,
                "func": func.__name__,
                "args": args_str
            })
            return output

        func_args = inspect.getargspec(func)
        is_method = func_args[0] and func_args[0][0] in ('self', 'cls')

        log = getattr(logger, log_level.lower())
        if is_method:
            template = "ms=%(chrono)d func=%(module)s.%(class)s.%(func)s(%(args)s)"
            log = partial(log, template)
            return update_wrapper(method_wrapper, func)

        template = "ms=%(chrono)d func=%(module)s.%(func)s(%(args)s)"
        log = partial(log, template)
        return update_wrapper(function_wrapper, func)

    return decorator


def start_timing_request(event):
    """
    This is a function that should handle the NewRequest event, it will log how
    long each view takes.

    It can be used by doing the following::

        config.add_subscriber(
            'notaliens.log.perflog.start_timing_request',
            'pyramid.events.NewRequest'
        )

    Note that the above will be done automatically for you if you do::

        config.include('notaliens.log')

    You can also register extra data to be logged by registering a function
    that returns a dict with extra data to be logged::

        def request_body(request):
            return request.body

        config.add_logging("body", request_body)

    or using inline lambda::

        config.add_logging("body", lambda req: req.body)

    or via Python dotted notation::

        config.add_logging("body", "myapp.lib.get_request_body")

    By default, logging components are space-separated: " ". If you want to
    change the separator, it can be done by changing it as followed::

        config.logging_separator(", ")

    """
    start_time = time()

    def stop_timing_request(request):
        if not request.matched_route:
            return

        final_time = time() - start_time

        introspector = request.registry.introspector
        route_name = request.matched_route.name
        route_intr = introspector.get('routes', route_name)

        if not  route_intr:
            return

        found_view = None

        should_log_static = asbool(
            request.registry.settings.get('log.log_static', False)
        )

        for related in introspector.related(route_intr):
            if related.category_name == 'views':
                view_func = related['callable']

                if isinstance(view_func, static_view) and not should_log_static:
                    return

                found_view = view_func


        def ms_logger(request):
            return "%d" % (final_time * 1000)

        loggers = {
            'ms': ms_logger,
        }

        registered_loggers = request.registry["registered_loggers"]
        log_order = request.registry["log_order"]
        log_separator = request.registry["log_separator"]

        loggers.update(registered_loggers)
        log_keys = ['ms'] + log_order
        log_values = []
        templates = []

        for log_key in log_keys:
            log_func = loggers[log_key]
            log_value = log_func(request)
            log_values.append(log_value)
            templates.append("%s=%%(%s)s" % (log_key, log_key))  # E.g.: ms=%(ms)s

        if found_view:
            if not isinstance(found_view, static_view):
                templates.append("%s.%s" % (
                        found_view.__module__
                        , found_view.__name__
                    )
                )
            else:
                templates.append("%s" % request.path)


        log_template = log_separator.join(templates)
        template_params = dict(zip(log_keys, log_values))
        logger.info(log_template, template_params)

    event.request.add_finished_callback(stop_timing_request)


def add_logging(config, log_key, log_func):
    resolver = DottedNameResolver()
    log_func = resolver.maybe_resolve(log_func)

    config.registry["registered_loggers"][log_key] = log_func
    config.registry["log_order"].append(log_key)


def set_logging_separator(config, separator):
    config.registry["log_separator"] = separator

color_codes = cycle((
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.CYAN,
))

end_color_code = Fore.RESET


def colorize_text(text):
    return '%s%s%s' % (next(color_codes), text, end_color_code)


def log_request_id(event):
    current_thread = threading.current_thread()
    original_name = current_thread.name

    # Hack the thread's name to inject a UUID
    registry = event.request.registry
    colored_logs = asbool(registry.settings.get('log.color', False))

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
    config.add_subscriber(start_timing_request, 'pyramid.events.NewRequest')
    config.add_subscriber(log_request_id, 'pyramid.events.NewRequest')

    config.registry["registered_loggers"] = {}
    config.registry["log_order"] = []
    config.registry["log_separator"] = " "

    config.add_directive('add_logging', add_logging)
    config.add_directive('logging_separator', set_logging_separator)


__all__ = ('perflog')
