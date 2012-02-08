'''
File: wolfutil.py
Author: Sigurd Fosseng
Description: Protocol utils
'''

from random import randint
from itertools import izip
from struct import unpack
from struct import pack

def build_challenge():
    """
    Build a challenge string for a "getinfo" message
    it is used to prevent spoofing of serveraddresses
    """
    def _rand_char():
        """ a random legal character """
        illegal = ["\\", ";", '"', "%", "/"]
        c = chr(randint(33,126))
        while c in illegal:
            c = chr(randint(33,126))
        return c

    #generate a random length challenge
    challenge = [_rand_char() for i in range(randint(9,12))]
    return ''.join(challenge)

def find_command(text):
    """
    Returns command and arguments, splits on the first non-normal
    character
    """
    for i, c in enumerate(text):
        if ord(c) <= ord(" ") or ord(c) == ord("\\"): # if it is not a normal character
           break # using i later

    command = text[:i]
    content = text[i:].lstrip("\n").lstrip("\\")
    return command, content

def infostring_to_dict(response):
    """takes a single line of infostring and creates a defaultdict"""
    info = response.split("\\")
    i = iter(info)
    infodict = dict(izip(i, i))
    return infodict

def statusresponse_to_dict(response):
    def extract_player_list(lines):
        players = []
        for p in lines:
            players.append(p.split(" ", 3)[-1])
        return players

    lines = response.split("\n")
    infodict = infostring_to_dict(lines[0])
    infodict["players"] = extract_player_list(lines[1:])
    return infodict

def pack_host(host, port):
    """
    Packs a host tuple according to the standard. AFAIK - Sigurd
    """
    values = map(int, host.split(".")) # the ip first
    values.append(port)
    return pack(">BBBBH", *values)

def unpack_host(string):
    data = unpack(">BBBBH", string)
    host = "%d.%d.%d.%d"% data[:-1]
    port = int(data[-1])
    return host, port
