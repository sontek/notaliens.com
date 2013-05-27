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

user_languages = Table('user_languages', Base.metadata,
    Column('profile_pk', Integer, ForeignKey('user_profile.pk')),
    Column('language_pk', Integer, ForeignKey(Language.pk))
)


class UserProfile(Base, TranslatableMixin):
    __translatables__ = [
        "description", "city", "state"
    ]

    user_pk = Column(Integer, ForeignKey(User.pk))
    description = Column(UnicodeText, nullable=True)
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

    def get_display_name(self, request):
        if request.user:
            return self.user.display_name
        else:
            if self.user.first_name and self.user.last_name:
                return '%s %s' % (
                    self.user.first_name,
                    self.user.last_name[:1]
                )
            elif self.user.first_name and not self.user.last_name:
                return self.user.first_name
            else:
                return self.user.username
