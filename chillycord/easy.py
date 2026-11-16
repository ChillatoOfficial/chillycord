"""
The MIT License (MIT)

Copyright (c) 2015-present Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Callable, Optional, Union

from .flags import Intents
from .utils import MISSING
from .ext import commands

__all__ = ('Bot',)

_log = logging.getLogger(__name__)

TOKEN_ENV_VARS = ('CHILLYCORD_TOKEN', 'DISCORD_TOKEN')


class Bot(commands.Bot):
    """A :class:`~chillycord.ext.commands.Bot` with sensible defaults and less boilerplate.

    .. code-block:: python3

        bot = chillycord.Bot(prefix='!')

        @bot.hybrid()
        async def ping(ctx):
            await ctx.send('pong')

        bot.run()  # reads CHILLYCORD_TOKEN or DISCORD_TOKEN

    Parameters
    ----------
    prefix: Union[:class:`str`, List[:class:`str`]]
        The command prefix. The bot also responds to mentions.
    intents: Optional[:class:`Intents`]
        Defaults to :meth:`Intents.default` with ``message_content`` enabled.
    sync_commands: :class:`bool`
        Whether to sync application commands on startup. The sync only happens
        when the set of commands changed since the last sync.
    sync_cache: Union[:class:`str`, :class:`os.PathLike`]
        File used to remember the hash of the last synced commands.
    lag_warning: Optional[:class:`float`]
        Log a warning when the event loop is blocked for longer than this many
        seconds, which usually means a handler is running blocking code (``time.sleep``,
        ``requests``, heavy CPU work...). ``None`` disables the watchdog.
    """

    def __init__(
        self,
        prefix: Union[str, list[str], tuple[str, ...]] = '!',
        *,
        intents: Optional[Intents] = None,
        sync_commands: bool = True,
        sync_cache: Union[str, 'os.PathLike[str]'] = '.chillycord_sync',
        lag_warning: Optional[float] = 0.5,
        **options: Any,
    ) -> None:
        if intents is None:
            intents = Intents.default()
            intents.message_content = True

        prefixes = [prefix] if isinstance(prefix, str) else list(prefix)
        options.setdefault('help_command', commands.DefaultHelpCommand())
        super().__init__(commands.when_mentioned_or(*prefixes), intents=intents, **options)
        self.sync_commands: bool = sync_commands
        self._sync_cache: Path = Path(sync_cache)
        self.lag_warning: Optional[float] = lag_warning
        self._lag_task: Optional[asyncio.Task[None]] = None

    def hybrid(self, name: str = MISSING, **attrs: Any) -> Callable[..., Any]:
        """Decorator registering a command usable both as a prefix and a slash command."""
        if name is not MISSING:
            attrs['name'] = name
        return self.hybrid_command(**attrs)

    def slash(self, name: str = MISSING, description: str = MISSING, **kwargs: Any) -> Callable[..., Any]:
        """Decorator registering a slash command on this bot's command tree."""
        if name is not MISSING:
            kwargs['name'] = name
        if description is not MISSING:
            kwargs['description'] = description
        return self.tree.command(**kwargs)

    def _commands_hash(self) -> str:
        payload = [cmd.to_dict(self.tree) for cmd in self.tree.get_commands()]
        raw = json.dumps(payload, sort_keys=True, default=str).encode()
        return hashlib.sha256(raw).hexdigest()

    async def sync_if_changed(self) -> bool:
        """Syncs the global application commands only if they changed since the last sync.

        Returns whether a sync was performed.
        """
        current = self._commands_hash()
        try:
            previous = self._sync_cache.read_text().strip()
        except OSError:
            previous = None

        if previous == current:
            _log.debug('Application commands unchanged, skipping sync')
            return False

        synced = await self.tree.sync()
        _log.debug('Synced %d application command(s)', len(synced))
        try:
            self._sync_cache.write_text(current)
        except OSError:
            _log.warning('Could not write sync cache %s', self._sync_cache)
        return True

    async def _watch_loop_lag(self, interval: float = 0.1) -> None:
        threshold = self.lag_warning
        assert threshold is not None
        while True:
            start = time.perf_counter()
            await asyncio.sleep(interval)
            lag = time.perf_counter() - start - interval
            if lag > threshold:
                _log.warning(
                    'Event loop was blocked for %.2fs: a handler is probably running blocking code. '
                    'Use async libraries or asyncio.to_thread() for slow work.',
                    lag,
                )

    async def close(self) -> None:
        if self._lag_task is not None:
            self._lag_task.cancel()
            self._lag_task = None
        await super().close()

    async def setup_hook(self) -> None:
        await super().setup_hook()
        if self.lag_warning is not None:
            self._lag_task = asyncio.create_task(self._watch_loop_lag())
        if self.sync_commands:
            await self.sync_if_changed()

    def run(self, token: Optional[str] = None, **kwargs: Any) -> None:
        """Like :meth:`Client.run` but the token defaults to the ``CHILLYCORD_TOKEN``
        or ``DISCORD_TOKEN`` environment variable."""
        if token is None:
            for var in TOKEN_ENV_VARS:
                token = os.environ.get(var)
                if token:
                    break
        if not token:
            raise RuntimeError('No token given: pass one to run() or set ' + ' or '.join(TOKEN_ENV_VARS))
        super().run(token, **kwargs)
