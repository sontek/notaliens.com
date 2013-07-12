from pyramid.view import view_config
from pyramid.settings import asbool
from notaliens.people.models import get_user_by_username
from notaliens.people.models import get_users
from notaliens.core.models.meta import get_region_by_postal

import math


@view_config(
    route_name='people_index',
    renderer='notaliens:people/templates/index.mako'
)
@view_config(
    route_name='people_index_paged',
    renderer='notaliens:people/templates/index.mako'
)
def people_index(request):
    max_rows = 10
    page = 0
    search_text = None
    distance_settings = None
    postal_code = None
    distance = None
    available_for_work = None

    if request.method == 'GET':
        page = int(request.matchdict.get('page', page))
    elif request.method == 'POST':
        search_text = request.POST.get('search', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        distance = request.POST.get('distance', '').strip()

        if distance:
            distance = int(distance)

        if 'available_for_work' in request.POST:
            available_for_work = request.POST.get('available_for_work', None)

            if available_for_work:
                available_for_work = asbool(available_for_work)

        if postal_code and distance:
            region = get_region_by_postal(request.db_session, postal_code)

            distance_settings = {
                'distance': distance,
                'lat': region.latitude,
                'lon': region.longitude
            }


    data = get_users(
        request,
        page=page,
        limit=max_rows,
        search_text=search_text,
        distance_settings=distance_settings,
        available_for_work=available_for_work
    )

    data['pages'] = int(math.ceil(data['count'] / max_rows))
    data['current_page'] = page

    if search_text:
        data['search_text'] = search_text

    if postal_code:
        data['postal_code'] = postal_code
        data['distance'] = distance

    if available_for_work is not None:
        data['available_for_work'] = available_for_work

    return {
        'data': data
    }


@view_config(
    route_name='people_profile',
    renderer='notaliens:people/templates/profile.mako'
)
def people_profile_view(request):
    user = get_user_by_username(
        request.db_session,
        request.matchdict['username']
    )

    region = get_region_by_postal(request.db_session, user.profile.postal)

    data = {}

    data['near_by'] = [u for u in get_users(
        request,
        distance_settings={
            'distance': 50,
            'lat': region.latitude,
            'lon': region.longitude
        },
    )['users'] if u['pk'] != user.pk][:5]

    data['user'] = user

    return {
        'data': data
    }
