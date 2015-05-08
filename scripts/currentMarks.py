from __future__ import unicode_literals


def run(config, imapmail, mails, *args):
    print("script rule works. Handed args: (%s)" % ", ".join(args))

    return mails
