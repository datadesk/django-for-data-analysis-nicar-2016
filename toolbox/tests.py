#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.test import TestCase
from .templatetags.toolbox_tags import dropcap
from .templatetags.toolbox_tags import emdashes


class ToolboxTest(TestCase):

    def test_unicodecsv(self):
        """
        Test simple usage of the unicodecsv toy.
        """
        import csv
        from toolbox import unicodecsv
        from cStringIO import StringIO
        d = StringIO("""Name,Type,County
La Cañada Flintridge,Neighborhood,L.A.County
Downtown,Neighborhood,L.A.County
""")
        reader = unicodecsv.UnicodeDictReader(d)
        reader.next()
        reader.__iter__()
        self.assertEqual(type(list(reader)), type([]))

    def test_dropcap_filter(self):
        """
        Test simple usage of the capfirst templatetag.
        """
        before = "I love dropcaps."
        after = dropcap(before)
        self.failUnlessEqual(
            after,
            "<span class='dropcap'>I</span> love dropcaps."
        )

    def test_emdashes_filter(self):
        """
        Test simple usage of the emdashes templatetag.
        """
        before = "<p>The end.</p><p>-- Ruben Salazar</p>"
        after = emdashes(before)
        self.failUnlessEqual(
            after,
            "<p>The end.</p><p>&mdash; Ruben Salazar</p>"
        )
