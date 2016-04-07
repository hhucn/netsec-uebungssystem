sheet broken (Philipp)
submissions (Martin)

Until Monday:
Korrekturen (Martin)
send simple confirmation mail (Martin)
set up server (Philipp)

Übersicht über alle Abgaben eines Blatts inkl. Link auf Korrektur
Übersicht über die Korrekturen
merge students; actually use alias as intended
require mails to start with "Abgabe [Nr]"
tag mail if exception occurs

move submission handling out of commands into a better-named module (how about submission?)
test with subject "AbgabeFoo"
fix travis
test with deliberately valid/invalid UTF8
PGP (students / system)
Do away with html_path configuration option
fix rendering so that we can just include instead of ../htmldocs
allow non-caching of templates (so that we can change templates and immediately see differences)
improve point rendering (human-readable)
Abgabefrist als Timestamp
move attachments into *one* folder instead of date-sorted attachments.
create a logfile per user to monitor changes on their contribution
send mail back with checksums of attachments
`def filter`: `email.message_from_string` accepts ASCII only. Rewrite.
Abgabestring in die Konfiguration
test 2 mails coming in at the same second
improve error handling (mark mail before saving/doing anything, do not retry if mark present)
