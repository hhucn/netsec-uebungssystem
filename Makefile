INSTALL_PACKAGE=pip3 install --user

test:
	flake8 .
	python3 -m unittest discover test/

deps:
	${INSTALL_PACKAGE} setuptools
	${INSTALL_PACKAGE} passlib tornado

install-service:
	sed -e "s,%LOCATION%,${PWD}," <netsecus.service >//netsecus.service  # Make sure to run as root
	chmod a+x /etc/init.d/netsecus
	service netsecus start

run:
	@python3 -m netsecus

deps-dev: deps
	flake8 --version >/dev/null 2>&1 || ${INSTALL_PACKAGE} install flake8

.PHONY: test run install install-dev install-service

