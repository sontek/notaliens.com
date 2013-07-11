import os
import sys
import pyelasticsearch
import logging

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from sqlalchemy import engine_from_config

from pyramid.paster import (
    bootstrap,
    setup_logging
)

from notaliens.people.models import get_users_from_db
from notaliens.people.search import index_users
from notaliens.people.search import setup_user_index


here = os.path.dirname(__file__)
log = logging.getLogger(__name__)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)

    config_uri = argv[1]
    setup_logging(config_uri)
    env = bootstrap(config_uri)
    settings = env['registry'].settings
    request = env['request']
    engine = engine_from_config(settings, 'sqlalchemy.')
    db_session = scoped_session(sessionmaker())
    db_session.configure(bind=engine)

    if request.search_settings['enabled']:
        setup_user_index(request)

        users = get_users_from_db(db_session, None, None)
        index_users(request, users)
    else:
        log.error("You have elastic search disabled")

if __name__ == '__main__':
    main()
