# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation

from unittest import TestCase

import time

from quodlibet.browsers.soundcloud import query
from quodlibet.browsers.soundcloud.query import SoundcloudQuery, convert_time

from quodlibet import const
from quodlibet.util.dprint import print_d

NONE = set([])


class TestExtract(TestCase):

    @classmethod
    def setUpClass(cls):
        const.DEBUG = True

    @classmethod
    def tearDownClass(cls):
        const.DEBUG = False

    def test_extract_single_tag(self):
        self.verify("artist=jay-z", {"jay-z"})

    def test_extract_unsupported(self):
        try:
            self.verify("musicbrainz_discid=12345", NONE)
        except query.error:
            pass
        else:
            self.fail("Should have thrown")

    def test_extract_composite_text(self):
        self.verify("&(foo, bar)", {"foo", "bar"})
        self.verify("|(either, or)", {"either", "or"})

    def test_numeric_simple(self):
        self.verify("#(length=180)", {'180000'}, term='duration')

    def test_extract_date(self):
        now = int(time.time())
        terms = SoundcloudQuery("#(date>today)", clock=lambda: now).terms
        self.failUnlessEqual(terms['created_at[from]'].pop(),
                             convert_time(now - 86400))

    def test_numeric_relative(self):
        self.verify("#(length>180)", {'180000'}, term='duration[from]')
        self.verify("#(180<=length)", {'180000'}, term='duration[from]')
        self.verify("#(length<360)", {'360000'}, term='duration[to]')
        self.verify("#(360>=length)", {'360000'}, term='duration[to]')

    def test_extract_tag_inter(self):
        self.verify("genre=&(jazz, funk)", {'jazz', 'funk'})

    def test_extract_tag_union(self):
        self.verify("genre=|(jazz, funk)", {'jazz', 'funk'})

    def test_extract_complex(self):
        self.verify("&(artist='foo', genre=|(rock, metal))",
                    {'foo', 'rock', 'metal'})

    def verify(self, text, expected, term='q'):
        print_d("Trying '%s'..." % text)
        terms = SoundcloudQuery(text).terms
        self.failUnlessEqual(terms[term], expected,
                             msg="terms[%s] wasn't %r. Full terms: %r"
                                 % (term, expected, terms))
