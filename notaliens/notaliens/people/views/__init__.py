from pyramid.view import view_config
from notaliens.people.models import get_user_by_username
from notaliens.people.models import get_all_users

@view_config(
    route_name='people_index'
    , renderer='notaliens:people/templates/index.mako'
)
def people_index(request):
    return {
        'users': get_all_users(request.db_session)
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
