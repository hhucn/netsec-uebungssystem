INSTALL_PACKAGE=pip3 install --user

test:
	python3 -m unittest discover test/
	@$(MAKE) lint

lint:
	flake8 .

deps:
	${INSTALL_PACKAGE} setuptools
	${INSTALL_PACKAGE} passlib tornado jinja2

install-service:
	systemctl stop netsecus || true
	sed -e "s,%LOCATION%,$${PWD}," <netsecus.service >/etc/systemd/system/netsecus.service  # Make sure to run as root
	chmod a+x /etc/systemd/system/netsecus.service
	systemctl enable netsecus
	systemctl start netsecus

uninstall-service:
	systemctl stop netsecus || true
	systemctl disable netsecus
	rm -f /etc/systemd/system/netsecus.service

run:
	@python3 -m netsecus

deps-dev: deps
	flake8 --version >/dev/null 2>&1 || ${INSTALL_PACKAGE} install flake8

.PHONY: lint test run install install-dev install-service uninstall-service
