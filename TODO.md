test reconnecting if connection aborts
require mails to start with "Abgabe [Nr]"
add CSRF protection
switch to proper external stylesheet (<link rel>, will facilitate proper debugging / caching / highlighting etc.)
make sure to never use floats for points (use INTEGER tenths of a point instead)
rewrite database code as class

test with deliberately invalid UTF8
PGP (students / system)
Do away with html_path configuration option
fix rendering so that we can just include instead of ../htmldocs

move attachments into *one* folder instead of date-sorted attachments.
create a logfile per user to monitor changes on their contribution
send mail back with checksums of attachments
`def filter`: `email.message_from_string` accepts ASCII only. Rewrite.
