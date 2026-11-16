"""
Discord API Wrapper
~~~~~~~~~~~~~~~~~~~

A basic wrapper for the Discord API.

:copyright: (c) 2015-present Rapptz
:license: MIT, see LICENSE for more details.

"""

__title__ = 'chillycord'
__author__ = 'ChillatoOfficial, Rapptz'
__license__ = 'MIT'
__copyright__ = 'Copyright 2015-present Rapptz, 2026-present ChillatoOfficial'
__version__ = '0.1.0'

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

import logging
from typing import NamedTuple, Literal, TYPE_CHECKING

from .client import *
from .appinfo import *
from .user import *
from .emoji import *
from .partial_emoji import *
from .activity import *
from .channel import *
from .guild import *
from .flags import *
from .member import *
from .message import *
from .asset import *
from .errors import *
from .permissions import *
from .role import *
from .file import *
from .colour import *
from .integrations import *
from .invite import *
from .template import *
from .welcome_screen import *
from .sku import *
from .widget import *
from .object import *
from .reaction import *
from . import (
    utils as utils,
    abc as abc,
    ui as ui,
    app_commands as app_commands,
)
from .enums import *
from .embeds import *
from .mentions import *
from .shard import *
from .webhook import *
from .audit_logs import *
from .raw_models import *
from .team import *
from .sticker import *
from .stage_instance import *
from .scheduled_event import *
from .interactions import *
from .components import *
from .threads import *
from .automod import *
from .poll import *
from .soundboard import *
from .subscription import *
from .presences import *
from .primary_guild import *
from .onboarding import *
from .collectible import *


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal['alpha', 'beta', 'candidate', 'final']
    serial: int


version_info: VersionInfo = VersionInfo(major=0, minor=1, micro=0, releaselevel='final', serial=0)

logging.getLogger(__name__).addHandler(logging.NullHandler())

# This is a backwards compatibility hack and should be removed in v3
# Essentially forcing the exception to have different base classes
# In the future, this should only inherit from ClientException
if len(MissingApplicationID.__bases__) == 1:
    MissingApplicationID.__bases__ = (app_commands.AppCommandError, ClientException)

del logging, NamedTuple, Literal, VersionInfo


# Voice support is optional and loaded lazily: importing chillycord does not
# import the voice, audio-player or opus modules (nor PyNaCl/davey/audioop).
_LAZY_VOICE = {
    'opus': 'opus',
    'VoiceProtocol': 'voice_client',
    'VoiceClient': 'voice_client',
    'AudioSource': 'player',
    'PCMAudio': 'player',
    'FFmpegAudio': 'player',
    'FFmpegPCMAudio': 'player',
    'FFmpegOpusAudio': 'player',
    'PCMVolumeTransformer': 'player',
    'Bot': 'easy',
}

if TYPE_CHECKING:
    from . import opus as opus
    from .player import *
    from .voice_client import *
    from .easy import Bot as Bot


def __getattr__(name: str):
    module = _LAZY_VOICE.get(name)
    if module is None:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
    import importlib

    mod = importlib.import_module(f'.{module}', __name__)
    value = mod if name == module else getattr(mod, name)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(_LAZY_VOICE))
