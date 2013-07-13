from notaliens.core.models import Base

from notaliens.core.models.translation import TranslatableMixin
from notaliens.core.models import JsonSerializableMixin

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.types import UnicodeText
from sqlalchemy.types import Unicode
from sqlalchemy.types import Integer
from sqlalchemy.types import Boolean
from sqlalchemy.types import Float
from sqlalchemy.orm import relationship

from notaliens.core.models.meta import Country

class Job(Base, TranslatableMixin, JsonSerializableMixin):
    __translatables__ = [
        'description', 'city', 'state'
    ]

    user_pk = Column(Integer, ForeignKey('user.pk'))
    active = Column(Boolean, nullable=False, default=True)
    allow_telecommute = Column(Boolean, nullable=False, default=False)
    allow_agencies = Column(Boolean, nullable=False, default=False)
    title = Column(Unicode(140), nullable=False)
    company = Column(Unicode(140), nullable=False)
    url = Column(Unicode(255), nullable=True)
    description = Column(UnicodeText, nullable=False)
    city = Column(Unicode(255), nullable=True)
    state = Column(Unicode(255), nullable=True)
    postal = Column(Unicode(255), nullable=True)
    country_pk = Column(Integer, ForeignKey(Country.pk), nullable=True)
    country = relationship(Country)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    contact_name = Column(Unicode(255), nullable=True)
    contact_email = Column(Unicode(255), nullable=True)
    contact_phone = Column(Unicode(255), nullable=True)
