# -*- coding: utf-8 -*-
import unittest
from os.path import join, dirname, abspath
from network_interfaces import InterfacesFile, Auto, Allow
__author__ = 'vahid'

this_dir = abspath(dirname(__file__))
data_dir = join(this_dir, 'data')

class NetworkingCase(unittest.TestCase):

    def setUp(self):
        self.interfaces_filename = join(data_dir, 'interfaces')

    def test_interfaces(self):
        f = InterfacesFile(self.interfaces_filename)

        self.assertRaises(KeyError, f.get_iface, 'non-existance-iface')

        lo = f.get_iface('lo')
        self.assertEquals(lo.startup.mode, 'auto')
        self.assertIsInstance(lo.startup, Auto)
        self.assertEquals(lo.name, 'lo')
        self.assertEquals(lo.address_family, 'inet')
        self.assertEquals(lo.method, 'loopback')

        eth0 = f.get_iface('eth0')
        self.assertEquals(eth0.startup.mode, 'auto')
        self.assertIsInstance(eth0.startup, Auto)
        self.assertEquals(eth0.name, 'eth0')
        self.assertEquals(eth0.address_family, 'inet')
        self.assertEquals(eth0.method, 'static')
        self.assertEquals(eth0.address, '192.168.11.2')
        self.assertEquals(eth0.netmask, '255.255.255.240')
        self.assertEquals(eth0.broadcast, '192.168.11.15')
        self.assertEquals(eth0.network, '192.168.11.0')
        self.assertEquals(eth0.gateway, '192.168.11.1')
        self.assertEquals(eth0.dns_nameservers, '8.8.8.8 8.8.4.4')

        eth1 = f.get_iface('eth1')
        self.assertEquals(eth1.startup.mode, 'auto')
        self.assertIsInstance(eth1.startup, Auto)
        self.assertEquals(eth1.name, 'eth1')
        self.assertEquals(eth1.address_family, 'inet')
        self.assertEquals(eth1.method, 'dhcp')
        self.assertRaises(AttributeError, lambda: eth1.address)

        wlan0 = f.get_iface('wlan0')
        self.assertEquals(wlan0.startup.mode, 'allow-hotplug')
        self.assertIsInstance(wlan0.startup, Allow)
        self.assertEquals(wlan0.name, 'wlan0')
        self.assertEquals(wlan0.address_family, 'inet')
        self.assertEquals(wlan0.method, 'static')
        self.assertEquals(wlan0.address, '192.168.9.41')
        self.assertEquals(wlan0.netmask, '255.255.255.0')
        self.assertEquals(wlan0.broadcast, '192.168.9.255')
        self.assertEquals(wlan0.network, '192.168.9.0')
        self.assertEquals(wlan0.gateway, '192.168.9.1')
        self.assertEquals(wlan0.wpa_ssid, 'khayyam')
        self.assertEquals(wlan0.wpa_psk, '<-Wine&Is&Mine->')

        wlan1 = f.get_iface('wlan1')
        self.assertEquals(wlan1.startup.mode, 'auto')
        self.assertIsInstance(wlan1.startup, Auto)
        self.assertEquals(wlan1.name, 'wlan1')
        self.assertEquals(wlan1.address_family, 'inet')
        self.assertEquals(wlan1.method, 'dhcp')
        self.assertEquals(wlan1.wpa_ssid, 'Dorfak')
        self.assertEquals(wlan1.wpa_psk, 'ShoorPalangGoolakhTappeh')
        self.assertRaises(AttributeError, lambda: wlan1.address)
        

if __name__ == '__main__':
    unittest.main()

