import asyncio

import pytest

import chillycord


def make(tmp_path, **kw):
    return chillycord.Bot('?', sync_cache=tmp_path / 'sync', **kw)


def test_defaults(tmp_path):
    bot = make(tmp_path)
    assert bot.intents.message_content
    assert bot.sync_commands


def test_hybrid_and_slash_registration(tmp_path):
    bot = make(tmp_path)

    @bot.hybrid()
    async def ping(ctx):
        """Ping."""

    @bot.slash(description='Say hi')
    async def hello(interaction):
        pass

    assert bot.get_command('ping') is not None
    assert {c.name for c in bot.tree.get_commands()} == {'ping', 'hello'}


def test_hash_changes_with_commands(tmp_path):
    bot = make(tmp_path)
    before = bot._commands_hash()

    @bot.slash(description='Say hi')
    async def hello(interaction):
        pass

    assert bot._commands_hash() != before


def test_sync_only_when_changed(tmp_path):
    bot = make(tmp_path)
    calls = []

    async def fake_sync(**kw):
        calls.append(1)
        return []

    bot.tree.sync = fake_sync  # type: ignore

    @bot.slash(description='Say hi')
    async def hello(interaction):
        pass

    async def go():
        assert await bot.sync_if_changed() is True
        assert await bot.sync_if_changed() is False

    asyncio.run(go())
    assert calls == [1]


def test_run_requires_token(tmp_path, monkeypatch):
    monkeypatch.delenv('CHILLYCORD_TOKEN', raising=False)
    monkeypatch.delenv('DISCORD_TOKEN', raising=False)
    with pytest.raises(RuntimeError, match='No token'):
        make(tmp_path).run()


def test_lag_watchdog_warns_on_blocking(tmp_path, caplog):
    import logging
    import time

    bot = make(tmp_path, lag_warning=0.05)

    async def go():
        task = asyncio.create_task(bot._watch_loop_lag(interval=0.01))
        await asyncio.sleep(0.05)
        time.sleep(0.2)  # simulate a handler blocking the loop
        await asyncio.sleep(0.05)
        task.cancel()

    with caplog.at_level(logging.WARNING):
        asyncio.run(go())
    assert any('blocked' in r.message for r in caplog.records)


def test_asset_save_does_not_block(tmp_path):
    from chillycord import utils

    target = tmp_path / 'f.bin'
    n = asyncio.run(utils._write_file(target, b'abc'))
    assert n == 3 and target.read_bytes() == b'abc'
