#!/usr/bin/env python3

from getpass import getpass
from pathlib import Path
from sys import argv
import json
import logging
import requests
import struct
import socket

log = logging.getLogger(__name__)


def open_pass(path):
    try:
        with open(".speedport_password", "r") as speedpw_file:
            passwd = speedpw_file.readline().strip()
            return passwd
    except FileNotFoundError:
        try:
            cfgpath = "{}/.config/speedport/.password".format(str(Path.home()))
            with open(cfgpath, "r") as speedpw_file:
                passwd = speedpw_file.readline().strip()
                return passwd
        except FileNotFoundError:
            pass


def get_default_gateway_linux():
    """Read the default gateway directly from /proc."""
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue
            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))


def get_status(address):
    status_url = "http://{}/data/Status.json".format(address)
    response = requests.get(status_url)
    return response.json()


class Listing:
    _formatting = "{:<17}  {:<15}  {:<3}  {:<25}  {:<19}  {:>8}  {:>11}"

    def __init__(self, crude):
        prefix = "mdevice_"
        _ressources = ["mac", "name", "ipv4", "fix_dhcp", "ipv6",
                       "connected", "type"]
        concat = [prefix + r for r in _ressources]
        for entry in crude:
            if entry["varid"] in concat:
                setattr(self, entry["varid"], entry["varvalue"])

    @property
    def connection(self):
        if self.mdevice_connected == "0":
            return "lost"
        if self.mdevice_connected == "1":
            return "established"

    @property
    def physical(self):
        if self.mdevice_type == "0":
            return "wired"
        if self.mdevice_type == "1":
            return "2.4 GHz"
        if self.mdevice_type == "2":
            return "5 GHz"

    def __repr__(self):
        return "Listing<{}>".format(self.mdevice_mac)

    def row(self):
        return self._formatting.format(self.mdevice_mac,
                                       self.mdevice_ipv4,
                                       self.mdevice_fix_dhcp,
                                       self.mdevice_name,
                                       self.mdevice_ipv6,
                                       self.physical,
                                       self.connection)

    @classmethod
    def header(cls):
        header_format = cls._formatting.replace(">", "<")
        string_list = re.findall(r'\d+', header_format)
        int_list = [int(i) for i in string_list]
        int_list.append(header_format.count(" "))
        top_row = header_format.format("mac", "ipv4", "fix", "hostname",
                                       "ipv6", "physical", "connection")
        return "{}\n{}".format(top_row, sum(int_list)*"-")


if "__main__" == __name__:
    log.info("Find default gateway...")
    dg = get_default_gateway_linux()
    log.info("Done.")
    log.info("Gateway found at {}.".format(str(dg)))
    if len(argv) > 1:
        if "--info" == argv[1]:
            log.info("Reading speedport status...")
            status = get_status(dg)
            log.info("Done.")
            log.info("got status:")
            print(json.dumps(status, indent=2))
            exit(0)
        else:
            log.error("Unknown argument {}".format(argv[1]))
            exit(1)
    passwd = open_pass(".")
    if passwd is None:
        passwd = getpass('Please enter the password of the speedport '
                         'located at {}: '.format(dg))
    print(Listing.header())
