#!/usr/bin/env python3

from getpass import getpass
from hashlib import sha256
from json import dumps
from json import loads
from logging import getLogger
from pathlib import Path
from re import findall
from re import search
from re import sub
from requests import get
from requests import post
from requests import Session
from socket import inet_ntoa
from struct import pack
from sys import argv

log = getLogger(__name__)


def challenge(address):
    chall_url = "http://{}/html/login/index.html".format(address)
    regex = r"challenge\s=\s\"(.*)\";"
    response = get(chall_url)
    matches = search(regex, response.text)
    if matches:
        firstgroup = matches.groups()[0]
        chall = matches.group(1)
        log.debug(chall)
        return chall


def hash_pw(challenge, password):
    concat = "{}:{}".format(challenge, password)
    hashed = sha256(concat.encode('utf-8')).hexdigest()
    log.debug("hashed: {}".format(hashed))
    return hashed


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
            return inet_ntoa(pack("<L", int(fields[2], 16)))


def get_dhcp_listing(session):
    res = session.get("http://{}/data/LAN.json".format(dg))
    broken_json = res.text
    repaired = remove_trailing_comma(broken_json)
    obj = loads(repaired)

    listing = []

    for entry in obj:
        if "template" == entry["vartype"]:
            if "addmdevice" == entry["varid"]:
                continue
            listed = entry["varvalue"]
            listing.append(Listing(listed))
    return listing


def get_status(address):
    status_url = "http://{}/data/Status.json".format(address)
    response = get(status_url)
    return response.json()


def login(session, dg, passwd):
    login_url = "http://{}/data/Login.json".format(dg)
    chall = challenge(dg)
    hashpw = hash_pw(chall, passwd)
    payload = {
            "csrf_token": "nulltoken",
            "password": hashpw,
            "showpw": 0,
            "challengev": chall}
    post = session.post(login_url, data=payload)


def remove_trailing_comma(speedport_mess):
    """
    Remove the last trailing comma in wrongly concatenated JSON-arrays

    this makes the speedports lan.json valid JSON again.
    https://twitter.com/Aiyion/status/1359080085706391554
    """
    regex = r"(})(,)(\s*\]\s*\Z)"
    result = sub(regex, r"\1 \3", speedport_mess, 0)
    log.debug(result)
    return result


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
        string_list = findall(r'\d+', header_format)
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
            print(dumps(status, indent=2))
            exit(0)
        else:
            log.error("Unknown argument {}".format(argv[1]))
            exit(1)
    passwd = open_pass(".")
    if passwd is None:
        passwd = getpass('Please enter the password of the speedport '
                         'located at {}: '.format(dg))

    s = Session()
    login(s, dg, passwd)

    listing = get_dhcp_listing(s)

    print(Listing.header())

    for each in listing:
        print(each.row())
