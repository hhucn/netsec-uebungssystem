test:
	pyflakes *.py
	pep8 --max-line-length=120 *.py
	python -m unittest discover test/

.PHONY: test

