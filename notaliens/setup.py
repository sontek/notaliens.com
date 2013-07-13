import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'colorama',
    'deform_bootstrap',
    'dogpile.cache',
    'gunicorn',
    'horus',
    'mako',
    'psycopg2',
    'pycountry>=0.17',
    'pyelasticsearch',
    'pygeoip',
    'pyramid>=1.4.2',
    'pyramid_debugtoolbar',
    'pyramid_mailer',
    'pytz',
    'redis',
    'requests',
    'six',
    'sqlalchemy',
    'validictory',
    'pyres'
]
entry_points = """\
[paste.app_factory]
main = notaliens:main

[console_scripts]
notaliens_create_db = notaliens.scripts.create:main
notaliens_update_geoip = notaliens.scripts.geoip:update
notaliens_update_geoip_csv = notaliens.scripts.geoip_csv:update
notaliens_rebuild_index = notaliens.scripts.reindex:main
notaliens_refresh_location = notaliens.scripts.refresh_user_location:update
notaliens_task_queue = notaliens.tasks.worker:main
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
