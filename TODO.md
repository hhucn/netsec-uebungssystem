Korrekturen absenden
	Neuer Menü-Punkt
	Neues Flag in der Datenbank versendet
	Mails generieren, Voransicht im Menüpunkt
	Mails versenden
	abgesendete Mails in den Sent-Ordner schieben
Bei Änderung der Korrektur versendet-flag löschen
make sure we store submission email
	write an update script

create view newest_grading_result
support multiple grading_results
move to new data structure grading_results
Bei teilweiser Korrektur erscheint als fertig
mass assigment
Übersicht -> Meine Korrekturen
tornado listen nur localhost (mit Konfigurationsoption)
Bei Abgabe Punktzahl/Status der bisherigen Übungen anzeigen
Übersicht über alle Abgaben eines Blatts inkl. Link auf Korrektur
merge students; actually use alias as intended
Antwortmail auf Abgabe sollte Größen/hashes aller Dateien enthalten
Links unter Student auf Abgabe falsch
Antwortmail sollte alle Punkte bisher enthalten
Übersicht der Punkte pro Student in der Weboberfläche
switch to nedb-like interface? (Discuss with Martin)

script to autorestart on changes
RequestHandlerWithAuth should store user id, do not parse it twice
move submission handling out of commands into a better-named module (how about submission?)
test with subject "AbgabeFoo"
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
also send text email
alias should contain umlauts (not encoded stuff)
