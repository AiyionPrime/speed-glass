#!/usr/bin/env python3

import json
import requests
import struct
import socket


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
    info("Find default gateway...")
    dg = get_default_gateway_linux()
    info("Done.")
    info("Gateway found at {}.".format(str(dg)))
    info("Reading speedport status...")
    status = get_status(dg)
    info("Done.")
    info("got status:")
    print(json.dumps(status, indent=2))
