====================================
Bind views to exceptions for aiohttp
====================================

.. image:: https://travis-ci.org/zzzsochi/aiohttp_exc_handlers.svg?branch=master
  :target:  https://travis-ci.org/zzzsochi/aiohttp_exc_handlers
  :align: right

.. image:: https://coveralls.io/repos/zzzsochi/aiohttp_exc_handlers/badge.svg
  :target:  https://coveralls.io/github/zzzsochi/aiohttp_exc_handlers
  :align: right

-----
Usage
-----

.. code:: python

    import asyncio

    from aiohttp import web
    from aiohttp_ext_handlers import (
        exc_handlers_middleware,
        bind_exc_handler,
    )


    class CustomException(Exception):
        pass


    async def custom_exception_handler(request, exc):
        return web.Response(text="Hello, {!s}!".format(exc))


    async def hello(request):
        raise CustomException('world')


    # add middleware
    app = web.Application(middlewares=[exc_handlers_middleware])

    # bind handler to exception
    bind_exc_handler(app, CustomException, custom_exception_handler)

    app.router.add_route('GET', '/', hello)

    loop = asyncio.get_event_loop()
    handler = app.make_handler()
    f = loop.create_server(handler, '0.0.0.0', 8080)
    srv = loop.run_until_complete(f)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(handler.finish_connections(1.0))
        srv.close()
        loop.run_until_complete(srv.wait_closed())
        loop.run_until_complete(app.finish())

    loop.close()


-----
Tests
-----

.. code:: shell

    $ pip install pytest
    $ py.test tests.py
