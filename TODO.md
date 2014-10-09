TODO
----

~~configuration file~~ Added support for config file, `config.ini`. Works for now, but for further development:

Move from INI to JSON.

move into module (name? "mailyourhomework"?)

real-time IMAP notifications

local test server with tests

~~Use MOVE extension to actually move emails~~ Implemented (see `main.py:69`).

~~automatic replies (make sure that we don't actually answer our own or other automated emails!)~~ Implemented. `main.py:41..50`

alias domains (hhu.de / uni-duesseldorf.de)

manually configured aliases

local database (sqlite?) for ratings

(web/cli) interface to actually rate homework
