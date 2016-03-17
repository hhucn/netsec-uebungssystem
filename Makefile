INSTALL_PACKAGE=pip3 install --user

test:
	flake8 .
	python3 -m unittest discover test/

install:
	${INSTALL_PACKAGE} passlib

run:
	@python3 -m netsecus

install-dev:
	flake8 --version >/dev/null 2>&1 || ${INSTALL_PACKAGE} install flake8

.PHONY: test run install install-dev

