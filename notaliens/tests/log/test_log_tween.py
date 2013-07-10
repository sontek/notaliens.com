import json
import mock

from colorama import Fore
from pyramid import testing
from webtest import TestApp


def test_log_tween_include():
    # This tests automatic instrumentation of Pyramid views, using the
    # NewEvent subscriber

    with mock.patch('notaliens.log.logger') as mock_logger:
        def view_func(request):
            return {
                'status': 0,
                'data': {
                    'foo': 'bar',
                },
            }

        # Create a WSGI app with Pyramid and then wrap it with
        # webtest.TestApp for testing
        config = testing.setUp()
        config.add_route('view', '/view')
        config.add_view(view_func, route_name='view', renderer='json')
        config.include('notaliens.log')
        app = config.make_wsgi_app()
        app = TestApp(app)

        def info(log_template, template_params):
            assert log_template == 'ms=%(ms)s view=%(view)s'

            assert 'ms' in template_params
            assert 'view' in template_params
            assert isinstance(template_params['ms'], str)
            assert isinstance(int(template_params['ms']), int)
            assert template_params['view'] == 'test_log_tween.view_func'

        mock_logger.info.side_effect = info

        data = {'foo': 'bar', 'password': 'sensitive'}
        data = json.dumps(data)

        response = app.post('/view', params=data, status=200)

        assert response.content_type == 'application/json'
        assert response.json['status'] == 0
        assert response.json['data'] == {'foo': 'bar'}

        assert mock_logger.info.called


def test_log_tween_include_with_comma_separator():
    # This tests automatic instrumentation of Pyramid views, using the
    # NewEvent subscriber

    with mock.patch('notaliens.log.logger') as mock_logger:
        def view_func(request):
            return {
                'status': 0,
                'data': {
                    'foo': 'bar',
                },
            }

        # Create a WSGI app with Pyramid and then wrap it with
        # webtest.TestApp for testing
        config = testing.setUp()
        config.add_route('view', '/view')
        config.add_view(view_func, route_name='view', renderer='json')
        config.include('notaliens.log')
        config.logging_separator(', ')
        app = config.make_wsgi_app()
        app = TestApp(app)

        def info(log_template, template_params):
            assert log_template == 'ms=%(ms)s, view=%(view)s'

        mock_logger.info.side_effect = info
        app.post('/view', params="", status=200)
        assert mock_logger.info.called


def test_perflog_tween_include_w_extra_logging():
    # This tests adding additional context to be logged by the NewEvent
    # subscriber

    with mock.patch('notaliens.log.logger') as mock_logger:
        def view_func(request):
            return {
                'status': 0,
                'data': {
                    'foo': 'bar',
                },
            }

        # Create a WSGI app with Pyramid and then wrap it with
        # webtest.TestApp for testing
        config = testing.setUp()
        config.add_route('view', '/view')
        config.add_view(view_func, route_name='view', renderer='json')
        config.include('notaliens.log')
        config.add_logging("body")
        config.add_logging('method')
        config.add_logging('url', lambda req: req.url)
        config.add_logging('user-agent', lambda req: req.user_agent)
        app = config.make_wsgi_app()
        app = TestApp(app)

        def info(log_template, template_params):
            log_format = '%s %s %s %s %s' % (
                'ms=%(ms)s',
                'view=%(view)s',
                'body=%(body)s',
                'method=%(method)s',
                'url=%(url)s',
                'user-agent=%(user-agent)s'
            )
            assert log_template == log_format

            assert 'ms' in template_params
            assert 'view' in template_params
            assert 'body' in template_params
            assert 'method' in template_params
            assert 'url' in template_params
            assert 'user-agent' in template_params

            assert isinstance(template_params['ms'], str)
            assert isinstance(int(template_params['ms']), int)
            assert template_params['view'] == 'test_log_tween.view_func'
            assert template_params['body'] == b''
            assert template_params['method'] == 'POST'
            assert template_params['url'] == 'http://localhost/view'
            assert template_params['user-agent'] is None

        mock_logger.info.side_effect = info
        app.post('/view', params="", status=200)
        assert mock_logger.info.called


def dummy_logging(request):
    return "dummy_logging"


def test_perflog_tween_automatic_extra_logging_dotted_path():
    # This tests adding additional context to be logged by the NewEvent
    # subscriber

    with mock.patch('notaliens.log.logger') as mock_logger:
        def view_func(request):
            return {
                'status': 0,
                'data': {
                    'foo': 'bar',
                },
            }

        # Create a WSGI app with Pyramid and then wrap it with
        # webtest.TestApp for testing
        config = testing.setUp()
        config.add_route('view', '/view')
        config.add_view(view_func, route_name='view', renderer='json')
        config.include('notaliens.log')
        config.add_logging("dummy", __name__ + ".dummy_logging")
        app = config.make_wsgi_app()
        app = TestApp(app)

        def info(log_template, template_params):
            assert 'ms=%(ms)s view=%(view)s dummy=%(dummy)s' == log_template
            assert "dummy" in template_params

        mock_logger.info.side_effect = info

        data = {'foo': 'bar', 'password': 'sensitive'}
        data = json.dumps(data)

        response = app.post('/view', params=data, status=200)

        assert response.content_type == 'application/json'
        assert response.json['status'] == 0
        assert response.json['data'] == {'foo': 'bar'}

        assert mock_logger.info.called


def test_perflog_tween_automatic_extra_logging_one_argument():
    # This tests adding additional context to be logged.
    # Here we use only one argument to ``config.add_logging`` (we don't provide
    # a function; this means to log an attribute of the request object)

    with mock.patch('notaliens.log.logger') as mock_logger:
        def view_func(request):
            return {
                'status': 0,
                'data': {'output_key': 'output_val'},
            }

        # Create a WSGI app with Pyramid and then wrap it with
        # webtest.TestApp for testing
        config = testing.setUp()
        config.add_route('view', '/view')
        config.add_view(view_func, route_name='view', renderer='json')
        config.include('notaliens.log')
        config.add_logging("method")
        app = config.make_wsgi_app()
        app = TestApp(app)

        def info(log_template, template_params):
            assert 'ms=%(ms)s view=%(view)s method=%(method)s' == log_template
            assert template_params['method'] == 'POST'

        mock_logger.info.side_effect = info

        response = app.post('/view', status=200)

        assert response.json['status'] == 0
        assert response.json['data'] == {'output_key': 'output_val'}

        assert mock_logger.info.called


def test_perflog_tween_no_matching_route():
    # This tests that things don't blow up when no route matches

    config = testing.setUp()
    config.include('notaliens.log')
    app = config.make_wsgi_app()
    app = TestApp(app)

    from pyramid.exceptions import HTTPNotFound

    try:
        app.post('/view', params='{}', status=404)
    except HTTPNotFound:
        pass
    else:
        assert False, "This should've raised an HTTPNotFound exception"


COLOR_CODES = (
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.CYAN,
    Fore.RED,
)


def test_colorize_text():
    from notaliens.log import colorize_text

    for i in range(1, 6):  # [1, ..., 6]
        expected_text = '%sfoo%s' % (COLOR_CODES[i - 1], Fore.RESET)
        assert colorize_text("foo") == expected_text


def test_colorize_via_config():
    with mock.patch('notaliens.log.logger') as mock_logger:
        def view_func(request):
            return {
                'status': 0,
                'data': {
                    'foo': 'bar',
                },
            }

        # Create a WSGI app with Pyramid and then wrap it with
        # webtest.TestApp for testing
        config = testing.setUp()
        config.registry.settings['notaliens.log.color'] = 'true'
        config.add_route('view', '/view')
        config.add_view(view_func, route_name='view', renderer='json')
        config.include('notaliens.log')
        app = config.make_wsgi_app()
        app = TestApp(app)

        def info(log_template, template_params):
            import threading
            thread_name = threading.current_thread().name
            possible_thread_names = frozenset(
                'MainThread][request=%s' % color
                for color in COLOR_CODES
            )
            for possible_thread_name in possible_thread_names:
                if thread_name.startswith(possible_thread_name):
                    break
            else:
                assert False, (
                    "thread_name %r doesn't have same root as these "
                    "expected names: %s" % (
                        thread_name,
                        possible_thread_names
                    )
                )
            assert thread_name.endswith(Fore.RESET)

        mock_logger.info.side_effect = info
        app.post('/view', params="", status=200)
        assert mock_logger.info.called


def test_inject_request_id():
    with mock.patch('notaliens.log.logger') as mock_logger:
        def view_func(request):
            return {
                'status': 0,
                'data': {
                    'foo': 'bar',
                },
            }

        # Create a WSGI app with Pyramid and then wrap it with
        # webtest.TestApp for testing
        config = testing.setUp()
        config.add_route('view', '/view')
        config.add_view(view_func, route_name='view', renderer='json')
        config.include('notaliens.log')
        app = config.make_wsgi_app()
        app = TestApp(app)

        def info(log_template, template_params):
            import threading
            import re
            thread_name = threading.current_thread().name

            assert thread_name.startswith('MainThread][request=')
            assert re.search(
                r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",  # nopep8
                thread_name
            )

        mock_logger.info.side_effect = info
        app.post('/view', params="", status=200)
        assert mock_logger.info.called


def test_log_static_view():
    # This tests automatic instrumentation of Pyramid views, using the
    # NewEvent subscriber

    with mock.patch('notaliens.log.logger') as mock_logger:
        def view_func(request):
            return {
                'status': 0,
                'data': {
                    'foo': 'bar',
                },
            }

        # Create a WSGI app with Pyramid and then wrap it with
        # webtest.TestApp for testing
        config = testing.setUp()
        config.registry.settings['notaliens.log.log_static'] = True
        config.include('notaliens.log')
        config.add_static_view(name='/static', path='notaliens.log')
        app = config.make_wsgi_app()
        app = TestApp(app)

        def info(log_template, template_params):
            assert log_template == 'ms=%(ms)s view=%(view)s'
            assert template_params['view'] == '/static/1.png'

        mock_logger.info.side_effect = info
        from pyramid.httpexceptions import HTTPNotFound
        try:
            app.post('/static/1.png', params="", status=404)
        except HTTPNotFound:
            pass
        else:
            assert False, "This should've raised an HTTPNotFound exception"

        assert mock_logger.info.called


def test_perflog_view_dictionary_extra_logging():
    with mock.patch('notaliens.log.logger') as mock_logger:
        def view_func(request):
            return {
                'status': 0,
                'data': {'output_key': 'output_val'},
            }

        # Create a WSGI app with Pyramid and then wrap it with
        # webtest.TestApp for testing
        config = testing.setUp()
        config.add_route('view', '/view')
        config.add_view(view_func, route_name='view', renderer='json')
        config.include('notaliens.log')
        config.add_logging("rattr-", lambda req: {'foo': 'bar'})
        app = config.make_wsgi_app()
        app = TestApp(app)

        def info(log_template, template_params):
            compare_str = 'ms=%(ms)s view=%(view)s rattr-foo=%(rattr-foo)s'
            assert compare_str == log_template
            assert template_params['rattr-foo'] == 'bar'

        mock_logger.info.side_effect = info

        response = app.post('/view', status=200)

        assert response.json['status'] == 0
        assert response.json['data'] == {'output_key': 'output_val'}

        assert mock_logger.info.called


def test_perflog_view_dictionary_w_empty_prefix_extra_logging():
    with mock.patch('notaliens.log.logger') as mock_logger:
        def view_func(request):
            return {
                'status': 0,
                'data': {'output_key': 'output_val'},
            }

        # Create a WSGI app with Pyramid and then wrap it with
        # webtest.TestApp for testing
        config = testing.setUp()
        config.add_route('view', '/view')
        config.add_view(view_func, route_name='view', renderer='json')
        config.include('notaliens.log')
        config.add_logging("", lambda req: {'foo': 'bar'})
        app = config.make_wsgi_app()
        app = TestApp(app)

        def info(log_template, template_params):
            assert 'ms=%(ms)s view=%(view)s foo=%(foo)s' == log_template
            assert template_params['foo'] == 'bar'

        mock_logger.info.side_effect = info

        app.post('/view', status=200)

        assert mock_logger.info.called
