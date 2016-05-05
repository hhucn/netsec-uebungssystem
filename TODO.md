Teste Änderung der Korrektur nach Herausschicken an den Studenten
alte Abgaben von Studenten fehlen (immer nur neuestes Blatt)!
Übersicht sollte wie Abgaben aussehen (gleiches Template nehmen, Punkte in beiden Seiten einbauen)
Bei Änderung der Korrektur grading_results neu erstellen (altes lassen, stattdessen view erstellen die immer nur das neueste grading_result anzeigt, und diese view verwenden)
upload sent mails via IMAP
fix auf nicht zugewiesen setzen (setzt im Moment leer)

Erlaube manuelles Einreichen (oder besseren Workflow für Leute die die Abgaben als Antwort oder an hagemeister@cs schicken)
Korrekturmails mit SHA-Summen/Dateigrößen etc.
Bei Studenten Gesamtpunktzahl über alle Blätter inkl. Prozent anzeigen
Bei Korrekturen Gesamtpunktzahl über alle Blätter inkl. Prozent anzeigen
mass assigment von Korrekturen (assign first [input type="num" value="10"] unassigned to ...)

handle errors when sending mail
create view newest_grading_result
support multiple grading_results over time
move to new data structure grading_results
Bei teilweiser Korrektur erscheint als fertig
tornado listen nur localhost (mit Konfigurationsoption)
Bei Abgabe Punktzahl/Status der bisherigen Übungen anzeigen
Übersicht über alle Abgaben eines Blatts inkl. Link auf Korrektur
merge students; actually use alias as intended
Antwortmail auf Abgabe sollte Größen/hashes aller Dateien enthalten
switch to nedb-like interface for grading_results? (Discuss with Martin)

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
