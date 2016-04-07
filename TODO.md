

Workflow Abgabe per E-Mail
	Speichern
	Verschieben in Unterordner
	Anzeigen in der Oberfläche
	Download der Dateien
Workflow Korrektur
Neue Pfad-Struktur für Abgaben submissions/<student>/<Blatt>/<timestamp>/{mail, alle dateien}


Übersicht über alle Abgaben eines Blatts inkl. Link auf Korrektur
Übersicht über die Korrekturen


improve error handling (mark mail before saving/doing anything, do not retry if mark present)

require mails to start with "Abgabe [Nr]"
make sure to never use floats for points (use INTEGER tenths of a point instead)
tag mail if exception occurs
reimplement answer

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
