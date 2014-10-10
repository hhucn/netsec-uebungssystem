CHANGELOG
---------

_Oct 10, 2014_

* Configuration file type is now JSON
* Created own `search` engine because the IMAP search command is case-sensitive
* `answerMails` now flags answered mails as "answered" (`NETSEC-ANSWERED`) so we don't spam someone if the mail isn't moved away.
* `moveMails` now creates the destination mailbox if it doesn't exist.
* Added another loglevel:
	* `1` Fatal errors (ex. login failed)
	* `2` Non-fatal errors (ex. mail movement failed)
	* `3` Information (ex. login successful)
* Added support for a logfile. `logmethod` may be 1 (STDOUT), 2 (File) or 3 (both)


_Oct 09, 2014_

* Added configuration file support, plus example configuration file (`Example config.ini`)
* Added multiple log levels (0-2)
* Re-structured code
* Automatic reply for incoming mails
* `moveMails` actually moves mails!
* patched `imaplib` for `MOVE` support. (ugh)




_Oct 06, 2014_

* Init.