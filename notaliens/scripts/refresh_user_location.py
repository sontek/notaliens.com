import logging
import os
import sys

from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from notaliens.people.models import refresh_users_location

from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging

log = logging.getLogger(__name__)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def update(config_file):
#    if len(argv) != 2:
#        usage(argv)

    setup_logging(config_file)
    settings = get_appsettings(config_file)

    engine = engine_from_config(settings, 'sqlalchemy.')
    db_session = scoped_session(sessionmaker())
    db_session.configure(bind=engine)

    log.info('Updating current users lat/long in DB')

    refresh_users_location(db_session)

    db_session.commit()

    log.info('Done!')
