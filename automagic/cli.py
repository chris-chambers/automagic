import lyre.server
import trio

from .autoreload import autoreloader
from . import harness


def main():
    trio.run(_main)


async def _main():
    def reload_filter(module):
        # Don't reload the harness module, since we set module-level variables
        # that need to be preserved.
        return module is not harness

    with autoreloader(reload_filter) as reloader:
        async with trio.open_nursery() as nursery:
            nursery.start_soon(lyre.server.run)
            nursery.start_soon(reloader.run)
