from horus.resources import RootFactory
from notaliens.people.models import get_user_by_username


class UserFactory(RootFactory):
    def __init__(self, request):
        self.request = request

    def __getitem__(self, username):
        user = get_user_by_username(self.request.db_session, username)

        if user:
            user.__parent__ = self
            user.__name__ = username

        return user
