import asyncio
import functools

import pytest

from aiohttp.web_exceptions import HTTPMethodNotAllowed
from aiohttp_ext_handlers import exc_handlers_middleware, bind_exc_handler


def coroutine(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        coro = asyncio.coroutine(func)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(coro(*args, **kwargs))
        # loop.close()
        # asyncio.set_event_loop(None)

    return wrap


@pytest.fixture
def app():
    class App(dict):
        _middlewares = [exc_handlers_middleware]

    return App()


def test_bind_exc_handler__first(app):
    assert 'exc_handlers' not in app

    handler = 'handler'
    bind_exc_handler(app, RuntimeError, handler)

    assert 'exc_handlers' in app
    assert app['exc_handlers'][RuntimeError] == handler


def test_bind_exc_handler__exists(app):
    app['exc_handlers'] = {ValueError: 'handler_old'}

    handler = 'handler'
    bind_exc_handler(app, RuntimeError, handler)

    assert app['exc_handlers'][RuntimeError] == handler
    assert app['exc_handlers'][ValueError] == 'handler_old'


def test_bind_exc_handler__middleware_not_exist(app):
    app._middlewares.clear()

    with pytest.raises(RuntimeError):
        bind_exc_handler(app, ValueError, 'handler')


@coroutine
def test_middleware__no_exc(app):
    @asyncio.coroutine
    def handler(request):
        return 'response'

    mw = yield from exc_handlers_middleware(app, handler)
    response = yield from mw('request')

    assert response == 'response'


@coroutine
def test_middleware__exc_eq(app):
    @asyncio.coroutine
    def handler(request):
        raise RuntimeError()

    @asyncio.coroutine
    def exc_handler(request, exc):
        return 'response'

    app['exc_handlers'] = {RuntimeError: exc_handler}

    mw = yield from exc_handlers_middleware(app, handler)
    response = yield from mw('request')

    assert response == 'response'


@coroutine
def test_middleware__twice_exc(app):
    @asyncio.coroutine
    def handler(request):
        raise RuntimeError()

    @asyncio.coroutine
    def exc_handler_1(request, exc):
        raise ValueError()

    @asyncio.coroutine
    def exc_handler_2(request, exc):
        return 'response'

    app['exc_handlers'] = {
        RuntimeError: exc_handler_1,
        ValueError: exc_handler_2,
    }

    mw = yield from exc_handlers_middleware(app, handler)

    with pytest.raises(ValueError):
        yield from mw('request')


@coroutine
def test_middleware__exc_inheritance(app):
    class Exc(RuntimeError):
        pass

    @asyncio.coroutine
    def handler(request):
        raise Exc()

    @asyncio.coroutine
    def exc_handler(request, exc):
        return 'response'

    app['exc_handlers'] = {RuntimeError: exc_handler}

    mw = yield from exc_handlers_middleware(app, handler)
    response = yield from mw('request')

    assert response == 'response'


@coroutine
def test_middleware__not_found(app):
    @asyncio.coroutine
    def handler(request):
        raise RuntimeError()

    mw = yield from exc_handlers_middleware(app, handler)

    with pytest.raises(RuntimeError):
        yield from mw('request')


@coroutine
def test_middleware__http_exc(app):
    @asyncio.coroutine
    def handler(request):
        raise HTTPMethodNotAllowed(method='GET', allowed_methods=[])

    mw = yield from exc_handlers_middleware(app, handler)
    response = yield from mw('request')

    assert isinstance(response, HTTPMethodNotAllowed)
