import zipfile
import logging
import os
import requests
import sys
import csv

from os import listdir

from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker


from notaliens.core.models.meta import GeoRegion
from notaliens.people.models import UserProfile
from notaliens.core.models.meta import Country

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
    source = settings['geoip.city.csv_source']
    destination = settings['geoip.city.csv_destination']

    engine = engine_from_config(settings, 'sqlalchemy.')
    db_session = scoped_session(sessionmaker())
    db_session.configure(bind=engine)

    if source.startswith('http://'):
        log.info("Downloading %s...", source)
        response = requests.get(source)
        log.info("Downloading done.")

        compressed = zipfile.ZipFile(StringIO(response.content))
    else:
        log.info("Opening %s...", source)
        compressed = zipfile.ZipFile(source)

    log.info("Writing to %s...", destination)
    compressed.extractall(path=destination)
    log.info("Writing done.")

    source_dir = os.path.join(destination, listdir(destination)[0])
    final_path = os.path.join(source_dir, 'GeoLiteCity-Location.csv')

    log.info("Dropping the GeoRegion table")
    GeoRegion.__table__.drop(engine)
    log.info("Creating the GeoRegion table")
    GeoRegion.__table__.create(engine)

    with open(final_path, 'r', newline='', encoding='latin1') as f:
        country = 1
        region = 2
        city = 3
        postal_code = 4
        latitude = 5
        longitude = 6
        metro_code = 7
        area_code = 8

        reader = csv.reader(f, delimiter=',')

        rows = list(reader)
        total_rows = len(rows)

        postals = {}

        for count, (
            locid, country, region, city, postal_code, latitude, longitude,
                metro_code, area_code
        ) in enumerate(rows[2:]):

            ip = GeoRegion(
                country=country,
                region=region,
                city=city,
                postal_code=postal_code,
                latitude=latitude,
                longitude=longitude,
                metro_code=metro_code,
                area_code=area_code
            )

            postals[postal_code] = ip

            db_session.add(ip)

            if count % 5000 == 0:
                log.info('Read %s of %s' % (count, total_rows))

        log.info('Finished, pushing to the database')

        db_session.flush()

        log.info('Finished, pushing to the database')

        log.info('Updating current users lat/long in DB')

        users = db_session.query(UserProfile).all()

        countries_dict = {}
        countries = db_session.query(Country).all()

        for country in countries:
            countries_dict[country.alpha2] = country

        for user in users:
            postal_data = postals[user.postal]

            user.latitude = postal_data.latitude
            user.longitude = postal_data.longitude
            user.city = postal_data.city
            user.state = postal_data.region
            user.country = countries_dict[postal_data.country]

            db_session.add(user)

        db_session.commit()

        log.info('Done!')
