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


def info(text):
    print("Info:\t{}".format(text))


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
