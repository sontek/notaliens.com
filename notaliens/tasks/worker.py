import os
import sys

from pyres.worker import Worker
from pyres import (
    setup_logging,
)

from pyramid.paster import get_appsettings

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def main(config_file):
    """
    Launches a pyres worker using the host and queues provided
    by the config keys `pyres.host` and `pyres.queues`
    """
    settings = get_appsettings(config_file)

    host = settings['pyres.host']
    queues = settings['pyres.queues'].strip().split(',')

    setup_logging(procname="notaliens.tasks.worker", log_level="INFO")
    Worker.run(queues, server=host)

if __name__ == '__main__':
    main()

