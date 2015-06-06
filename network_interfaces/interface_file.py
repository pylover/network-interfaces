# -*- coding: utf-8 -*-
import re
import os.path
import shutil
from .constants import DEFAULT_HEADER
from .stanza import Stanza
from .source import SourceDirectory, Source
from .startup import StartupStanza
from .iface import Iface, Mapping
__author__ = 'vahid'

class InterfacesFile(object):

    @property
    def absolute_filename(self):
        if self.filename.startswith('/'):
            return self.filename

        if self.source:
            rootdir = os.path.dirname(self.source._filename)
            return os.path.abspath(os.path.join(rootdir, self.filename))

        raise ValueError('Cannot resolve absolute path for %s' % self.filename)

    def __init__(self, filename, header=DEFAULT_HEADER, backup='.back', source=None):
        self.source = source
        self.filename = filename
        self.dirname = os.path.dirname(filename)
        self.sub_files = []
        self.header = header
        self.backup = backup
        current_stanza = None
        stanzas = []

        with open(self.absolute_filename) as f:
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
                d = i.source_directory
                subfiles += [(os.path.join(d, f), i) for f in os.listdir(os.path.join(self.dirname, d))
                             if os.path.isfile(os.path.join(self.dirname, d, f)) and
                             re.match('^[a-zA-Z0-9_-]+$', f)]
            else:
                subfiles.append((i.source_filename, i))

        for subfile in subfiles:
            self.sub_files.append(InterfacesFile(subfile[0], source=subfile[1]))

        for startup in [s for s in stanzas if isinstance(s, StartupStanza)]:
            self.get_iface(startup.iface_name).startup = startup

    def find_iface(self, name):
        return [iface for iface in self.interfaces if iface.name.index(name)]

    def get_iface(self, name):
        result = [iface for iface in self.interfaces + self.mappings if iface.name == name]
        if result:
            return result[0]

        for s in self.sub_files:
            try:
                return s.get_iface(name)
            except KeyError:
                continue

        raise KeyError(name)

    def save(self, recursive=False, filename=None, directory=None):

        filename = filename if filename else self.filename
        if not filename.startswith('/') and directory:
            filename = os.path.abspath(os.path.join(directory, filename))

        if self.backup and os.path.exists(filename):
            shutil.copyfile(filename, '%s%s' % (filename, self.backup))

        with open(filename, 'w') as f:
            f.write(self.header)
            for iface in self.interfaces:
                f.write('\n')
                f.write(repr(iface))

            for mapping in self.mappings:
                f.write('\n')
                f.write(repr(mapping))

            for source in self.sources:
                f.write('\n')
                f.write(repr(source))

        if recursive:
            dirname = directory if directory else os.path.abspath(os.path.dirname(filename))
            for sub_file in self.sub_files:
                sub_file.save(recursive=recursive, directory=dirname)

    def __hash__(self):
        result = 0
        for iface in self.interfaces:
            result ^= hash(iface)

        for map in self.mappings:
            result ^= hash(map)

        for source in self.sources:
            result ^= hash(source)
        return result
