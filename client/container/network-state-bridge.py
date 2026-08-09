#!/usr/bin/env python3
"""Private, read-only subset of org.freedesktop.NetworkManager for Steam."""

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

BUS_NAME = "org.freedesktop.NetworkManager"
OBJECT_PATH = "/org/freedesktop/NetworkManager"
NM = BUS_NAME
PROPERTIES = "org.freedesktop.DBus.Properties"
OBJECT_MANAGER = "org.freedesktop.DBus.ObjectManager"


class NetworkState(dbus.service.Object):
    values = {
        "Version": dbus.String("pontifex-read-only"),
        "State": dbus.UInt32(70),  # NM_STATE_CONNECTED_GLOBAL
        "Connectivity": dbus.UInt32(4),  # NM_CONNECTIVITY_FULL
        "Startup": dbus.Boolean(False),
        "NetworkingEnabled": dbus.Boolean(True),
        "WirelessEnabled": dbus.Boolean(False),
        "WirelessHardwareEnabled": dbus.Boolean(False),
        "WwanEnabled": dbus.Boolean(False),
        "WwanHardwareEnabled": dbus.Boolean(False),
        "CheckConnectivityAvailable": dbus.Boolean(False),
        "Devices": dbus.Array([], signature="o"),
        "AllDevices": dbus.Array([], signature="o"),
        "ActiveConnections": dbus.Array([], signature="o"),
    }

    @dbus.service.method(NM, in_signature="", out_signature="ao")
    def GetDevices(self):
        return dbus.Array([], signature="o")

    @dbus.service.method(NM, in_signature="", out_signature="ao")
    def GetAllDevices(self):
        return dbus.Array([], signature="o")

    @dbus.service.method(NM, in_signature="", out_signature="u")
    def CheckConnectivity(self):
        return dbus.UInt32(4)

    @dbus.service.method(PROPERTIES, in_signature="ss", out_signature="v")
    def Get(self, interface, name):
        if interface != NM or name not in self.values:
            raise dbus.exceptions.DBusException("org.freedesktop.DBus.Error.InvalidArgs")
        return self.values[name]

    @dbus.service.method(PROPERTIES, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface != NM:
            return {}
        return self.values

    @dbus.service.method(OBJECT_MANAGER, in_signature="", out_signature="a{oa{sa{sv}}}")
    def GetManagedObjects(self):
        return {OBJECT_PATH: {NM: self.values}}


DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
name = dbus.service.BusName(BUS_NAME, bus=bus)
state = NetworkState(bus, OBJECT_PATH)
GLib.MainLoop().run()
