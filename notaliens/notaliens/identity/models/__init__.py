from horus.models import GroupMixin
from horus.models import UserMixin
from horus.models import UserGroupMixin
from horus.models import ActivationMixin

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from notaliens.core.models import JsonSerializableMixin
from notaliens.core.models import Base


class NullPkMixin(Base):
    """ Horus is now going to default to 'id' as the primary key
    because its more common in open source projects, but I prefer keeping
    usin using pk.

    This class overrides the horus id to use pk
    """
    __abstract__ = True
    _idAttribute = 'pk'

    @declared_attr
    def pk(self):
        return Base.pk

    @declared_attr
    def id(self):
        return None


class Activation(NullPkMixin, ActivationMixin):
    pass


class Group(NullPkMixin, GroupMixin):
    pass


class UserGroup(NullPkMixin, UserGroupMixin):
    pass


class User(NullPkMixin, UserMixin, JsonSerializableMixin):
    _json_blacklist = ['salt', 'password', '_password']
    _json_eager_load = ['profile']
    profile = relationship('UserProfile', uselist=False, backref='user')

    def __json__(self, request):
        """ JSON Serialization, that overrides the default horus __json__
        to also ignore things in _json_blacklist
        """
        results = JsonSerializableMixin.__json__(self, request)

        return results
