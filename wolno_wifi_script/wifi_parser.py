import bs4 as bs
import urllib3
import re
import os
import datetime as d
import pytz
import sqlalchemy
import logging
from itertools import chain
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, String, MetaData, Integer, DateTime, Identity, BigInteger
from ap_zones import ap_zones

"""
CZ:

struktura souborů:
Jmeno_AP
Uptime
Typ_AP
Site_5G:
A
B
C
Site_2.4G:
A
B
C
Pocet_lidi_5G:
sit_A
sit_B
sit_C
Pocet_lidi_2.4G:
sit_A
sit_B
sit_C
Timestamp data z controlleru
Timestamp vytvoreni souboru pro dane ap


EN:

API response structure:
AP_Name (Hostname)
AP_Uptime 
AP_Model
Networks_5G: (str, const)
A
B
C
Networks_2.4G: (str, const)
A
B
C
Pocet_lidi_5G: (str, const)
network_A
network_B
network_C
Pocet_lidi_2.4G: (str, const)
network_A
network_B
network_C
data z controlleru (str, const)
vytvoreni souboru pro dane ap creating: (str, const) timestamp (datetime)

"""


def main():
    counter_ap = 0
    zones = []
    wifi_zones = {}

    http = urllib3.PoolManager(num_pools=1)
    # we make initial request to main page
    response = http.request('GET', 'http://192.168.80.14/apcka2')
    html = response.data.decode('utf8')
    soup = bs.BeautifulSoup(html, 'html.parser')
    # when we getting names of all zones
    for link in soup.find_all('a'):
        if (('pef' in link.get('href')) or ('cems' in link.get('href'))) and ('out' not in link.get(
                'href')):  # Checking if AP's whitch we need is in building PEF (pef, cems) and adding to list of names of APs
            zones.append(link.get('href'))
    # when we make requests using name of zones to get data for each zone
    for name in zones:
        if name:
            counter_ap += 1
        response = http.request('GET', f'http://192.168.80.14/apcka2/{name}')
        html = response.data.decode('utf8')
        networks_counts = list(chain(x.split('\n')[1:-1] for x in html.split(':')[3:7]))
        g2, g5 = tuple(dict(zip(networks_counts[x], networks_counts[y])) for x, y in [
            (1, 3),
            (0, 2),
        ])

        wifi_zones[name] = {'2.4G': g2, '5G': g5}

    # print(f'TOTAL AP\'s {counter_ap}')

    DB_HOST, DB_NAME, DB_USER, DB_PASSWORD = tuple(
        os.environ.get(x) for x in ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD'])

    db_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}'

    db = create_engine(db_string)

    meta = MetaData(db)
    # our table template
    wifi_data = Table('wifi_data_test', meta,
                      Column('id', BigInteger, Identity(), primary_key=True),
                      Column('ssid', String),
                      Column('eduroam_5ghz', Integer),
                      Column('czu_guest_5ghz', Integer),
                      Column('czu_staff_5ghz', Integer),
                      Column('pef_repro_5ghz', Integer),

                      Column('eduroam_2_4ghz', Integer),
                      Column('czu_guest_2_4ghz', Integer),
                      Column('czu_staff_2_4ghz', Integer),
                      Column('pef_repro_2_4ghz', Integer),

                      Column('total_networks', Integer),

                      Column('timemark', DateTime(timezone=True)))

    wifi_users = Table('wifi_users_test', meta,
                       Column('id', BigInteger, Identity(), primary_key=True),
                       Column('connUsers', Integer),
                       Column('timemark', DateTime(timezone=True)),
                       Column('sectorId', Integer))

    with db.connect() as conn:
        # creating table
        wifi_data.create(checkfirst=True)
        # creating "users" table
        wifi_users.create(checkfirst=True)
        # get actual date and time
        actual_date_time_zone = (
            (pytz.utc.localize(d.datetime.utcnow())).astimezone(pytz.timezone("Europe/Prague"))).strftime(
            '%Y-%m-%d %H:%M:%S%z')
        # counting and sorting data and then put data into table
        for zone_name, zone_data in wifi_zones.items():
            try:
                # print(zone_name, zone_data)
                total_users = sum(
                    int(count)
                    for _, by_network in zone_data.items()
                    for _, by_band in by_network.items()
                    for count in by_band if count.isdigit()
                )
                # print(total_users)
            except Exception as exc:
                logging.exception(f'{zone_name}, {exc}\n\n')
            try:
                insert_statement = wifi_data.insert().values(ssid=zone_name,
                                                             eduroam_5ghz=zone_data['5G'].get('eduroam'),
                                                             czu_guest_5ghz=zone_data['5G'].get('CZU-guest'),
                                                             czu_staff_5ghz=zone_data['5G'].get('CZU-staff'),
                                                             pef_repro_5ghz=zone_data['5G'].get('PEF-repro'),
                                                             eduroam_2_4ghz=zone_data['2.4G'].get('eduroam'),
                                                             czu_guest_2_4ghz=zone_data['2.4G'].get('CZU-guest'),
                                                             czu_staff_2_4ghz=zone_data['2.4G'].get('CZU-staff'),
                                                             pef_repro_2_4ghz=zone_data['2.4G'].get('PEF-repro'),
                                                             total_networks=total_users,
                                                             timemark=actual_date_time_zone)
            except Exception as exc:
                logging.exception(f'{zone_name}, {exc}\n\n')
            conn.execute(insert_statement)

            # take data for each ap and sort it to zones
            for ap in ap_zones:
                if zone_name in ap:
                    ap[zone_name] += total_users
        # summ data and put it in DB
        for index, ap in enumerate(ap_zones):
            sum_of_users_in_zone = sum(ap.values())
            insert_statement = wifi_users.insert().values(
                connUsers=sum_of_users_in_zone,
                timemark=actual_date_time_zone,
                sectorId=index + 1
            )
            conn.execute(insert_statement)

    print('Done')


if __name__ == '__main__':
    logging.basicConfig(filename='test_errors.log', level=logging.INFO)
    main()