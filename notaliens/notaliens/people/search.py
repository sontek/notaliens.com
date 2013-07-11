from notaliens.log import perflog
from notaliens.people import USER_INDEX
from pyelastic.search.exceptions import ElasticHttpNotFoundError

user_mapping = {
    "users": {
        "user": {
            "properties": {
                "date_created": {
                    "type": "date",
                    "format": "dateOptionalTime"
                    },
                "email": {
                    "type": "string"
                    },
                "last_login_date": {
                    "type": "date",
                    "format": "dateOptionalTime"
                    },
                "pk": {
                    "type": "long"
                    },
                "profile": {
                    "properties": {
                        "location": {
                            "type": "geo_point"
                            },
                        "date_created": {
                            "type": "date",
                            "format": "dateOptionalTime"
                            },
                        "date_modified": {
                            "type": "date",
                            "format": "dateOptionalTime"
                            },
                        "first_name": {
                            "type": "string"
                            },
                        "last_name": {
                            "type": "string"
                            },
                        "latitude": {
                            "type": "double"
                            },
                        "longitude": {
                            "type": "double"
                            },
                        "one_liner": {
                            "type": "string"
                            },
                        "pk": {
                            "type": "long"
                            },
                        "postal": {
                            "type": "string"
                            },
                        "user_pk": {
                            "type": "long"
                            }
                        }
                    },
                "registered_date": {
                    "type": "date",
                    "format": "dateOptionalTime"
                },
                "security_code": {
                    "type": "string"
                },
                "username": {
                    "type": "string"
                }
            }
        }
    }
}


@perflog()
def index_users(request, users):
    for user in users:
        request.es.index(
            USER_INDEX,
            'user',
            user.__json__(request),
            id=user.pk
        )


def setup_user_index(request):
    try:
        request.es.delete_index(USER_INDEX)
    except ElasticHttpNotFoundError:
        pass

    request.es.create_index(USER_INDEX)
    request.es.put_mapping(USER_INDEX, 'user', user_mapping)
