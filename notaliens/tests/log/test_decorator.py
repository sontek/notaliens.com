import mock

from notaliens.log import perflog


def test_perflog_on_function():
    with mock.patch('notaliens.log.logger') as mock_logger:
        @perflog()
        def some_silly_func(foo, kwarg=None):
            assert foo == 'bar'
            return 'ret'

        def info(format_str, data):
            assert format_str == 'ms=%(chrono)d func=%(module)s.%(func)s(%(args)s)'
            assert data['module'] == 'test_decorator'
            assert data['func'] == 'some_silly_func'
            assert data['args'] == "'bar', kwarg='some_kwarg'"
            assert 'chrono' in data

        mock_logger.info.side_effect = info

        ret = some_silly_func('bar', kwarg='some_kwarg')

        assert ret == 'ret'

        assert mock_logger.info.called


def test_perflog_on_method():
    with mock.patch('notaliens.log.logger') as mock_logger:
        class Foo(object):
            @perflog()
            def some_silly_method(self, foo):
                assert foo == 'bar'
                return 'ret'

        def info(format_str, data):
            assert format_str == 'ms=%(chrono)d func=%(module)s.%(class)s.%(func)s(%(args)s)'
            assert data['module'] == 'test_decorator'
            assert data['func'] == 'some_silly_method'
            assert data['args'].startswith("<test_decorator.")
            assert "Foo object at 0x" in data['args']
            assert data['args'].endswith(">, 'bar'")
            assert 'chrono' in data

        mock_logger.info.side_effect = info

        foo = Foo()
        ret = foo.some_silly_method('bar')

        assert ret == 'ret'

        assert mock_logger.info.called
