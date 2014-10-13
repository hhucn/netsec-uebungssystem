TODO
----

~~configuration file~~ Added support for config file, `config.ini`. ~~Works for now, but for further development:~~

~~Move from INI to JSON.~~

~~Dynamic rule configuration in `config.json` file (allowing creation of a workflow, ex: Move mails containing "Question" into a separate mailbox, auto-reply and notify a third person)~~ aww yeah.

Time to write a small README to understand the configuration and possibilities in rule creation :blush:

Catch attachments

move into module (name? "mailyourhomework"?)

real-time IMAP notifications

local test server with tests

~~Use MOVE extension to actually move emails~~ Implemented (see `main.py:moveMails(...)`).

~~automatic replies (make sure that we don't actually answer our own or other automated emails!)~~ Implemented. `main.py:answerMails(...)`

alias domains (hhu.de / uni-duesseldorf.de)

manually configured aliases

local database (sqlite?) for ratings

(web/cli) interface to actually rate homework
