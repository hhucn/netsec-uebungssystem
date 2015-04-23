from __future__ import unicode_literals


import os
import sys

if not __package__:
    # direct call of korrekturserver.py
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(os.path.dirname(path)))
    sys.path.append(os.path.dirname(path))


def _main():
    from . import main
    sys.exit(main())

_main()
