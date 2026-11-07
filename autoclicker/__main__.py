from __future__ import annotations

import argparse
import sys
import threading

from .core import ClickEngine, load_settings, save_settings, validate_cps
from .platform import load_input, parse_hotkey, start_listener


def main(argv=None):
    parser = argparse.ArgumentParser(description='Click repeatedly at the mouse pointer using a global toggle hotkey.')
    parser.add_argument('--cli', action='store_true', help='run in the terminal instead of opening the UI')
    parser.add_argument('--cps', type=float, help='clicks per second (greater than 0, up to 1000)')
    parser.add_argument('--hotkey', help='global toggle key or combination, e.g. F8 or ctrl+shift+a')
    args = parser.parse_args(argv)
    settings = load_settings()
    try:
        cps = validate_cps(args.cps if args.cps is not None else settings['cps'])
        hotkey = args.hotkey if args.hotkey is not None else settings['hotkey']
        keyboard, mouse = load_input()
        parse_hotkey(keyboard, hotkey)
        if args.cli:
            return run_cli(keyboard, mouse, cps, hotkey)
        from .ui import run_ui
        return run_ui(keyboard, mouse, cps, hotkey)
    except (RuntimeError, ValueError, OSError, ImportError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


def run_cli(keyboard, mouse, cps, hotkey):
    controller = mouse.Controller()
    engine = ClickEngine(lambda: controller.click(mouse.Button.left), cps,
                         lambda active: print('Clicking ' + ('ON' if active else 'OFF'), flush=True))
    listener = None
    try:
        listener = start_listener(keyboard, hotkey, engine.toggle)
        save_settings(cps, hotkey)
        print(f'Ready: {cps:g} clicks/second. Press {hotkey} to toggle; Ctrl+C to quit.', flush=True)
        threading.Event().wait()
    except KeyboardInterrupt:
        print('\nStopping.')
    finally:
        if listener:
            listener.stop()
        engine.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
