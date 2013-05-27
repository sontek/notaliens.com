from notaliens.core.models import Base
from notaliens.core.models.translation import TranslatableMixin
from notaliens.core.models.meta import Country
from notaliens.core.models.meta import Language
from notaliens.core.models.meta import Timezone
from notaliens.identity.models import User

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import UnicodeText
from sqlalchemy.types import Unicode
from sqlalchemy.types import Integer
from sqlalchemy import Table
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref

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


class UserProfile(Base, TranslatableMixin):
    __translatables__ = [
        "description", "city", "state"
    ]

    user_pk = Column(Integer, ForeignKey(User.pk))
    user = relationship(User, backref=backref('profile', uselist=False))
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
