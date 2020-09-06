import contextlib
from types import ModuleType
from typing import Callable
import sys

import fswatch
from fswatch import libfswatch
import magazine
import trio

# MONKEY PATCH libfswatch!
assert fswatch.__version__ == '0.1.1'

import ctypes

libfswatch.fsw_stop_monitor = libfswatch.lib.fsw_stop_monitor
libfswatch.fsw_stop_monitor.restype = ctypes.c_int
libfswatch.fsw_stop_monitor.argtypes = [ctypes.c_void_p]
# END PATCHING


FilterFn = Callable[[ModuleType], bool]


@contextlib.contextmanager
def autoreloader(filter: FilterFn=None):
    reloader = Autoreloader(filter)
    with magazine.importhook(reloader._hook):
        yield reloader


class Autoreloader:
    def __init__(self, filter: FilterFn=None):
        self.filter = filter

    def _changes(self, path, evt_time, flags, flags_num, event_num):
        module = None
        path = path.decode('utf8')
        for m in sys.modules.values():
            modfile = getattr(m, '__file__', None)
            if modfile == path:
                module = m
                break

        if not module:
            return

        if self.filter and not self.filter(module):
            return

        try:
            magazine.reload(module)
            print(f'reloaded: {module}')
        except:
            import traceback
            print(f'reloading failed for {module}')
            traceback.print_exc()


    def _hook(self, module):
        # FIXME: Race condition.  `_hook` may be called before the monitor has
        # been created in `run`.
        if module.__file__:
            libfswatch.fsw_stop_monitor(self.monitor.handle)


    async def run(self):
        try:
            while True:
                self.monitor = fswatch.Monitor()
                self.monitor.set_callback(self._changes)

                for module in sys.modules.values():
                    modfile = getattr(module, '__file__', None)
                    if modfile:
                        self.monitor.add_path(modfile)

                await trio.to_thread.run_sync(
                    libfswatch.fsw_start_monitor,
                    self.monitor.handle,
                    cancellable=True,
                )
        except trio.Cancelled:
            libfswatch.fsw_stop_monitor(self.monitor.handle)
