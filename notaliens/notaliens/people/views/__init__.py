from pyramid.view import view_config
from pyramid.settings import asbool
from notaliens.people.models import get_user_by_username
from notaliens.people.models import get_users
from notaliens.core.models.meta import get_region_by_postal
from notaliens.core.models.meta import get_all_countries
from notaliens.people.models import refresh_user_location
from notaliens.people.search import index_users

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
    country = None

    if request.method == 'GET':
        page = int(request.matchdict.get('page', page))
    elif request.method == 'POST':
        search_text = request.POST.get('search', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        distance = request.POST.get('distance', '').strip()
        country = int(request.POST.get('country', '1').strip())

        if distance:
            distance = int(distance)

        if 'available_for_work' in request.POST:
            available_for_work = request.POST.get('available_for_work', None)

            if available_for_work:
                available_for_work = asbool(available_for_work)

        if country and postal_code and distance:
            region = get_region_by_postal(
                request.db_session,
                postal_code,
                country
            )

            if region:
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

    if country:
        data['country'] = country

    if available_for_work is not None:
        data['available_for_work'] = available_for_work

    data['countries'] = get_all_countries(request.db_session)

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

    region = get_region_by_postal(
        request.db_session,
        user.profile.postal,
        user.profile.country_pk
    )

    data = {}

    if region:
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


def handle_profile_update(event):
    """ This function is fired off from the horus profile view.
    We have extended the profile to have extra data and we handle that data
    here
    """
    request = event.request
    context = request.context
    values = event.values

    email = values['email']
    first_name = values['first_name']
    last_name = values['last_name']
    one_liner = values['one_liner']
    postal = values['postal']

    #language_ids = values['spoken_languages']
    #timezone = values['timezone']

    context.email = email
    context.profile.first_name = first_name
    context.profile.last_name = last_name
    context.profile.one_liner = one_liner

    if postal != context.profile.postal:
        context.profile.postal = postal
        refresh_user_location(request.db_session, context)

    index_users(request, [context])

    request.db_session.commit()
