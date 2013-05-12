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


We are written with only Python 3.3 in mind.


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

    $ python bootstrap.py
    $ bin/buildout
