from notaliens.core.models import Base
from notaliens.core.models.translation import TranslatableMixin
from notaliens.core.models import JsonSerializableMixin
from notaliens.core.models.meta import Country
from notaliens.core.models.meta import Language
from notaliens.core.models.meta import Timezone
from notaliens.people import USER_INDEX
from notaliens.identity.models import User
from notaliens.cache.sa import FromCache
from notaliens.cache.sa import RelationshipCache
from notaliens.core.models.meta import GeoRegion
from notaliens.log import perflog


from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy.types import UnicodeText
from sqlalchemy.types import Unicode
from sqlalchemy.types import Integer
from sqlalchemy.types import Boolean
from sqlalchemy.types import Float
from sqlalchemy import Table
from sqlalchemy.orm import relationship
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from sqlalchemy import and_


import logging

logger = logging.getLogger(__name__)


user_languages = Table(
    'user_languages',
    Base.metadata,
    Column('profile_pk', Integer, ForeignKey('user_profile.pk')),
    Column('language_pk', Integer, ForeignKey(Language.pk))
)

user_skills = Table(
    'user_skills',
    Base.metadata,
    Column('profile_pk', Integer, ForeignKey('user_profile.pk')),
    Column('skill_tag_pk', Integer, ForeignKey('skill_tag.pk'))
)


class SkillTag(Base, TranslatableMixin, JsonSerializableMixin):
    __translatables__ = ["name"]
    name = Column(UnicodeText, nullable=False, unique=True)


class UserProfile(Base, TranslatableMixin, JsonSerializableMixin):
    __translatables__ = [
        'description', 'city', 'state'
    ]
    _json_eager_load = ['country', 'skills']

    user_pk = Column(Integer, ForeignKey('user.pk'))
    available_for_work = Column(Boolean, nullable=False, default=False)
    description = Column(UnicodeText, nullable=True)
    one_liner = Column(Unicode(140), nullable=False)
    first_name = Column(Unicode(255), nullable=True)
    last_name = Column(Unicode(255), nullable=True)
    blog_rss = Column(Unicode(255), nullable=True)
    twitter_handle = Column(Unicode(255), nullable=True)
    github_handle = Column(Unicode(255), nullable=True)
    city = Column(Unicode(255), nullable=True)
    state = Column(Unicode(255), nullable=True)
    postal = Column(Unicode(255), nullable=True)
    country_pk = Column(Integer, ForeignKey(Country.pk), nullable=True)
    country = relationship(Country)
    languages = relationship(Language, secondary=user_languages)
    timezone_pk = Column(Integer, ForeignKey(Timezone.pk), nullable=True)
    timezone = relationship(Timezone)
    skills = relationship("SkillTag", secondary=user_skills)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    @property
    def display_name(self):
        if self.first_name and self.last_name:
            return '%s %s' % (
                self.first_name,
                self.last_name
            )
        elif self.first_name and not self.last_name:
            return self.first_name
        else:
            return self.user.username

    def __json__(self, request):
        results = JsonSerializableMixin.__json__(self, request)

        results['location'] = {
            'lat': self.latitude,
            'lon': self.longitude
        }

        return results


@perflog()
def get_user_by_username(
        session, username, with_profile=True, from_cache=True
):

    query = session.query(User).filter(
        User.username == username
    )

    if with_profile:
        query = query.options(joinedload('profile'))

    if from_cache:
        query = query.options(FromCache())
        query = query.options(RelationshipCache(User.profile))

    user = query.one()

    return user


def get_users(request, search_text=None, distance_settings=None, page=0,
              limit=50):
    """ This will get the users limited by `page` and `limit`.  It will
    return a dict of the total users and the limited paged results.

    For example:

        {
            'count': 1,
            'users': [ ... ]
        }
    """

    def db_wrapper(*args, **kwargs):
        users = get_users_from_db(request.db_session, page, limit, search_text)

        if search_text:
            count = len(users)
        else:
            count = get_user_count_from_db(request.db_session)

        return {
            'count': count,
            'users': [u.__json__(request) for u in users]
        }

    if request.search_settings['enabled']:
        results = get_users_from_es(
            request.es,
            page,
            limit,
            fallback=db_wrapper,
            search_text=search_text,
            distance_settings=distance_settings)
        return results
    else:
        return db_wrapper()


@perflog()
def get_user_count_from_db(session):
    query = session.query(func.count(User.pk))

    results = query.one()

    return results[0]


@perflog()
def get_users_from_db(session, page, limit, search_text=None):
    """ This queries the database for the user and his profile,
    it will cache the query to redis if possible
    """

    query = session.query(User)
    query = query.options(joinedload('profile'))

    if search_text:
        like_format = '%' + search_text + '%'
        query = query.filter(
            and_(
                or_(
                    User.username.like(like_format),
                    User.email.like(like_format),
                    UserProfile.first_name.like(like_format),
                    UserProfile.last_name.like(like_format)
                ),
                UserProfile.user_pk == User.pk
            )
        )

    query = query.options(FromCache())
    query = query.options(RelationshipCache(User.profile))

    if limit:
        query = query.limit(limit)

    if page and limit:
        offset = page * limit
        query = query.offset(offset)

    users = query.all()

    return users


@perflog()
def get_users_from_es(es, page, limit, fallback=None, search_text=None,
                      distance_settings=None):
    query = {
        'from': page,
        'size': limit
    }

    if search_text or distance_settings:
        query['query'] = {}

    if search_text:
        search_text = search_text.lower()
        query['query'] = {
            'multi_match': {
                'query': search_text,
                'fields': ['first_name', 'last_name', 'email', 'name']
            },
        }

    if distance_settings:
        query['query']['filtered'] = {
            'filter': {
                'geo_distance': {
                    'distance': '%smi' % distance_settings['distance'],
                    'location': {
                        'lat': distance_settings['lat'],
                        'lon': distance_settings['lon']
                    }
                }
            }
        }

    results = es.search(query, fallback=fallback, index=USER_INDEX)
    # we got our data from elastic search
    if 'hits' in results:
        count = results['hits']['total']
        users = []

        for hit in results['hits']['hits']:
            users.append(hit['_source'])

        return {
            'count': count,
            'users': users
        }

    else:
        return results


def refresh_users_location(db_session):
    regions = db_session.query(GeoRegion).all()

    regions_dict = {}

    for region in regions:
        regions_dict[region.postal_code] = region

    users = db_session.query(UserProfile).all()

    countries_dict = {}
    countries = db_session.query(Country).all()

    for country in countries:
        countries_dict[country.alpha2] = country

    for user in users:
        try:
            postal_data = regions_dict[user.postal]
            user.latitude = postal_data.latitude
            user.longitude = postal_data.longitude
            user.city = postal_data.city
            user.state = postal_data.region
            user.country = countries_dict[postal_data.country]
        except KeyError:
            logger.warn("Couldn't find info for %s" % user.postal)

        db_session.add(user)
