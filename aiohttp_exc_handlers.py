import asyncio
import logging

from aiohttp.web_exceptions import HTTPException

from resolver_deco import resolver

log = logging.getLogger(__name__)


@asyncio.coroutine
def exc_handlers_middleware(app, handler):
    @asyncio.coroutine
    def middleware(request):
        try:
            return (yield from handler(request))
        except HTTPException as exc:
            return exc
        except Exception as exc:
            log.debug("search handler for exception {!r}".format(exc))
            exc_handlers = app.get('exc_handlers', {})

            if exc.__class__ in exc_handlers:
                exc_handler = exc_handlers[exc.__class__]
            else:
                for exc_class, exc_handler in exc_handlers.items():
                    if isinstance(exc, exc_class):
                        # TODO: search closer inheritance
                        break
                else:
                    log.debug("exception not handled {!r}".format(exc))
                    raise exc

            log.debug("find handler for exception {!r} {!r}"
                      "".format(exc, exc_handler))
            return (yield from exc_handler(request, exc))

    return middleware


@resolver('exc', 'handler')
def bind_exc_handler(app, exc, handler):
    if exc_handlers_middleware not in app._middlewares:
        raise RuntimeError("not found exc_handlers_middleware"
                           " in applisaction middlewares")

    if 'exc_handlers' not in app:
        app['exc_handlers'] = {}

    app['exc_handlers'][exc] = handler
