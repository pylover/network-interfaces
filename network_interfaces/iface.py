# -*- coding: utf-8 -*-
from .stanza import MultilineStanza
import ipcalc
from .errors import ValidationError
__author__ = 'vahid'


class IfaceBase(MultilineStanza):
    startup = None

    @property
    def name(self):
        return self._headers[1]

    @name.setter
    def name(self, val):
        self._headers[1] = val

    def __hash__(self):
        return hash(self.startup) ^ super(IfaceBase, self).__hash__()

    def __repr__(self):
        if self.startup:
            return '%s\n%s' % (self.startup, super(IfaceBase, self).__repr__())
        return super(IfaceBase, self).__repr__()


class Iface(IfaceBase):
    _type = 'iface'

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

    def validate(self, allow_correction=False):
        if self.method == 'static':
            if 'network' not in self:
                raise ValidationError('The network option was not exists in the %s' % self.name)

            if 'netmask' not in self:
                raise ValidationError('The netmask option was not exists in the %s' % self.name)

            # if not allow_correction:
            # else:

            network = ipcalc.Network('%s/%s' % (self.network, self.netmask))
            if ipcalc.IP(self.address) not in network:
                raise ValidationError('The ip address: %s was not exists in the network: %s' % (self.address, network))
        return True


class Mapping(IfaceBase):
    _type = 'mapping'

    def __getattr__(self, item):
        if item.startswith('map_'):
            map_name = item.split('_')[1]
            key = map_name.replace('_', '-')
            return ' '.join([i for i in self._items if i[0] == 'map' and i[1] == key][0][2:])
        return super(Mapping, self).__getattr__(item)

    @property
    def mappings(self):
        return [i for i in self._items if i[0] == 'map']
