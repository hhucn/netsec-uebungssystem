TODO
----

~~configuration file: Added support for config file, `config.ini`. Works for now, but for further development:~~

Moved from INI to JSON. :heavy_check_mark:

Dynamic rule configuration in `config.json` file (allowing creation of a workflow, ex: Move mails containing "Question" into a separate mailbox, auto-reply and notify a third person) :heavy_check_mark:

Dynamic template/variable configuration in `config.json` file (allowing dynamic reply e-mails) :heavy_check_mark:

Catch attachments :heavy_check_mark:

move into module (name? "mailyourhomework"?)

real-time IMAP notifications :heavy_check_mark: using IMAP `IDLE`

local test server with tests

Use MOVE extension to actually move emails :heavy_check_mark: (see `main.py:moveMails(...)`).

automatic replies (make sure that we don't actually answer our own or other automated emails!) :heavy_check_mark: `main.py:answerMails(...)`

alias domains (hhu.de / uni-duesseldorf.de)

manually configured aliases

~~local database (sqlite?) for ratings~~ local sqlite database to store attachments :heavy_check_mark:

~~(web/cli) interface to actually rate homework~~

**move from sqlite to actual directories/files due to sqlites size limit (0.9MB)?**

**tokens as authentication? Would make mail aliases obsolete and prevents mail spoofing.**
