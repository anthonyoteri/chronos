PYTHON ?= $(shell which python)

all: dist/Cronos.app

dist/Cronos.app:
	$(PYTHON) setup.py py2app

develop:
	$(PYTHON) setup.py py2app -A

test:
	$(PYTHON) setup.py test

check:
	flake8 timekeeper

env:
	virtualenv env
	env/bin/python setup.py develop
	touch env

run: env
	env/bin/python -m cronos.main --loglevel debug --config sample_config.yml

clean:
	rm -rf env build dist *.egg-info .eggs
	find . -name *.py[co] -delete
