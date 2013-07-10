notaliens.com
=============

A website for show casing pyramid powered sites and the hackers that use it!

The site is a combination of these namespaced packages:
    - notaliens.core: Shared templates and assets
    - notaliens.identity: An oauth provider service to allow the other sections of the website to verify the identity of
        a user. It is also an oauth client to allow users to identify themselves via social networks.
    - notaliens.people: The section of the site that manages the list of Pyramid developers and their user profiles
    - notaliens.sites: The section of the site dedicated to managing the list of Pyramid powered websites
    - notaliens.jobs: The section of the website dedicated to posting and searching for Pyramid jobs


We are written with Python 3.3 and Python 2.7 in mind.


Features
============

We should have a mix of features that are similar to http://djangosites.org and
http://people.djangoproject.com/



# People
- Developers should be able to register accounts, list their basic profile information
such as github, twitter, and linked in, along with their location and if they are looking
for work. They should also be able to tag themselves for what type of technology
they work with.


# Sites
- Registered users should be able to add 'sites' that are powered by Pyramid.
This will include adding screenshots, tags for type of site, URL, should have stats
about backend db (pgsql, redis, etc), what server is used (nginx, gunicorn), OS, and
released version.  What spoken language it is in.


# Jobs
- This will be for people to post up jobs that are pyramid related


Getting Started
==================================
    $ easy_install -U setuptools
    $ python bootstrap.py


Before running buildout, you need to make sure you have postgresql installed.

## Fedora

    $ sudo yum install postgresql-server postgresql-devel
    $ sudo su - postgres
    $ initdb
    $ exit
    $ sudo systemctl start postgresql.service

## Ubuntu

    $ sudo apt-get install postgresql postgresql-dev
    $ sudo su - postgres
    $ initdb
    $ exit
    

## Finally

    $ sudo su - postgres
    $ createuser -s <your user name>
    $ exit
    $ createdb notaliens
    $ bin/buildout
    $ bin/notaliens_create_db notaliens/development.ini
    $ bin/notaliens_update_geoip notaliens/development.ini


We also have support for caching SQL queries via redis and using elasticsearch
for full text search, so use your distro to install those if you would like
to take advantage of those features.


You will notice on the view timings that we are running at about 30-40ms per view,
this is not an accurate number because we enable the debugtoolbar by default.

With the toolbar off we average around 10-15ms per view request.


Elastic Search
==================================
To test the elastic search:

Profile Schema:

    curl -XGET 'http://127.0.0.1:9200/profiles/_mapping?pretty=1'

All profiles:

    curl -XGET 'http://127.0.0.1:9200/profiles/_search?pretty=1'


Filter Profile:

    curl -XGET 'http://127.0.0.1:9200/profiles/person/_search?q=first_name:john'

Or for more advanced querying:

    curl -XPOST 'http://127.0.0.1:9200/profiles/person/_search?pretty=true' -d'
    {
        "query":{
            "term" : {
                "first_name" :"john"
            }   
        }
    }
    '
