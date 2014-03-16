import pygeoip


def get_geoip_info(request):
    """
    Return a dictionary containing the GeoIP information based on
    `request.ip_address`. The dictionary might be empty if no information about
    the IP address was found in the GeoIP database.

    """
    geoip = request.registry['geoip']
    geoip_info = geoip.record_by_addr(request.ip_address)
    return geoip_info


def get_ip_address(request):
    """
    Return the IP address of the caller. It will either be
    `request.headers['X-Forwarded-For']` if present, otherwise
    environ['REMOTE_ADDR'].

    """
    remote_address = request.environ.get('REMOTE_ADDR')
    ip_address = request.headers.get('X-Forwarded-For', remote_address)
    return ip_address


def includeme(config):
    """
    Provides:

    * `request.ip_address`: IP address of the caller.
    * `request.geoip_info`: A GeoIP dictionary.
    * `request.registry['geoip']`: the GeoIP database.

    """
    path_to_geoip_db = config.registry.settings["geoip.city.destination"]
    config.registry['geoip'] = pygeoip.GeoIP(path_to_geoip_db)
    config.add_request_method(get_ip_address, 'ip_address', reify=True)
    config.add_request_method(get_geoip_info, 'geoip_info', reify=True)
