import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'colorama'
    , 'deform_bootstrap'
    , 'dogpile.cache'
    , 'horus'
    , 'mako'
    , 'psycopg2'
    , 'pycountry'
    , 'pyramid_mailer'
    , 'pyramid>=1.4.2'
    , 'pyramid_debugtoolbar'
    , 'pytz'
    , 'redis'
    , 'six'
    , 'sqlalchemy'
    , 'validictory'
    , 'gunicorn'
]

setup(
    name='notaliens'
    , version='0.0'
    , description='notaliens'
    , long_description=README + '\n\n' + CHANGES
    , classifiers=[
        "Programming Language :: Python"
        "Framework :: Pyramid"
        "Topic :: Internet :: WWW/HTTP"
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
    ]
    , author='John Anderson'
    , author_email='sontek@gmail.com'
    , url=''
    , keywords='web pyramid pylons'
    , packages=find_packages()
    , include_package_data=True
    , zip_safe=False
    , install_requires=requires
    , tests_require=requires
    , test_suite="notaliens"
    , entry_points="""\
    [paste.app_factory]
    main = notaliens:main

    [console_scripts]
    notaliens_create_db = notaliens.scripts.create:main
    """
)
