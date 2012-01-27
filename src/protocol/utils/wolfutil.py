'''
File: q3util.py
Author: Sigurd Fosseng
Description: Protocol utils
'''

from random import randint

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
    """ returns command and arguments, splits on the first non-normal character"""
    index = 0
    for i, c in enumerate(text):
        if ord(c) <= ord(" "): # if it is not a normal character
           index = i
           break
    return text[:i], text[i:]

def infostring_to_dict(infostring):
    """ search an infostring for a key """
    def _player_list(playerlist):
        players = []
        for p in playerlist:
            players.append(p.split(" ", 3)[-1])
        return players

    infostring = infostring.split("\n")
    infolist  = infostring[1].split("\\")
    playerlist = infostring[2:]

    infodict = {}
    for i in range(1, len(infolist), 2):
        infodict[infolist[i]] = infolist[i+1]

    infodict["players"] = _player_list(playerlist)
    return infodict
