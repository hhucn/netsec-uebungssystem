from __future__ import unicode_literals


import os
import sys

if not __package__:
    # direct call of korrekturserver.py
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(os.path.dirname(path)))
    sys.path.append(os.path.dirname(path))


if len(sys.argv) >= 2:
    if sys.argv[1] == "client":
        sys.argv.remove("client")
        from .korrekturclient import korrekturclient
        korrekturclient.main()
        sys.exit(1)
    elif sys.argv[1] == "server":
        sys.argv.remove("server")
        from .korrekturserver import korrekturserver
        korrekturserver.main()
        sys.exit(1)

print("Usage: %s [client/server]" % sys.argv[0])
