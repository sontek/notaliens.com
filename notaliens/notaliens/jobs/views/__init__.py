from pyramid.view import view_config
from notaliens.phantomjs import take_screenshot

@view_config(
    route_name='jobs_index',
    renderer='notaliens:jobs/templates/index.mako'
)
def sites_index(request):
    if request.method == 'POST':
        url = request.POST.get('url')

        take_screenshot(request, url)        
    return {}
