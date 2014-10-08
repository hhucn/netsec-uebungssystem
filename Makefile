test:
	pyflakes *.py
	pep8 --max-line-length=120 *.py

.PHONY: test

