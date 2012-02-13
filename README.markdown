PYMASTER - A implementation of the quake 3 master server
========================================================
Depends on [Twisted](http://twistedmatrix.com)
The goal of this project is to provide a Quake 3 master server implementation.

Features:

 * A JSON API for getting servers (protocols/ serverlist/[protocol #] server/[host]/[port])
 * Queries Master Servers periodically to get a list of servers
 * All game client and game server communication with the master server is supported

TODO:

 * Stop abusive clients (UDP amplification)
 * Support the Darkplaces extension to the protocol
 * Geolocation of the servers in the JSON API?

Inspirations:
* [Server discovery for Quake III Arena, Wolfenstein Enemy Territory and Quake 4](http://en.scientificcommons.org/48909680)
* [dpmaster 2.2](http://icculus.org/twilight/darkplaces/download.html)
* [masterserver-0.4.1](http://src.gnu-darwin.org/ports/games/masterserver/work/masterserver-0.4.1/)

for usage:
`twistd pymaster --help`