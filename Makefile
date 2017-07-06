all: dist/Chronos.app

dist/Chronos.app: env
	env/bin/python setup.py py2app

check:
	flake8 chronos 

format:
	find chronos -name '*.py' -print | xargs yapf -i

env:
	virtualenv env
	env/bin/python setup.py develop
	touch env

run: env
	env/bin/python script.py --loglevel debug

clean:
	rm -rf env build dist *.egg-info .eggs
	find . -name *.py[co] -delete
