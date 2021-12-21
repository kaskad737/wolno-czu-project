import bs4 as bs
import urllib3
import re
import os
import datetime as d
import pytz
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, String, MetaData, Integer, DateTime, Identity, BigInteger
from ap_zones import ap_zones

"""


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
        if (('pef' in link.get('href')) or ('cems' in link.get('href'))) and ('out' not in link.get('href')): # Checking if AP's whitch we need is in building PEF (pef, cems) and adding to list of names of APs
            zones.append(link.get('href'))
    # when we make requests using name of zones to get data for each zone
    for name in zones:
        number_of_users_in_each_network = [] # list for collecting number of users for each type of network
        if name:
            counter_ap += 1
        response = http.request('GET', f'http://192.168.80.14/apcka2/{name}')
        html = response.data.decode('utf8')
        for index, line in enumerate(html.split('\n')):
            if line.isdigit(): # check if in list only digit element
                if index != 2: # exclude type of AP number
                    number_of_users_in_each_network.append(line)
        wifi_zones[name] = number_of_users_in_each_network
    # print(f'TOTAL AP\'s {counter_ap}')


    DB_HOST, DB_NAME, DB_USER, DB_PASSWORD = tuple(
        os.environ.get(x) for x in ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD'])

    db_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}'

    db = create_engine(db_string)

    meta = MetaData(db)
    # our table template
    wifi_data = Table('wifi_data', meta,
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

    wifi_users = Table('wifi_users', meta,
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
        actual_date_time_zone = ((pytz.utc.localize(d.datetime.utcnow())).astimezone(pytz.timezone("Europe/Prague"))).strftime('%Y-%m-%d %H:%M:%S%z')
        # counting and sorting data and then put data into table
        for zone, networks in wifi_zones.items():
            networks = list(map(int, networks))
            total_users = sum(networks)
            if zone == 'pef-0-es12':
                insert_statement = wifi_data.insert().values(ssid=zone, eduroam_5ghz=networks[0],
                                                                czu_guest_5ghz=networks[1],
                                                                czu_staff_5ghz=networks[2],
                                                                pef_repro_5ghz=networks[3],
                                                                eduroam_2_4ghz=networks[4],
                                                                czu_guest_2_4ghz=networks[5],
                                                                czu_staff_2_4ghz=networks[6],
                                                                pef_repro_2_4ghz=networks[7],
                                                                total_networks=total_users,
                                                                timemark=actual_date_time_zone)
            elif zone == 'cems1-3-stoly-vytah-ap515-pef':
                insert_statement = wifi_data.insert().values(ssid=zone, 
                                                                timemark=actual_date_time_zone)
            else:
                insert_statement = wifi_data.insert().values(ssid=zone, eduroam_5ghz=networks[0],
                                                                czu_guest_5ghz=networks[1],
                                                                czu_staff_5ghz=networks[2],
                                                                eduroam_2_4ghz=networks[3],
                                                                czu_guest_2_4ghz=networks[4],
                                                                czu_staff_2_4ghz=networks[5],
                                                                total_networks=total_users,
                                                                timemark=actual_date_time_zone)
            conn.execute(insert_statement)

            # take data for each ap and sort it to zones
            for ap in ap_zones:
                if zone in ap:
                    ap[zone] += total_users
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

main()
