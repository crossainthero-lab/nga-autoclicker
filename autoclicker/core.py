"""Settings and the shared, thread-safe clicking engine."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import threading

DEFAULT_CPS = 10.0
DEFAULT_HOTKEY = '<f8>'
MAX_CPS = 1000.0


def validate_cps(value: object) -> float:
    try:
        cps = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError('Clicks per second must be a number.') from exc
    if not math.isfinite(cps) or not 0 < cps <= MAX_CPS:
        raise ValueError(f'Clicks per second must be greater than 0 and at most {MAX_CPS:g}.')
    return cps


def config_path() -> Path:
    if os.name == 'nt':
        base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
    else:
        base = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
    return base / 'nga-autoclicker' / 'settings.json'


def load_settings(path: Path | None = None) -> dict:
    try:
        data = json.loads((path or config_path()).read_text(encoding='utf-8'))
        cps = validate_cps(data['cps'])
        hotkey = data['hotkey']
        if not isinstance(hotkey, str) or not hotkey.strip():
            raise ValueError('Invalid hotkey')
        return {'cps': cps, 'hotkey': hotkey.strip()}
    except (OSError, ValueError, TypeError, KeyError):
        return {'cps': DEFAULT_CPS, 'hotkey': DEFAULT_HOTKEY}


def save_settings(cps: float, hotkey: str, path: Path | None = None) -> None:
    destination = path or config_path()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({'cps': validate_cps(cps), 'hotkey': hotkey}, indent=2) + '\n', encoding='utf-8')


class ClickEngine:
    """Click in a worker thread; configuration and state are protected by a lock."""
    def __init__(self, click, cps: float, on_change=None):
        self._click = click
        self._cps = validate_cps(cps)
        self._on_change = on_change or (lambda active: None)
        self._condition = threading.Condition()
        self._active = False
        self._closed = False
        self._thread = threading.Thread(target=self._run, name='clicker', daemon=True)
        self._thread.start()

    def set_cps(self, cps: float) -> None:
        with self._condition:
            self._cps = validate_cps(cps)
            self._condition.notify_all()

    def toggle(self) -> bool:
        with self._condition:
            if self._closed:
                return False
            self._active = not self._active
            active = self._active
            self._condition.notify_all()
        self._on_change(active)
        return active

    def close(self) -> None:
        with self._condition:
            self._closed = True
            self._active = False
            self._condition.notify_all()
        self._thread.join()

    def _run(self) -> None:
        while True:
            with self._condition:
                self._condition.wait_for(lambda: self._active or self._closed)
                if self._closed:
                    return
                # Holding the lock ensures stop cannot return while a click is in flight.
                try:
                    self._click()
                except Exception:
                    self._active = False
                    self._on_change(False)
                    continue
                self._condition.wait(timeout=1 / self._cps)
