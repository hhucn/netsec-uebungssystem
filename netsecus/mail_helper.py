from __future__ import unicode_literals

import imaplib
import logging


def loginIMAP(server, address, password, ssl=True, debug=False):
    if not address or not password:
        err = "IMAP login information incomplete. (Missing address or password)"
        logging.error(err)
        raise ValueError(err)

    imapmail = create_imap_conn(server, ssl, debug)
    imapmail.login(address, password)
    logging.debug("IMAP login (%s on %s)" % (address, server))
    return imapmail


def logoutIMAP(imapmail):
    imapmail.close()
    imapmail.logout()
    logging.debug("IMAP logout")


def create_imap_conn(server, ssl, debug):
    if ssl:
        res = imaplib.IMAP4_SSL(server)
    else:
        res = imaplib.IMAP4(server)
    if debug:
        send_func = res.send
        read_func = res.read
        readline_func = res.readline

        def _debug_send(data):
            print('> %s' % data.decode('utf-8'), end='')
            return send_func(data)

        def _debug_read(size):
            res = read_func(size)
            print('< %s' % res.decode('utf-8'), end='')
            return res

        def _debug_readline():
            res = readline_func()
            print('< %s' % res.decode('utf-8'), end='')
            return res

        res.send = _debug_send
        res.read = _debug_read
        res.readline = _debug_readline

    return res
