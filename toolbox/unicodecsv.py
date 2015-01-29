"""
Support for reading CSV as Unicode objects.

This module is necessary because Python's csv library doesn't support reading
Unicode strings.

This code is mostly copied from the Python documentation:
http://www.python.org/doc/2.5.2/lib/csv-examples.html
"""
import csv
import codecs


class UTF8Recoder:
    """
    Reencodes input to UTF-8.
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode('utf-8')


class UnicodeDictReader:
    """
    Like the standard csv.DictReader, except it actually works with unicode.
    """
    def __init__(self, f, encoding='utf-8', **kwargs):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.DictReader(f, **kwargs)

    def next(self):
        row = self.reader.next()
        keys = [unicode(i, 'utf-8') for i in row.keys()]
        values = [unicode(i, 'utf-8') for i in row.values()]
        return dict(zip(keys, values))

    def __iter__(self):
        return self
