import gzip
import logging
import os
import requests
import sys

from cStringIO import StringIO
from pyramid.paster import get_appsettings

logging.basicConfig()
log = logging.getLogger(__name__)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def update(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)

    config_uri = argv[1]
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
