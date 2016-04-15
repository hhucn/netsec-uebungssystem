from __future__ import unicode_literals

import argparse
import getpass
import logging
import os
import sys
import threading

from .config import Config

from . import mail_handler
from . import korrekturserver


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config",
        default="config.json", metavar="FILE", dest="config_path",
        help="Path to the config.json to be used")
    parser.add_argument(
        "-d", "--default",
        default="config_default.json", dest="config_default_path",
        help="Path to the config_default.json to be used")
    parser.add_argument(
        "--only-mail",
        dest="only_mail", action="store_true",
        help="Run the mail collecting server, but not the web server")
    parser.add_argument(
        "--only-web",
        dest="only_web", action="store_true",
        help="Run the web server, but not the mail collecting server")
    parser.add_argument(
        "-p", "--make-passhash",
        dest="make_passhash", action="store_true",
        help="Create a password hash to include in the configuration")
    args = parser.parse_args()

    config = Config.read(args.config_default_path, args.config_path)

    config.module_path = os.path.dirname(os.path.dirname(__file__))

    loglevel = getattr(logging, config("loglevel").upper())
    logfile = config('logfile')
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=loglevel,
        filename=logfile)
    logging.debug('Starting with command line %r' % sys.argv)

    if args.make_passhash:
        pw = getpass.getpass()
        if len(pw) < 10:
            raise ValueError('Password too short')
        pw2 = getpass.getpass('Repeat password: ')
        if pw != pw2:
            raise ValueError('Passwords are not equal!')
        from passlib.hash import pbkdf2_sha256
        print(pbkdf2_sha256.encrypt(pw))
        return 0

    if args.only_mail:
        mail_handler.mail_main(config)
        assert False, 'mail_main should never terminate'
    if args.only_web:
        korrekturserver.mainloop(config)
        assert False, 'mainloop should never terminate'

    mail_thread = threading.Thread(
        target=mail_handler.mail_main, args=(config,))
    mail_thread.daemon = True
    mail_thread.start()
    web_thread = threading.Thread(
        target=korrekturserver.mainloop, args=(config,))
    web_thread.daemon = True
    web_thread.start()

    mail_thread.join()
    assert False, 'mail server should never terminate'
