from sqlalchemy import Column
from sqlalchemy.types import Unicode
from sqlalchemy.types import Integer

from notaliens.core.models import Base
from notaliens.core.models.translation import TranslatableMixin

class Country(Base, TranslatableMixin):
    __translatables__ = ['name', 'official_name']
    
    name = Column(Unicode(128), nullable=False)
    official_name = Column(Unicode(128), nullable=True)
    alpha2 = Column(Unicode(128), nullable=True)
    alpha3 = Column(Unicode(128), nullable=True)
    numeric = Column(Integer, nullable=True)


class Currency(Base, TranslatableMixin):
    __translatables__ = ['name', 'letter']
    name = Column(Unicode(128), nullable=False)
    letter = Column(Unicode(128), nullable=False, unique=True)


class Language(Base, TranslatableMixin):
    __translatables__ = ['name']
    name = Column(Unicode(128), nullable=False)
    alpha3_bib = Column(Unicode(128), nullable=False)
    alpha3_term = Column(Unicode(128), nullable=False)
    alpha2 = Column(Unicode(128), nullable=False)

    def __json__(self, request):
        return {'pk': self.pk, 'name': self.name.encode('utf-8')}

class Timezone(Base, TranslatableMixin):
    __translatables__ = ['name']
    name = Column(Unicode(128), nullable=False)
