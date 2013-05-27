from horus.models import GroupMixin
from horus.models import UserMixin
from horus.models import UserGroupMixin
from horus.models import ActivationMixin
from sqlalchemy.ext.declarative import declared_attr

from notaliens.core.models import Base

class NullPkMixin(Base):
    """ Horus is now going to default to 'id' as the primary key
    because its more common in open source projects, but I prefer keeping
    usin using pk. 

    This class overrides the horus id to use pk
    """
    __abstract__ = True
    _idAttribute = 'pk'
#
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


class User(NullPkMixin, UserMixin):
    pass

def get_user_by_username(session, username):
    return session.query(User).filter(User.username == username).one()
