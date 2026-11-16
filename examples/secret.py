import typing

import chillycord
from chillycord.ext import commands

intents = chillycord.Intents.default()

bot = commands.Bot(command_prefix=commands.when_mentioned, description='Nothing to see here!', intents=intents)


# the `hidden` keyword argument hides it from the help command.
@bot.group(hidden=True)
async def secret(ctx: commands.Context):
    """What is this "secret" you speak of?"""
    if ctx.invoked_subcommand is None:
        await ctx.send('Shh!', delete_after=5)


def create_overwrites(ctx, *objects):
    """This is just a helper function that creates the overwrites for the
    voice/text channels.

    A `chillycord.PermissionOverwrite` allows you to determine the permissions
    of an object, whether it be a `chillycord.Role` or a `chillycord.Member`.

    In this case, the `view_channel` permission is being used to hide the channel
    from being viewed by whoever does not meet the criteria, thus creating a
    secret channel.
    """

    # a dict comprehension is being utilised here to set the same permission overwrites
    # for each `chillycord.Role` or `chillycord.Member`.
    overwrites = {obj: chillycord.PermissionOverwrite(view_channel=True) for obj in objects}

    # prevents the default role (@everyone) from viewing the channel
    # if it isn't already allowed to view the channel.
    overwrites.setdefault(ctx.guild.default_role, chillycord.PermissionOverwrite(view_channel=False))

    # makes sure the client is always allowed to view the channel.
    overwrites[ctx.guild.me] = chillycord.PermissionOverwrite(view_channel=True)

    return overwrites


# since these commands rely on guild related features,
# it is best to lock it to be guild-only.
@secret.command()
@commands.guild_only()
async def text(ctx: commands.Context, name: str, *objects: typing.Union[chillycord.Role, chillycord.Member]):
    """This makes a text channel with a specified name
    that is only visible to roles or members that are specified.
    """

    overwrites = create_overwrites(ctx, *objects)

    # Tell the type checker that our Guild is not None
    assert ctx.guild is not None

    await ctx.guild.create_text_channel(
        name,
        overwrites=overwrites,
        topic='Top secret text channel. Any leakage of this channel may result in serious trouble.',
        reason='Very secret business.',
    )


@secret.command()
@commands.guild_only()
async def voice(ctx: commands.Context, name: str, *objects: typing.Union[chillycord.Role, chillycord.Member]):
    """This does the same thing as the `text` subcommand
    but instead creates a voice channel.
    """

    overwrites = create_overwrites(ctx, *objects)

    assert ctx.guild is not None

    await ctx.guild.create_voice_channel(
        name,
        overwrites=overwrites,
        reason='Very secret business.',
    )


@secret.command()
@commands.guild_only()
async def emoji(ctx: commands.Context, emoji: chillycord.PartialEmoji, *roles: chillycord.Role):
    """This clones a specified emoji that only specified roles
    are allowed to use.
    """

    # fetch the emoji asset and read it as bytes.
    emoji_bytes = await emoji.read()

    assert ctx.guild is not None

    # the key parameter here is `roles`, which controls
    # what roles are able to use the emoji.
    await ctx.guild.create_custom_emoji(
        name=emoji.name,
        image=emoji_bytes,
        roles=roles,
        reason='Very secret business.',
    )


bot.run('token')
