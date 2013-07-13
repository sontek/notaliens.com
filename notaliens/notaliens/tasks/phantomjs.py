import logging
from subprocess import call

logger = logging.getLogger(__name__)

def take_screenshot(data):
    folder = data['folder']
    pjs = data['pjs']
    script = data['script']
    url = data['url']
    pk = data['pk']

    logger.info("Calling %s with %s, %s, %s"
                % (pjs, script, url, '%s/site_%s.png' % (folder, pk)))
    call([pjs, script, url, '%s/site_%s.png' % (folder, pk)])
