import unittest
import mock

from pyramid.testing import DummyRequest


class TestPeopleViews(unittest.TestCase):
    def test_people_index_base_get(self):
        from notaliens.people.views import people_index

        request = DummyRequest()
        request.method = 'GET'

        request.search_settings = {
            'enabled': True
        }

        with mock.patch('notaliens.people.views.get_users') as get_users:
            get_users.return_value = {
                'count': 0
            }

            response = people_index(request)

            assert response['data']['count'] == 0
            assert response['data']['current_page'] == 0

    def test_people_index_base_post(self):
        from notaliens.people.views import people_index

        request = DummyRequest()
        request.method = 'POST'

        request.POST = {
        }

        request.search_settings = {
            'enabled': True
        }

        with mock.patch('notaliens.people.views.get_users') as get_users:
            get_users.return_value = {
                'count': 0
            }

            response = people_index(request)

            assert response['data']['count'] == 0
            assert response['data']['current_page'] == 0

    def test_people_profile_view(self):
        from notaliens.people.views import people_profile_view

        request = DummyRequest()
        request.method = 'GET'
        request.db_session = mock.Mock()
        request.matchdict = mock.MagicMock()

        request.search_settings = {
            'enabled': True
        }

        user = mock.Mock()
        region = mock.Mock()
        users = mock.MagicMock()

        with mock.patch('notaliens.people.views.get_user_by_username') as get_user_by_username:  # nopep8
            with mock.patch('notaliens.people.views.get_region_by_postal') as get_region_by_postal:  # nopep8
                with mock.patch('notaliens.people.views.get_users') as get_users:  # nopep8
                    get_user_by_username.return_value = user
                    get_region_by_postal.return_value = region
                    get_users.return_value = users

                    response = people_profile_view(request)

                    assert response['data']['user'] == user
