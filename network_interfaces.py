# -*- coding: utf-8 -*-
import re
import os
__author__ = 'vahid'


def clean_list(l):
    return [j for j in [i.strip().strip('"') for i in l] if j]


class Stanza(object):
    type = None
    _filename = None

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
        key = item.replace('_', '-')
        try:
            return ' '.join([i for i in self._items if i[0] == key][0][1:])
        except IndexError:
            raise AttributeError('%s %s' % (object.__repr__(self), item))

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
            if subclass.type and stanza_type == subclass.type:
                return subclass(filename, *cells)

        # Partial start match
        for subclass in subclasses:
            if subclass.type and stanza_type.startswith(subclass.type):
                return subclass(filename, *cells)


class MultilineStanza(Stanza):

    def __repr__(self):
        return '%s\n%s\n' % (
            super(MultilineStanza, self).__repr__(),
            '\n'.join(['  ' + ' '.join(i) for i in self._items]))


class StartupStanza(Stanza):

    @property
    def mode(self):
        return self._headers[0]

    @property
    def iface_name(self):
        return self._headers[1]


class Auto(StartupStanza):
    type = 'auto'


class Allow(StartupStanza):
    type = 'allow-'


class Iface(MultilineStanza):
    type = 'iface'
    startup = None

    @property
    def name(self):
        return self._headers[1]

    @name.setter
    def name(self, val):
        self._headers[1] = val

    @property
    def address_family(self):
        return self._headers[2]

    @address_family.setter
    def address_family(self, val):
        self._headers[2] = val

    @property
    def method(self):
        return self._headers[3]

    @method.setter
    def method(self, val):
        self._headers[3] = val

    def __repr__(self):
        return '%s\n%s' % (self.startup, super(Iface, self).__repr__())


class Mapping(MultilineStanza):
    type = 'mapping'


class Source(Stanza):
    type = 'source'

    @property
    def source_filename(self):
        return self._headers[1]

    @source_filename.setter
    def source_filename(self, val):
        self._headers[1] = val


class SourceDirectory(Stanza):
    type = 'source-directory'

    @property
    def source_directory(self):
        return self._headers[1]

    @source_directory.setter
    def source_directory(self, val):
        self._headers[1] = val


class InterfacesFile(object):

    def __init__(self, filename):
        self.filename = filename
        self.dirname = os.path.dirname(filename)
        self.sub_files = []
        current_stanza = None
        stanzas = []
        with open(self.filename) as f:
            for l in f:
                line = l.strip()
                if not line or line.startswith('#'):
                    continue
                if Stanza.is_stanza(line):
                    if current_stanza:
                        stanzas.append(current_stanza)
                    current_stanza = Stanza.create(line, self.filename)
                else:
                    current_stanza.add_entry(line)
            if current_stanza:
                stanzas.append(current_stanza)

        self.interfaces = [iface for iface in stanzas if isinstance(iface, Iface)]
        for i in self.interfaces:
            stanzas.remove(i)

        self.mappings = [mapping for mapping in stanzas if isinstance(mapping, Mapping)]
        for i in self.mappings:
            stanzas.remove(i)

        self.sources = [source for source in stanzas if isinstance(source, (Source, SourceDirectory))]
        subfiles = []
        for i in self.sources:
            if isinstance(i, SourceDirectory):
                d = self.normalize_path(i.source_directory)
                subfiles += [os.path.join(d, f) for f in os.listdir(d)
                             if os.path.isfile(os.path.join(d, f)) and
                             re.match('^[a-zA-Z0-9_-]+$', f)]
            else:
                subfiles.append(self.normalize_path(i.source_filename))

        for subfile in subfiles:
            self.sub_files.append(InterfacesFile(subfile))

        for startup in [s for s in stanzas if isinstance(s, StartupStanza)]:
            self.get_iface(startup.iface_name).startup = startup

    def find_iface(self, name):
        return [iface for iface in self.interfaces if iface.name.index(name)]

    def get_iface(self, name):
        result = [iface for iface in self.interfaces if iface.name == name]
        if result:
            return result[0]

        for s in self.sub_files:
            try:
                return s.get_iface(name)
            except KeyError:
                continue

        raise KeyError(name)

    def normalize_path(self, p):
        if p.startswith('/'):
            return p
        return os.path.join(self.dirname, p)
