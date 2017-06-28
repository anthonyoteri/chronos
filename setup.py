
import sys
from setuptools import setup, find_packages

from chronos import __NAME__, __VERSION__, __AUTHOR__


setup_requires = [
    'py2app',
    'pytest-runner',
]

install_requires = [
    'alembic==0.9.2',
    'chardet==3.0.4',
    'dataset==0.8.0',
    'Mako==1.0.6',
    'MarkupSafe==1.0',
    'normality==0.4.4',
    'python-dateutil==2.6.0',
    'python-editor==1.0.3',
    'PyYAML==3.12',
    'six==1.10.0',
    'SQLAlchemy==1.1.11',
    'wheel==0.26.0',
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
    description='time clock',
    license='BSD',
    url='http://github.com/anthonyoteri/chronos',
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    app=['script.py'],
    options={
        "py2app": {
            "includes": ["sqlalchemy.dialects.sqlite",
                         "sqlalchemy.sql.default_comparator"],
            "argv_emulation": False,
            'plist': {
                'CFBundleName': __NAME__,
                'CFBundleDisplayName': __NAME__,
                'CFBundleGetInfoString': 'Time tracking',
                'CFBundleVersion': __VERSION__,
                'CFBundleShortVersionString': __VERSION__,
                'NSHumanReadableCopyright': (u'Copyright (C) 2017, Anthony '
                                             'Oteri.  All rights reserved.'),
            },
        }
    },
)
