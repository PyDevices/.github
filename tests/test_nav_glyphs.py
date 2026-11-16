# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""The navigation glyphs in site-chrome.js are the ones in data/nav_glyphs.json."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class NavGlyphs(unittest.TestCase):
    def test_chrome_draws_every_glyph(self):
        with open(os.path.join(ROOT, 'data/nav_glyphs.json'), encoding='utf-8') as f:
            glyphs = json.load(f)
        with open(os.path.join(ROOT, 'assets/js/site-chrome.js'), encoding='utf-8') as f:
            chrome = f.read()
        for name, entry in glyphs.items():
            if entry.get('cards_only'):
                # A page the navigator does not list: only the generator draws it.
                continue
            # The chrome adds a class to the four symbols it styles by name.
            body = entry['svg'].split('>', 1)[1]
            self.assertIn(body, chrome, f'{name} in site-chrome.js differs from data/nav_glyphs.json')


if __name__ == '__main__':
    unittest.main()
