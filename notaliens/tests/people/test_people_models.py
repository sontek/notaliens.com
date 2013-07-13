import unittest
import mock


class TestUserProfile(unittest.TestCase):
    def test_display_name(self):
        from notaliens.people.models import UserProfile
        from notaliens.identity.models import User

        user = User(username='sontek')
        profile = UserProfile(user=user)

        assert profile.display_name == 'sontek'

        profile.first_name = 'John'

        assert profile.display_name == 'John'

        profile.last_name = 'Anderson'

        assert profile.display_name == 'John Anderson'

    def test_location(self):
        from notaliens.people.models import UserProfile
        from notaliens.core.models.meta import Country

        profile = UserProfile()

        assert profile.location == ""

        profile.city = "Sometown"

        assert profile.location == "Sometown"

        profile.state = "California"

        assert profile.location == "Sometown, California"

        country = Country(alpha2="US")
        profile.country = country

        assert profile.location == "Sometown, California, US"

    def test_json(self):
        from notaliens.people.models import UserProfile

        profile = UserProfile(latitude=1, longitude=2)

        json = profile.__json__(None)

        assert json['location'] == {
            'lat': 1,
            'lon': 2
        }

class TestUserProfileModels(unittest.TestCase):
    def test_get_user_by_username(self):
        from notaliens.identity.models import User
        from notaliens.people.models import get_user_by_username

        options = mock.Mock()

        query2 = mock.Mock()
        options2 = mock.Mock()
        query2.options = options2

        query3 = mock.Mock()
        options3 = mock.Mock()
        query3.options = options3

        options.return_value = query2
        options2.return_value = query3

        query = mock.Mock()
        query.return_value = query
        query.options = options

        filter_ = mock.Mock()
        filter_.return_value = query

        query.filter = filter_

        session = mock.Mock()
        session.query = query


        with mock.patch('notaliens.people.models.joinedload') as joinedload:
            with mock.patch('notaliens.people.models.FromCache') as FromCache:  # nopep8
                with mock.patch('notaliens.people.models.RelationshipCache') as RelationshipCache:  # nopep8
                    FromCache.return_value = 'foo'
                    RelationshipCache.return_value = 'bar'

                    get_user_by_username(session, 'sontek')

                    query.assert_called_with(User)
                    joinedload.assert_called_with('profile')

                    options.assert_called_with(joinedload('profile'))
                    options2.assert_called_with('foo')

                    options3.assert_called_with('bar')


        query.one.assert_called()

