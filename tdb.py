#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
A library supporting Tdb “Text DataBase” format.

Tdb provides a superior alternative to CSV. In particular, Tdb tables are
named and Tdb fields are strictly typed. Also, there is a clear distinction
between field names and data values, and strings respect whitespace
(including newlines) and have no problems with commas, quotes, etc.. Perhaps
best of all, a single Tdb file may contain one—or more—tables.
'''

import datetime
import gzip
import io
import pathlib

import editabletuple


BYTES_SENTINAL = b'\x04'
DATE_SENTINAL = datetime.date(1808, 8, 8)
DATETIME_SENTINAL = datetime.datetime(1808, 8, 8, 8, 8, 8)
INT_SENTINAL = -1808080808
REAL_SENTINAL = -1808080808.0808
STR_SENTINAL = '\x04'


class Tdb:

    def __init__(self):
        self.tables = {}


    def load(self, filename_or_filelike):
        '''Reads the given file (or file-like stream) and replaces this
        Tdb's tables with those read in.'''
        close = False
        if isinstance(filename_or_filelike, (str, pathlib.Path)):
            filename_or_filelike = str(filename_or_filelike)
            opener = (gzip.open
                      if filename_or_filelike[-3:].lower().endswith('.gz')
                      else open)
            stream = opener(filename_or_filelike, 'rt', encoding='utf-8')
            close = True
        else:
            stream = filename_or_filelike
        try:
            self.loads(stream.read())
        finally:
            if close:
                stream.close()


    def loads(self, text):
        '''Reads the given text and replaces this Tdb's tables with those
        read in.'''
        self.tables = _read_tdb(text)


    def dump(self, filename_or_filelike, *, decimals=-1):
        '''Writes this Tdb's tables to the given file (or file-like
        stream).'''
        if not (1 <= decimals <= 19):
            decimals = -1
        close = False
        if isinstance(filename_or_filelike, (str, pathlib.Path)):
            filename_or_filelike = str(filename_or_filelike)
            opener = (gzip.open
                      if filename_or_filelike[-3:].lower().endswith('.gz')
                      else open)
            stream = opener(filename_or_filelike, 'wt', encoding='utf-8')
            close = True
        else:
            stream = filename_or_filelike
        try:
            _write_tdb(stream, self.tables, decimals)
        finally:
            if close:
                stream.close()


    def dumps(self, *, decimals=-1):
        '''Writes this Tdb's tables to a string which is then returned.'''
        stream = io.StringIO()
        try:
            self.dump(stream, decimals)
            return stream.getvalue()
        finally:
            stream.close()


def load(filename_or_filelike):
    '''Reads the given file (or file-like stream) and returns a Tdb with the
    tables that have been read in.'''
    db = Tdb()
    db.load(filename_or_filelike)
    return db


def loads(text):
    '''Reads the given text and returns a Tdb with the tables that have been
    read in.'''
    db = Tdb()
    db.loads(text)
    return db


def _read_tdb(text):
    tables = {}
    table = None
    lino = 1
    while text:
        c = text[0]
        if c == '\n':
            lino += 1
            text = text[1:]
        elif c == '[':
            text, table, lino = _read_meta(text[1:], lino)
            tables[table.name] = table
            print(table) # TODO delete
        else: # read records into the current table
            text, lino = _read_records(text, table, lino)
            for record in table.records: # TODO delete
                print(record)
    return tables


def _read_meta(text, lino):
    end = text.find('%')
    if end == -1:
        raise Error(f'{lino}#expected to find "%"')
    lino += text[:end].count('\n')
    table = Table()
    field_name = None
    for i, part in enumerate(text[:end].split()):
        if i == 0:
            table.name = part
        elif i % 2 != 0:
            field_name = part
        else:
            table.meta_fields.append(MetaField(field_name, part))
    return text[end + 1:], table, lino + 1 # allow for %


def _read_records(text, table, lino):
    record = None
    column = 0
    columns = table.columns
    while text:
        if record is None:
            record = table.RecordClass()
            column = 0
        c = text[0]
        if c == '\n': # ignore whitespace
            text = text[1:]
            lino += 1
        elif c in ' \t\r': # ignore whitespace
            text = text[1:]
        elif c == '!':
            _handle_sentinel(record, column, lino)
            text, column = _advance(text, column)
        elif c in 'FfNn':
            _handle_bool(False, record, column, lino)
            text, column = _advance(text, column)
        elif c in 'TtYy':
            _handle_bool(True, record, column, lino)
            text, column = _advance(text, column)
        elif c == '(':
            text = _handle_bytes(text[1:], record, column, lino)
            column += 1
        else:
            text, column = _advance(text, column) # TODO delete
    # TODO
    return text, lino


def _advance(text, column):
    return text[1:], column + 1


def _handle_sentinel(record, column, lino):
    kind = record[column].kind
    if kind == 'bool':
        raise Error(f'{lino}#bool fields don\'t allow sentinals')
    elif kind == 'bytes':
        record[column] = BYTES_SENTINAL
    elif kind == 'date':
        record[column] = DATE_SENTINAL
    elif kind == 'datetime':
        record[column] = DATETIME_SENTINAL
    elif kind == 'int':
        record[column] = INT_SENTINAL
    elif kind == 'real':
        record[column] = REAL_SENTINAL
    else: # str
        record[column] = STR_SENTINAL


def _handle_bool(value, record, column, lino):
    kind = record[column].kind
    if kind != 'bool':
        raise Error(f'{lino}#expected type {kind}, got a bool')
    record[column] = value


def _handle_bytes(text, record, column, lino):
    kind = record[column].kind
    if kind != 'bytes':
        raise Error(f'{lino}#expected type {kind}, got a bytes')
    return text


def _fromstr_for_kind(kind):
    if kind == 'bool':
        def bool_fromstr(s):
            s = s.lower()
            if s in 'ty':
                return True 
            elif s in 'fn':
                return False 
            raise Error(f'0#expected one of T t Y y F f N n, got {s!r}')
        return bool_fromstr
    if kind == 'bytes':
        return bytes.fromhex
    if kind == 'date':
        return datetime.date.fromisoformat
    if kind == 'datetime':
        return datetime.datetime.fromisoformat
    if kind == 'int':
        return int
    if kind == 'real':
        return float
    return str


def _write_tdb(stream, tables, decimals):
    for table_name, table in tables.items():
        pass # TODO


class MetaField:

    def __init__(self, name, kind):
        self.name = name
        self.kind = kind
        self.fromstr = _fromstr_for_kind(kind)


    def __repr__(self):
        return f'{self.__class__.__name__}({self.name!r}, {self.kind!r})'


class Table:

    def __init__(self):
        self.name = None
        self.meta_fields = []
        self.records = []
        self._RecordClass = None


    @property
    def RecordClass(self):
        if self._RecordClass is None:
            self._RecordClass = editabletuple.editabletuple(self.name,
                *[field.name for field in self.meta_fields])
        return self._RecordClass


    @property
    def columns(self):
        return len(self.meta_fields)


    def append(self, record):
        self.records.append(record)


    def __repr__(self):
        meta = '\n  '.join((str(m) for m in self.meta_fields))
        return f'{self.__class__.__name__}({self.name!r})\n  ' + meta


class Error(Exception):
    pass


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1 or sys.argv[1] in {'-h', '--help'}:
        raise SystemExit('usage: tdb.py <infile.tdb> [outfile.tdb]')
    infile = sys.argv[1]
    outfile = sys.stdout if len(sys.argv) == 2 else sys.argv[2]
    db = load(infile)
    db.dump(outfile)
