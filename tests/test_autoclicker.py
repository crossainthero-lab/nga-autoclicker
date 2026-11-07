import json
from pathlib import Path
import tempfile
import threading
import time
import unittest

from autoclicker.core import ClickEngine, load_settings, save_settings, validate_cps
from autoclicker.platform import parse_hotkey


class SettingsTests(unittest.TestCase):
    def test_valid_and_invalid_rates(self):
        self.assertEqual(validate_cps('2.5'), 2.5)
        for value in (0, -1, 1001, 'nan', 'inf', 'abc', None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_cps(value)

    def test_save_load_and_invalid_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'settings.json'
            save_settings(12, 'ctrl+a', path)
            self.assertEqual(load_settings(path), {'cps': 12, 'hotkey': 'ctrl+a'})
            path.write_text(json.dumps({'cps': -1, 'hotkey': 'F8'}))
            self.assertEqual(load_settings(path), {'cps': 10, 'hotkey': '<f8>'})

    def test_hotkey_normalization(self):
        class HotKey:
            @staticmethod
            def parse(value):
                return value
        keyboard = type('Keyboard', (), {'HotKey': HotKey})
        self.assertEqual(parse_hotkey(keyboard, 'F8'), '<f8>')
        self.assertEqual(parse_hotkey(keyboard, 'Ctrl+Shift+A'), '<ctrl>+<shift>+a')
        self.assertEqual(parse_hotkey(keyboard, '<ctrl>+<alt>+a'), '<ctrl>+<alt>+a')


class EngineTests(unittest.TestCase):
    def test_toggle_stops_clicking_and_close(self):
        clicked = threading.Event()
        clicks = []
        states = []
        def click():
            clicks.append(time.monotonic())
            clicked.set()
        engine = ClickEngine(click, 100, states.append)
        try:
            self.assertEqual(clicks, [])
            self.assertTrue(engine.toggle())
            self.assertTrue(clicked.wait(1))
            self.assertFalse(engine.toggle())
            count = len(clicks)
            time.sleep(.05)
            self.assertEqual(len(clicks), count)
            self.assertEqual(states, [True, False])
        finally:
            engine.close()
        self.assertFalse(engine.toggle())

    def test_close_wakes_slow_clicker(self):
        clicked = threading.Event()
        engine = ClickEngine(clicked.set, 0.01)
        engine.toggle()
        self.assertTrue(clicked.wait(1))
        start = time.monotonic()
        engine.close()
        self.assertLess(time.monotonic() - start, 1)


if __name__ == '__main__':
    unittest.main()
