from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime

import sqlalchemy as sa
import re

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from notaliens.cache.sa import query_callable
from notaliens.cache import regions

DBSession = scoped_session(
    sessionmaker(query_cls=query_callable(regions))
)

class UTCNow(expression.FunctionElement):
    type = sa.DateTime()

@compiles(UTCNow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"

class BaseModel(object):
    """Base class which auto-generates tablename, and surrogate
    primary key column.
    """
    __table_args__ = {
        'mysql_engine': 'InnoDB'
        , 'mysql_charset': 'utf8'
    }

    @declared_attr
    def pk(self):
        # We use pk instead of id because id is a python builtin
        return sa.Column(sa.Integer, primary_key=True)

    _traversal_lookup_key = 'pk'

    @declared_attr
    def __tablename__(cls):
        """Convert CamelCase class name to underscores_between_words 
        table name."""
        name = cls.__name__.replace('Mixin', '')

        return (
            name[0].lower() + 
            re.sub(r'([A-Z])', lambda m:"_" + m.group(0).lower(), name[1:])
        )

    @declared_attr
    def date_created(self):
        return sa.Column(sa.DateTime, server_default=UTCNow())

    @declared_attr
    def date_modified(self):
        return sa.Column(sa.DateTime, onupdate=datetime.utcnow)

Base = declarative_base(cls=BaseModel)
