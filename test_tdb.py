#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import os
import re
import unittest

import tdb


class TestTdb(unittest.TestCase):

    def setUp(self):
        # self.maxDiff = None
        self.filenames = [os.path.expanduser(f'~/app/go/tdb/eg/{name}.tdb')
                          for name in ('classic', 'csv', 'db1',
                                       'incidents')]


    def test_01(self):
        for i, filename in enumerate(self.filenames, 1):
            with self.subTest(i=i):
                with open(filename, 'rt', encoding='utf-8') as file:
                    expected = file.read()
                db = tdb.load(filename)
                actual = db.dumps()
                if expected != actual:
                    expected, actual = maybe_sanitize(expected, actual)
                self.assertEqual(expected, actual)
                db = tdb.loads(expected)
                actual = db.dumps()
                if expected != actual:
                    expected, actual = maybe_sanitize(expected, actual)
                self.assertEqual(expected, actual)


    def test_02(self):
        data = '[Recs Ok bool\n%\nT f y N 1 0]'
        expected = '[Recs Ok bool\n%\nT\nF\nT\nF\nT\nF\n]'
        db = tdb.loads(data)
        actual = db.dumps()
        if expected != actual:
            expected, actual = maybe_sanitize(expected, actual)
        self.assertEqual(expected, actual)


    def test_03(self):
        expected = '[Records AField int\n%\n2\n3\n5\n]\n'
        db = tdb.loads(expected)
        actual = db.dumps()
        if expected != actual:
            expected, actual = maybe_sanitize(expected, actual)
        self.assertEqual(expected, actual)


    def test_e100(self):
        with self.assertRaises(tdb.Error) as ctx:
            tdb.loads('[T A bool\n%\n-3]')
        err = ctx.exception
        m = re.search(r'^E(\d\d\d)#', str(err))
        self.assertTrue(m is not None and m.group(1) == '100')


    def test_e105(self):
        with self.assertRaises(tdb.Error) as ctx:
            tdb.loads('[T A bool\n%\n2]')
        err = ctx.exception
        m = re.search(r'^E(\d\d\d)#', str(err))
        self.assertTrue(m is not None and m.group(1) == '105')



def maybe_sanitize(a, b):
    if a != b:
        a = strip0s(a).strip()
        b = strip0s(b).strip()
        if a != b:
            show(a, b)
    return a, b


def strip0s(text):
    text = text.replace('.0 ', ' ')
    return re.sub(r'(\.[1-9]+)0+', r'\1', text)


def show(expected, actual):
    with open('/tmp/a.tdb', 'wt', encoding='utf-8') as file:
        file.write(actual)
    with open('/tmp/e.tdb', 'wt', encoding='utf-8') as file:
        file.write(expected)
    print('wrote /tmp/[ae].tdb')


if __name__ == '__main__':
    unittest.main()
