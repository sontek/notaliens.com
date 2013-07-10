import gzip
import logging
import os
import requests
import sys

#py3
try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging

logging.basicConfig()
log = logging.getLogger(__name__)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def update(argv=sys.argv):
    """
    Download the GeoIP database from the URL provided under the config key
    `geoip.city.source` and save it under the path provided by the config key
    `geoip.city.db`.

    """
    if len(argv) != 2:
        usage(argv)

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    source = settings['geoip.city.source']
    output = settings['geoip.city.db']
    log.info("Downloading %s...", source)
    response = requests.get(source)
    log.info("Downloading done.")

    compressed = gzip.GzipFile(fileobj=StringIO(response.content))
    with open(output, "wb") as f:
        log.info("Writting to %s...", output)
        f.write(compressed.read())
        log.info("Writting done.")
