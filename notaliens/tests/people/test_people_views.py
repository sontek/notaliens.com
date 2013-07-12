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
