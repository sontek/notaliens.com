from pyramid.view import view_config
from notaliens.people.models import get_user_by_username
from notaliens.people.models import get_users

import math

@view_config(
    route_name='people_index'
    , renderer='notaliens:people/templates/index.mako'
)
@view_config(
    route_name='people_index_paged'
    , renderer='notaliens:people/templates/index.mako'
)
def people_index(request):
    page = int(request.matchdict.get('page', 0))
    max_rows = 10
    data = get_users(request, page=page, limit=max_rows)
    data['pages'] = math.ceil(data['count'] / max_rows)
    data['current_page'] = page

    return {
        'data': data
    }

@view_config(
    route_name='people_profile'
    , renderer='notaliens:people/templates/profile.mako'
)
def people_profile_view(request):
    user = get_user_by_username(
        request.db_session,
        request.matchdict['username']
    )

    return {
        'user': user
    }
