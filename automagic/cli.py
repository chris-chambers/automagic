import functools

import lyre.server
import trio

from .autoreload import autoreloader
from . import harness


def main():
    import logging
    lyre_log_level = logging.INFO
    ch = logging.StreamHandler()
    ch.setLevel(lyre_log_level)
    lyre_logger = logging.getLogger('lyre')
    lyre_logger.setLevel(lyre_log_level)
    lyre_logger.addHandler(ch)

    trio.run(_main)


async def _main():
    def reload_filter(module):
        # Don't reload the harness module, since we set module-level variables
        # that need to be preserved.
        return module is not harness

    with autoreloader(reload_filter) as reloader:
        async with trio.open_nursery() as nursery:
            nursery.start_soon(functools.partial(lyre.server.run, port=0))
            nursery.start_soon(reloader.run)


if __name__ == '__main__':
    main()
