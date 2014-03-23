import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

is_pypy = '__pypy__' in sys.builtin_module_names


def get_postgres_dependencies():
    if is_pypy:
#        psyco = 'psycopg2ct'
        return ['psycopg2cffi']
    else:
        return ['psycopg2']


requires = [
    'colorama',
    'deform_bootstrap',
    'dogpile.cache',
    'gunicorn',
    'horus',
    'mako',
    'pillow',
    'pycountry>=0.17',
    'pyelasticsearch',
    'pygeoip',
    'pyramid>=1.4.2',
    'pyramid_debugtoolbar',
    'pyramid_mailer',
    'pyramid_tm',
    'pyres',
    'pytz',
    'redis',
    'requests',
    'six',
    'sqlalchemy',
    'validictory',
    'waitress',
    'zope.sqlalchemy'
] + get_postgres_dependencies()

entry_points = """\
[paste.app_factory]
main = notaliens:main

[console_scripts]
notaliens = notaliens.scripts.notaliens_cmd:main
"""  # nopep8

setup(
    name='notaliens',
    version='0.0',
    description='notaliens',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python"
        "Framework :: Pyramid"
        "Topic :: Internet :: WWW/HTTP"
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
    ],
    author='John Anderson',
    author_email='sontek@gmail.com',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    test_suite="notaliens",
    entry_points=entry_points
)
