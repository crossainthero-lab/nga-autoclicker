"""System input integration. Imported lazily so --help works without a desktop."""


def load_input():
    try:
        from pynput import keyboard, mouse
        return keyboard, mouse
    except ImportError as exc:
        raise RuntimeError('pynput is required. Install dependencies with: python -m pip install -r requirements.txt') from exc
    except Exception as exc:
        raise RuntimeError(f'Unable to access system input: {exc}. Check your desktop session and input permissions.') from exc


def parse_hotkey(keyboard, value):
    value = value.strip().lower()
    # Accept convenient names such as F8 and ctrl+shift+a alongside pynput syntax.
    parts = value.split('+')
    aliases = {'ctrl': '<ctrl>', 'control': '<ctrl>', 'shift': '<shift>',
               'alt': '<alt>', 'cmd': '<cmd>', 'super': '<cmd>'}
    normalized = '+'.join(aliases.get(part.strip(),
        f'<{part.strip()}>' if len(part.strip()) > 1 and not part.strip().startswith('<') else part.strip())
        for part in parts)
    try:
        return keyboard.HotKey.parse(normalized)
    except (ValueError, TypeError) as exc:
        raise ValueError('Invalid hotkey. Try F8, a, or ctrl+shift+a.') from exc


def start_listener(keyboard, hotkey, callback):
    keys = parse_hotkey(keyboard, hotkey)
    binding = keyboard.HotKey(keys, callback)
    listener = keyboard.Listener(
        on_press=lambda key: binding.press(listener.canonical(key)),
        on_release=lambda key: binding.release(listener.canonical(key)))
    listener.start()
    listener.wait()
    return listener
