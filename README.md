Homework grading system for netsec
==================================

Installation
============

```
sudo apt-get install -y git make python3
git clone https://github.com/hhucn/netsec-uebungssystem.git
make deps
sudo make install-service # To start automatically
```

Debugging tips
==============

```
$ openssl s_client -crlf -connect imap.gmail.com:993
```

Command to start the mail filter system:
```
$ python -m netsecus --only-mail
```

Command to start the web grading server:
```
$ python -m netsecus --only-web
```