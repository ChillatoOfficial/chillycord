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

import argparse
import importlib.metadata
import platform
import sys

import aiohttp

import chillycord


def show_version() -> None:
    entries = []

    entries.append('- Python v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}'.format(sys.version_info))
    version_info = chillycord.version_info
    entries.append('- chillycord v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}'.format(version_info))
    if version_info.releaselevel != 'final':
        try:
            version = importlib.metadata.version('chillycord')
        except importlib.metadata.PackageNotFoundError:
            version = None
        if version:
            entries.append(f'    - chillycord metadata: v{version}')

    entries.append(f'- aiohttp v{aiohttp.__version__}')

    try:
        import davey  # type: ignore
    except ImportError:
        entries.append('- davey not found')
    else:
        entries.append(f'- davey v{davey.__version__}')

    uname = platform.uname()
    entries.append('- system info: {0.system} {0.release} {0.version}'.format(uname))
    print('\n'.join(entries))


def main() -> None:
    parser = argparse.ArgumentParser(prog='chillycord', description='Tools for helping with chillycord')
    parser.add_argument('-v', '--version', action='store_true', help='shows the library version')
    args = parser.parse_args()
    if args.version:
        show_version()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
