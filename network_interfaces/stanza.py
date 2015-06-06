# -*- coding: utf-8 -*-
import re
from .helpers import clean_list, list_hash
__author__ = 'vahid'

class Stanza(object):
    _type = None
    _filename = None
    _headers = None
    _items = None

    def __init__(self, filename, *headers):
        self._filename = filename
        self._headers = headers
        self._items = []

    def add_entry(self, l):
        cells = re.split('\s+', l)
        cells = clean_list(cells)
        if cells:
            self._items.append(cells)

    def __repr__(self):
        return ' '.join(self._headers)

    def __getattr__(self, item):
        try:
            return self[item]
        except (KeyError, IndexError):
            raise AttributeError('%s %s' % (object.__repr__(self), item))

    def __setattr__(self, key, value):
        if hasattr(self.__class__, key):
            super(Stanza, self).__setattr__(key, value)
        else:
            self[key] = value

    def __delattr__(self, item):
        if hasattr(self.__class__, item):
            super(Stanza, self).__delattr__(item)
        else:
            del self[item]

    def __getitem_internal(self, item):
        key = item.replace('_', '-')
        for i in self._items:
            if i[0] == key:
                return i
        return None

    def __delitem_internal(self, item):
        key = item.replace('_', '-')
        for i in self._items:
            if i[0] == key:
                self._items.remove(i)
                return

    def __getitem__(self, item):
        if not isinstance(item, basestring):
            raise TypeError(type(item))
        result = self.__getitem_internal(item)
        if not result:
            raise KeyError(item)
        return ' '.join(result[1:])

    def __setitem__(self, key, value):
        if not isinstance(key, basestring):
            raise TypeError(type(key))
        values = re.split('\s', value)

        cells = self.__getitem_internal(key)
        if not cells:
            self.add_entry(' '.join([key] + values))
        else:
            del cells[1:]
            cells += values

    def __delitem__(self, item):
        if not isinstance(item, basestring):
            raise TypeError(type(item))
        self.__delitem_internal(item)

    def _items_hash(self):
        result = 0
        for i in self._items:
            result ^= list_hash(i)
        return result

    def _headers_hash(self):
        result = 0
        for h in self._headers:
            result ^= h.__hash__()
        return result

    def __hash__(self):
        return \
            self._type.__hash__() ^ \
            self._headers_hash() ^ \
            self._items_hash()

    @classmethod
    def is_stanza(cls, s):
        return re.match(r'^(iface|mapping|auto|allow-|source).*', s)

    @classmethod
    def subclasses(cls):
        return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                       for g in s.subclasses()]

    @classmethod
    def create(cls, header, filename):
        cells = re.split('\s+', header)
        cells = clean_list(cells)
        stanza_type = cells[0]
        subclasses = cls.subclasses()

        # Checking for exact match
        for subclass in subclasses:
            if subclass._type and stanza_type == subclass._type:
                return subclass(filename, *cells)

        # Partial start match
        for subclass in subclasses:
            if subclass._type and stanza_type.startswith(subclass._type):
                return subclass(filename, *cells)


class MultilineStanza(Stanza):
    def __repr__(self):
        return '%s\n%s\n' % (
            super(MultilineStanza, self).__repr__(),
            '\n'.join(['  ' + ' '.join(i) for i in self._items]))


