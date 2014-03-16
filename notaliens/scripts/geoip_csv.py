import zipfile
import logging
import os
import requests
import sys
import six
import csv
import math
from threading import Thread
from os import listdir

from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from notaliens.core.models.meta import Country
from notaliens.core.models.meta import GeoRegion
from notaliens.people.models import refresh_users_location

if six.PY3:
    from io import BytesIO as StringIO
else:
    from cStringIO import StringIO

from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging

logging.basicConfig()
log = logging.getLogger(__name__)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def latin1_csv_reader(latin1_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(latin1_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'latin1') for cell in row]

if six.PY3:
    csv_reader = csv.reader
else:
    csv_reader = latin1_csv_reader


def chunks(source, chunk_size):
    """
    Splits a list up into chunks
    """
    return [source[i:i+chunk_size] for i in range(0, len(source), chunk_size)]


def update(argv=sys.argv):
    """
    Download the GeoIP database from the URL provided under the config key
    `geoip.city.source` and save it under the path provided by the config key
    `geoip.city.destination`.

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

    countries = {}

    for country in db_session.query(Country).all():
        countries[country.alpha2] = country

    db_session.commit()

    if six.PY3:
        infile = open(final_path, 'r', newline='', encoding='latin1')
    else:
        infile = open(final_path, 'rb')

    with infile as f:
        reader = csv_reader(f, delimiter=',')

        rows = list(reader)

        chunk_size = 5000
        split_rows = chunks(rows[2:], chunk_size)
        thread_count = 10.0
        row_len = len(split_rows)
        loops = math.ceil(row_len/thread_count)
        current_row = 0

        total = 0

        for i in range(int(loops)):
            threads = []

            for j in range(int(thread_count)):
                if current_row < row_len:
                    rows = split_rows[current_row]
                    t = Thread(
                        target=write_to_db,
                        args=(
                            db_session,
                            rows,
                            countries
                        )
                    )
                    threads.append(t)
                    current_row += 1

            [x.start() for x in threads]

            for x in threads:
                x.join()
                total += int(thread_count) * chunk_size
                logging.info(
                    "Done adding %s locations in DB\n" % total
                )

        log.info('Finished, pushing to the database')


def write_to_db(db_session, rows, countries):
    for count, (
            locid, country_code, region, city, postal_code, latitude,
            longitude, metro_code, area_code
    ) in enumerate(rows):
        if country_code not in countries:
            # Should always be ok, only ones not there are anonymous
            # proxy, and regions like EU
            print("Country Code %s isn't in our DB" % country_code)
            continue
        else:
            country_obj = countries[country_code]

        ip = GeoRegion(
            country_pk=country_obj.pk,
            region=region,
            city=city,
            postal_code=postal_code,
            latitude=latitude,
            longitude=longitude,
            metro_code=metro_code,
            area_code=area_code
        )

        db_session.add(ip)

    db_session.commit()
