#!/usr/bin/env python
from __future__ import unicode_literals

import sys

if not __package__:
    # direct call of __main__.py
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(os.path.dirname(path)))

if __name__ == '__main__':
    import netsecus
    netsecus.main()
