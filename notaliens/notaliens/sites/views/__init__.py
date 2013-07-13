from pyramid.view import view_config

from notaliens.sites.models import get_site_by_pk
from notaliens.sites.models import get_sites
from notaliens.sites.models import Site
from notaliens.tasks.sites import CaptureScreenshot

import math

@view_config(
    route_name='sites_index',
    renderer='notaliens:sites/templates/index.mako'
)
@view_config(
    route_name='sites_index_paged',
    renderer='notaliens:sites/templates/index.mako'
)
def sites_index(request):
    max_rows = 10
    page = 0
    search_text = None

    if request.method == 'GET':
        page = int(request.matchdict.get('page', page))
    elif request.method == 'POST':
        search_text = request.POST['search'].strip()

    data = get_sites(
        request,
        page=page,
        limit=max_rows,
        search_text=search_text
    )

    data['pages'] = int(math.ceil(data['count'] / max_rows))
    data['current_page'] = page

    if search_text:
        data['search_text'] = search_text

    return {
        'data': data
    }

@view_config(
    route_name='sites_details',
    renderer='notaliens:sites/templates/details.mako'
)
def sites_details_view(request):
    site = get_site_by_pk(
        request.db_session,
        request.matchdict['site_pk']
    )

    return {
        'site': site
    }

@view_config(
    route_name='sites_new',
    renderer='notaliens:sites/templates/new.mako'
)
def sites_new_view(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        description = request.POST.get('description')
        title = request.POST.get('title')

        site = Site(
            url=url,
            description=description,
            title=title,
        )
        request.db_session.add(site)
        request.db_session.flush()
        request.db_session.commit()

        CaptureScreenshot.enqueue(request, site)
    return {}
