#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path
import codecs
import os
import re
import sys


# When creating the sdist, make sure the django.mo file also exists:
if 'sdist' in sys.argv or 'develop' in sys.argv:
    os.chdir('oscar_docdata')
    try:
        from django.core import management
        management.call_command('compilemessages', stdout=sys.stderr, verbosity=1)
    except ImportError:
        if 'sdist' in sys.argv:
            raise
    finally:
        os.chdir('..')


def read(*parts):
    file_path = path.join(path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding='utf-8').read()


def find_version(*parts):
    version_file = read(*parts)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return str(version_match.group(1))
    raise RuntimeError("Unable to find version string.")


setup(
    name='django-oscar-docdata',
    version=find_version('oscar_docdata', '__init__.py'),
    license='Apache 2.0',

    install_requires=[
        'suds-jurko>=0.6',             # for SOAP requests. (suds-jurko = maintained fork of suds)
        'django-oscar>=0.5',           # version number guessed
        'django-polymorphic>=0.5.3',   # 0.5.1 has Django 1.6 support, but ask for the latest bugfix release.
        'six>=1.10.0',                 # python3 compatibility
    ],
    requires=[
        'Django (>=1.4)',
    ],

    description='Docdata Payments Gateway integration for django-oscar',
    long_description=read('README.rst'),

    author='Diederik van der Boor',
    author_email='opensource@edoburu.nl',

    url='https://github.com/django-oscar/django-oscar-docdata',
    download_url='https://github.com/django-oscar/django-oscar-docdata/zipball/master',

    packages=find_packages(exclude=('example*','sandbox*')),
    include_package_data=True,

    #test_suite = 'runtests',

    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
