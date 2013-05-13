from horus.models import GroupMixin
from horus.models import UserMixin
from horus.models import UserGroupMixin
from horus.models import ActivationMixin

from notaliens.core.models import Base


class Activation(ActivationMixin, Base):
    pass


class Group(GroupMixin, Base):
    pass


class UserGroup(UserGroupMixin, Base):
    pass


class User(UserMixin, Base):
    pass

