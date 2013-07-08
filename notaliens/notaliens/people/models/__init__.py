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
from notaliens.log import perflog


from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy.types import UnicodeText
from sqlalchemy.types import Unicode
from sqlalchemy.types import Integer
from sqlalchemy import Table
from sqlalchemy.orm import relationship
from sqlalchemy.orm import joinedload

import logging

logger = logging.getLogger(__name__)


user_languages = Table('user_languages', Base.metadata,
    Column('profile_pk', Integer, ForeignKey('user_profile.pk')),
    Column('language_pk', Integer, ForeignKey(Language.pk))
)

user_skills = Table('user_skills', Base.metadata,
    Column('profile_pk', Integer, ForeignKey('user_profile.pk')),
    Column('skill_tag_pk', Integer, ForeignKey('skill_tag.pk'))
)

class SkillTag(Base, TranslatableMixin):
    __translatables__ = ["name"]
    name = Column(UnicodeText, nullable=False, unique=True)


class UserProfile(Base, TranslatableMixin, JsonSerializableMixin):
    __translatables__ = [
        'description', 'city', 'state'
    ]

    user_pk = Column(Integer, ForeignKey('user.pk'))
    description = Column(UnicodeText, nullable=True)
    one_liner  = Column(Unicode(140), nullable=False)
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


@perflog()
def get_user_by_username(session, username, with_profile=True,
        from_cache=True):

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

def get_users(request, page=0, limit=50):
    """ This will get the users limited by `page` and `limit`.  It will
    return a dict of the total users and the limited paged results.

    For example:

        {
            'count': 1,
            'users': [ ... ] 
        }
    """

    if request.search_settings['enabled']: 
        results = get_users_from_es(request.es, page, limit)
        return results
    else:
        users = get_users_from_db(request.db_session, page, limit)
        count = get_user_count_from_db(request.db_session)
        serialized_users = [u.__json__(request) for u in users] 

        return {
            'count': count,
            'users': [u.__json__(request) for u in users]
        }
    

@perflog()
def get_user_count_from_db(session):
    query = session.query(func.count(User.pk))

    results = query.one()

    return results[0]

@perflog()
def get_users_from_db(session, page, limit, with_profile=True):
    """ This queries the database for the user and his profile,
    it will cache the query to redis if possible
    """

    query = session.query(User)
    query = query.options(joinedload('profile'))
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
def get_users_from_es(es, page, limit):
    query = {
        'from': page,
        'size': limit
    }

    results = es.search(query, index=USER_INDEX)
    count = results['hits']['total']
    users = []

    for hit in results['hits']['hits']: 
        users.append(hit['_source'])

    return {
        'count': count,
        'users': users
    }
{'_shards': {'failed': 0, 'successful': 5, 'total': 5},
 'hits': {'hits': [{'_id': '1',
                    '_index': 'users',
                    '_score': 1.0,
                    '_source': {'activation_id': None,
                                'date_created': '2013-07-08T00:39:27.958382',
                                'date_modified': None,
                                'email': 'sontek@gmail.com',
                                'last_login_date': '2013-07-07T20:39:27.958382',
                                'pk': 1,
                                'profile': {'blog_rss': None,
                                            'city': None,
                                            'country_pk': None,
                                            'date_created': '2013-07-08T00:39:27.958382',
                                            'date_modified': None,
                                            'description': None,
                                            'first_name': 'John',
                                            'github_handle': None,
                                            'last_name': 'Anderson',
                                            'one_liner': "I'm awesome",
                                            'pk': 1,
                                            'postal': None,
                                            'state': None,
                                            'timezone_pk': None,
                                            'twitter_handle': None,
                                            'user_pk': 1},
                                'registered_date': '2013-07-07T20:39:27.958382',
                                'security_code': 'e875c3f7f0e2',
                                'status': None,
                                'username': 'sontek'},
                    '_type': 'user'}],
          'max_score': 1.0,
          'total': 1},
 'timed_out': False,
 'took': 2}


@perflog()
def index_users(request, users):
    for user in users:
        request.es.index(
            USER_INDEX
            , 'user'
            , user.__json__(request)
            , id=user.pk
        )
