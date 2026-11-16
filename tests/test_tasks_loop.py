import asyncio

import pytest

import chillycord
from chillycord.ext import tasks


class _Resp:
    status = 503
    reason = 'Service Unavailable'


@pytest.mark.asyncio
async def test_server_error_does_not_kill_loop():
    n = 0

    @tasks.loop(seconds=0.02)
    async def t():
        nonlocal n
        n += 1
        if n == 2:
            raise chillycord.DiscordServerError(_Resp(), 'boom')

    t.start()
    try:
        # after the error the loop retries with a random backoff (up to ~1s)
        for _ in range(300):
            if n > 3:
                break
            await asyncio.sleep(0.02)
        assert t.is_running()
        assert n > 3
    finally:
        t.cancel()


@pytest.mark.asyncio
async def test_class_level_exception_types_are_inherited():
    class C:
        @tasks.loop(seconds=0.02)
        async def t(self):
            raise ValueError('x')

    C.t.add_exception_type(ValueError)
    c = C()
    c.t.start()
    await asyncio.sleep(0.3)
    try:
        assert c.t.is_running()
    finally:
        c.t.cancel()


@pytest.mark.asyncio
async def test_restart_revives_failed_loop():
    n = 0

    @tasks.loop(seconds=0.02)
    async def t():
        nonlocal n
        n += 1
        if n == 1:
            raise ValueError('not retried')

    t.start()
    await asyncio.sleep(0.15)
    assert not t.is_running() and t.failed()
    t.restart()
    await asyncio.sleep(0.15)
    try:
        assert t.is_running()
    finally:
        t.cancel()


@pytest.mark.asyncio
async def test_count_and_before_after_hooks():
    seen = []

    @tasks.loop(seconds=0.01, count=3)
    async def t():
        seen.append('run')

    @t.before_loop
    async def before():
        seen.append('before')

    @t.after_loop
    async def after():
        seen.append('after')

    t.start()
    await asyncio.sleep(0.3)
    assert seen == ['before', 'run', 'run', 'run', 'after']
