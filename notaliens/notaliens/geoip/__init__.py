import pygeoip


def includeme(config):
    path_to_geoip_db = config.registry.settings["geoip.city.db"]
    config.registry['geoip'] = pygeoip.GeoIP(path_to_geoip_db)
