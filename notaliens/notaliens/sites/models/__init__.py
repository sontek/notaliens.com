from notaliens.core.models import Base
from notaliens.core.models.translation import TranslatableMixin
from notaliens.core.models import JsonSerializableMixin
from notaliens.cache.sa import FromCache
from notaliens.log import perflog

from sqlalchemy import ForeignKey
from sqlalchemy import or_
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import func
from sqlalchemy.types import UnicodeText
from sqlalchemy.types import Unicode
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship

import logging

logger = logging.getLogger(__name__)

site_tags = Table(
    'site_tags',
    Base.metadata,
    Column('site_pk', Integer, ForeignKey('site.pk')),
    Column('site_tag_pk', Integer, ForeignKey('site_tag.pk')),
)

class SiteTag(Base, JsonSerializableMixin, TranslatableMixin):
    __translatables__ = ['name']
    name = Column(UnicodeText, nullable=False, unique=True)


class Site(Base, JsonSerializableMixin, TranslatableMixin):
    __translatables__ = [
        'description',
        'title',
    ]

    url = Column(Unicode(255), nullable=False)
    description = Column(UnicodeText, nullable=False)
    title = Column(UnicodeText, nullable=False)
    tags = relationship("SiteTag", secondary=site_tags)

    owner_pk = Column(Integer, ForeignKey('user.pk'))

    def __json__(self, request):
        results = JsonSerializableMixin.__json__(self, request)
        return results

@perflog()
def get_site_by_pk(session, site_pk, from_cache=True):
    query = session.query(Site).filter(Site.pk == site_pk)
    if from_cache:
        query = query.options(FromCache())

    site = query.one()

    return site

@perflog()
def get_sites_from_db(session, page, limit, search_text=None):
    """ Query the database for sites, it will cache the query
    to redis if possible
    """

    query = session.query(Site)

    if search_text:
        like_format = '%' + search_text + '%'
        query = query.filter(
            or_(
                Site.url.like(like_format),
                Site.description.like(like_format),
            )
        )

    query = query.options(FromCache())

    if limit:
        query = query.limit(limit)

    if page and limit:
        offset = page * limit
        query = query.offset(offset)

    return query

@perflog()
def get_site_count_from_db(session):
    query = session.query(func.count(Site.pk))

    results = query.one()

    return results[0]

def get_sites(request, search_text=None, page=0, limit=50):
    """ This will get the sites limited by `page` and `limit`.  It will
    return a dict of the total sites and the limited paged results.

    For example:

        {
            'count': 1,
            'sites': [ ... ]
        }
    """

    def db_wrapper(*args, **kwargs):
        sites = get_sites_from_db(request.db_session, page, limit, search_text)

        if search_text:
            count = len(sites)
        else:
            count = get_site_count_from_db(request.db_session)

        return {
            'count': count,
            'sites': [s.__json__(request) for s in sites]
        }

    # Implement elastic search stuff here
    # TODO

    return db_wrapper()

