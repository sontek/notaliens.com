import logging
from subprocess import call

logger = logging.getLogger(__name__)

def take_screenshot(request, url):
    pjs = request.registry['phantomjs_path']
    script = request.registry['phantomjs_script']
    logger.info("Calling %s with %s, %s, %s" % (pjs, script, url, '/tmp/foo.png'))
    call([pjs, script, url, '/tmp/foo.png'])
