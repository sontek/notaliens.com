from horus.resources import RootFactory
from notaliens.sites.models import get_site_by_pk


class SiteFactory(RootFactory):
    def __init__(self, request):
        self.request = request

    def __getitem__(self, pk):
        site = get_site_by_pk(self.request.db_session, pk)

        if site:
            site.__parent__ = self
            site.__name__ = pk

        return site
