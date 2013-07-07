from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

import sqlalchemy as sa

from datetime import datetime
from datetime import date
from datetime import time

import re

from notaliens.cache.sa import query_callable
from notaliens.cache import regions
from six import text_type

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

class JsonSerializableMixin(object):
    """
    Converts all the properties of the object into a dict for use in json.
    You can define the following as your class properties.

    _json_eager_load :
        list of which child classes need to be eagerly loaded. This applies
        to one-to-many relationships defined in SQLAlchemy classes.

    _base_blacklist :
        top level blacklist list of which properties not to include in JSON

    _json_blacklist :
        blacklist list of which properties not to include in JSON
    """

    _base_blacklist = ['password', '_json_eager_load', '_request',
        '_base_blacklist', '_json_blacklist'
    ]


    def __json__(self, request):
        """
        Main JSONify method

        :param request: Pyramid Request object
        :type request: <Request>
        :return: dictionary ready to be jsonified
        :rtype: <dict>
        """

        props = {}

        # grab the json_eager_load set, if it exists
        # use set for easy 'in' lookups
        json_eager_load = set(getattr(self, '_json_eager_load', []))

        # now load the property if it exists
        # (does this issue too many SQL statements?)
        for prop in json_eager_load:
            getattr(self, prop, None)

        # we make a copy because the dict will change if the database
        # is updated / flushed
    #    options = self.__dict__.copy()
        properties = list(class_mapper(type(self)).iterate_properties)

        relationships = [
            p.key for p in properties if type(p) is RelationshipProperty
        ]

        # attrs is the attributes that we serialize to json
        # we store them separately since we have a blacklist
        attrs = []
        all_properties = {}
        for p in properties:
            all_properties[p.key] = p

            if not p.key in relationships:
                attrs.append(p.key)

        # setup the blacklist
        # use set for easy 'in' lookups
        blacklist = set(getattr(self, '_base_blacklist', []))

        # extend the base blacklist with the json blacklist
        blacklist.update(getattr(self, '_json_blacklist', []))

        for key in attrs:
            # skip blacklisted properties
            if key in blacklist:
                continue

            # format and date/datetime/time properties to isoformat
            obj = getattr(self, key)

            if isinstance(obj, (datetime, date, time)):
                props[key] = obj.isoformat()
                continue

            # get the class property value
            attr = getattr(self, key)

            # convert all non integer strings to unicode or if unicode conversion
            # is not possible, convert it to a byte string.
            if attr and not isinstance(attr, (int, float)):
                try:
                    props[key] = text_type(attr)
                except UnicodeDecodeError:
                    props[key] = str(attr)  # .encode('utf-8')
                continue

            props[key] = attr

        for key in relationships:
            # let see if we need to eagerly load it
            # this is for SQLAlchemy foreign key fields that
            # indicate with one-to-many relationships
            many_directions = ["ONETOMANY", "MANYTOMANY"]

            if key in json_eager_load:
                # get the class property value
                attr = getattr(self, key)

                if attr:
                    if all_properties[key].direction.name in many_directions:
                        # jsonify all child objects
                        props[key] = [self.try_to_json(request, x) for x in attr]
                    else:
                        props[key] = self.try_to_json(request, attr)

        return props

    def try_to_json(self, request, attr):
        """
        Try to run __json__ on the given object.
        Raise TypeError is __json__ is missing

        :param request: Pyramid Request object
        :type request: <Request>
        :param obj: Object to JSONify
        :type obj: any object that has __json__ method
        :exception: TypeError
        """

        # check for __json__ method and try to JSONify
        if hasattr(attr, '__json__'):
            return attr.__json__(request)

        # raise error otherwise
        raise TypeError('__json__ method missing on %s' % str(attr))


Base = declarative_base(cls=BaseModel)
