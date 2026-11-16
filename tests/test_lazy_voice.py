import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VOICE_MODULES = ('voice_client', 'voice_state', 'player', 'opus', 'oggparse')

CODE = """
import sys
sys.path.insert(0, %r)
sys.modules['audioop'] = None  # make 'import audioop' fail
for name in ('nacl', 'davey'):
    sys.modules[name] = None
import chillycord, chillycord.ext.commands, chillycord.ext.tasks
loaded = [m for m in %r if 'chillycord.' + m in sys.modules]
assert not loaded, loaded
assert chillycord.VoiceProtocol.__name__ == 'VoiceProtocol'
assert 'chillycord.voice_client' in sys.modules
print('ok')
"""


def test_import_does_not_load_voice():
    out = subprocess.run(
        [sys.executable, '-I', '-c', CODE % (ROOT, VOICE_MODULES)], capture_output=True, text=True
    )
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == 'ok'
