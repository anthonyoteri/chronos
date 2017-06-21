import sys
from setuptools import setup, find_packages

from cronos import __NAME__, __VERSION__, __AUTHOR__

setup_requires = [
    'py2app',
    'pytest-runner',
]

install_requires = [
    'PyYAML',
]

tests_require = [
    'pytest',
    'pytest-mock',
]

setup(
    name=__NAME__,
    version=__VERSION__,
    packages=find_packages(),
    author=__AUTHOR__,
    author_email='anthony.oteri@gmail.com',
    description='Multi-project time clock',
    license='BSD',
    url='http://github.com/anthonyoteri/cronos',
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    app=['cronos/main.py'],
    options={
        'py2app': {
            'argv_emulation': True,
        }
    }
)
